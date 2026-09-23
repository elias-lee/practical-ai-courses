"""A small, framework-free tool harness.

Four pieces, each one screen of code:

1. ``@tool``            turns a typed, documented Python function into a JSON-schema tool.
2. ``ToolRegistry``     holds tools, validates arguments and runs them.
3. ``run_tool_loop``    the tool-call loop: ask the model, run the tool it asks for, feed the
                        result (or the error) back, repeat until a final answer or the budget.
4. Guardrails           an allow-list for tool calls and PII redaction for tool results,
                        plus ``with_retry`` / ``with_fallback`` for unreliable models.

The model speaks a tiny JSON protocol (real SDKs use native tool calling; the ideas are the same):

    {"tool": "get_population", "arguments": {"district": "Kessan"}}   -> call a tool
    {"final": "Kessan has an estimated population of ..."}             -> finish
"""
from __future__ import annotations

import inspect
import json
import re
import time
import typing
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

from llm import LLM

# --------------------------------------------------------------------------------------
# 1. @tool: Python function -> JSON schema
# --------------------------------------------------------------------------------------

_JSON_TYPES = {str: "string", int: "integer", float: "number", bool: "boolean", dict: "object"}


class ToolError(Exception):
    """Raised by a tool when it cannot do what was asked. The message goes back to the model,
    so write it for the model: say what was wrong and what to do instead."""


class ToolArgumentError(ToolError):
    """The model's arguments do not match the tool's schema."""


def _json_type(annotation: Any) -> Dict[str, Any]:
    """Map a Python type hint to a JSON-schema fragment."""
    origin = typing.get_origin(annotation)
    args = typing.get_args(annotation)
    if origin is typing.Union:  # Optional[X] is Union[X, None]
        non_none = [a for a in args if a is not type(None)]
        if len(non_none) == 1:
            return _json_type(non_none[0])
    if origin in (list, List):
        item = _json_type(args[0]) if args else {}
        return {"type": "array", "items": item}
    if origin is typing.Literal:
        return {"type": _JSON_TYPES[type(args[0])], "enum": list(args)}
    if annotation in _JSON_TYPES:
        return {"type": _JSON_TYPES[annotation]}
    raise TypeError(f"@tool does not know how to describe type {annotation!r}")


def _parse_docstring(doc: str) -> Tuple[str, Dict[str, str]]:
    """Split a Google-style docstring into (description, {arg: description})."""
    doc = inspect.cleandoc(doc or "")
    if not doc:
        raise ValueError("a tool needs a docstring: the model reads it to decide when to use the tool")
    head, _, args_block = doc.partition("\nArgs:\n")
    arg_docs: Dict[str, str] = {}
    current = None
    for line in args_block.splitlines():
        match = re.match(r"\s{2,}(\w+):\s*(.*)", line)
        if match:
            current = match.group(1)
            arg_docs[current] = match.group(2).strip()
        elif current and line.strip():
            arg_docs[current] += " " + line.strip()
    return " ".join(head.split()), arg_docs


@dataclass
class Tool:
    """A function plus the JSON schema that describes it to the model."""

    name: str
    description: str
    parameters: Dict[str, Any]
    func: Callable[..., Any]

    @property
    def schema(self) -> Dict[str, Any]:
        """The definition sent to the model (the same shape most provider SDKs use)."""
        return {"name": self.name, "description": self.description, "parameters": self.parameters}

    def __call__(self, **kwargs: Any) -> Any:
        return self.func(**kwargs)


def tool(func: Callable[..., Any]) -> Tool:
    """Decorator: build a Tool from a function's name, type hints and docstring."""
    description, arg_docs = _parse_docstring(func.__doc__ or "")
    hints = typing.get_type_hints(func)
    properties: Dict[str, Any] = {}
    required: List[str] = []
    for name, param in inspect.signature(func).parameters.items():
        if name not in hints:
            raise TypeError(f"tool {func.__name__!r}: parameter {name!r} needs a type hint")
        prop = _json_type(hints[name])
        if name in arg_docs:
            prop["description"] = arg_docs[name]
        if param.default is inspect.Parameter.empty:
            required.append(name)
        else:
            prop["default"] = param.default
        properties[name] = prop
    parameters = {
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": False,
    }
    return Tool(name=func.__name__, description=description, parameters=parameters, func=func)


# --------------------------------------------------------------------------------------
# 2. The registry: validate, then run
# --------------------------------------------------------------------------------------

_PY_CHECKS = {
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "array": lambda v: isinstance(v, list),
    "object": lambda v: isinstance(v, dict),
}


class ToolRegistry:
    """The set of tools one harness exposes."""

    def __init__(self, tools: Iterable[Tool] = ()):
        self._tools: Dict[str, Tool] = {}
        for t in tools:
            self.register(t)

    def register(self, t: Tool) -> None:
        if t.name in self._tools:
            raise ValueError(f"duplicate tool name {t.name!r}")
        self._tools[t.name] = t

    @property
    def names(self) -> List[str]:
        return list(self._tools)

    def schemas(self) -> List[Dict[str, Any]]:
        return [t.schema for t in self._tools.values()]

    def validate(self, name: str, arguments: Any) -> Tool:
        """Check a proposed call against the schema; raise errors the model can act on."""
        if name not in self._tools:
            raise ToolArgumentError(
                f"Unknown tool {name!r}. Available tools: {', '.join(self.names)}."
            )
        t = self._tools[name]
        if not isinstance(arguments, dict):
            raise ToolArgumentError(f"'arguments' for {name} must be a JSON object.")
        props = t.parameters["properties"]
        unknown = sorted(set(arguments) - set(props))
        if unknown:
            raise ToolArgumentError(
                f"{name} does not accept {unknown}. Accepted arguments: {sorted(props)}."
            )
        missing = [r for r in t.parameters["required"] if r not in arguments]
        if missing:
            raise ToolArgumentError(f"{name} is missing required argument(s): {missing}.")
        for arg, value in arguments.items():
            if value is None and arg not in t.parameters["required"]:
                continue  # an explicit null for an optional argument means "use the default"
            expected = props[arg]["type"]
            if not _PY_CHECKS[expected](value):
                raise ToolArgumentError(
                    f"{name}: argument {arg!r} must be of type {expected}, got {value!r}."
                )
            if "enum" in props[arg] and value not in props[arg]["enum"]:
                raise ToolArgumentError(
                    f"{name}: argument {arg!r} must be one of {props[arg]['enum']}, got {value!r}."
                )
        return t

    def call(self, name: str, arguments: Dict[str, Any]) -> Any:
        t = self.validate(name, arguments)
        # Drop explicit nulls for optional arguments so the function's own defaults apply.
        kwargs = {k: v for k, v in arguments.items() if v is not None or k in t.parameters["required"]}
        return t(**kwargs)


# --------------------------------------------------------------------------------------
# 3. Guardrails
# --------------------------------------------------------------------------------------

# A guardrail looks at a proposed tool call and returns a reason to block it, or None.
Guardrail = Callable[[str, Dict[str, Any]], Optional[str]]


def allow_list(allowed: Sequence[str]) -> Guardrail:
    """Only the named tools may run: least privilege, enforced in code."""
    allowed_set = set(allowed)

    def check(name: str, arguments: Dict[str, Any]) -> Optional[str]:
        if name not in allowed_set:
            return f"tool {name!r} is not permitted in this deployment"
        return None

    return check


_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_PHONE = re.compile(r"\+\d[\d\s().-]{6,}\d")  # international format only, so dates survive


def redact_pii(text: str) -> str:
    """Mask email addresses and international phone numbers. Deliberately simple: a real
    deployment would use a dedicated PII service (names and ID numbers are much harder)."""
    text = _EMAIL.sub("[EMAIL REDACTED]", text)
    return _PHONE.sub("[PHONE REDACTED]", text)


# --------------------------------------------------------------------------------------
# 4. The tool-call loop
# --------------------------------------------------------------------------------------

PROTOCOL = """You can call tools to answer the user's request.

Reply with exactly ONE JSON object and nothing else:
- To call a tool:   {{"tool": "<tool name>", "arguments": {{...}}}}
- To finish:        {{"final": "<your answer for the user>"}}

After each tool call you will receive the result (or an error) as JSON. If a tool returns an
error, read it and correct your call. Only use figures that appear in tool results.

Available tools (JSON schema):
{schemas}"""


@dataclass
class ToolCallRecord:
    step: int
    tool: str
    arguments: Dict[str, Any]
    ok: bool
    result: str


@dataclass
class LoopResult:
    status: str  # "final" or "budget_exceeded": two different outcomes, never confuse them
    answer: Optional[str]
    steps: int
    messages: List[Dict[str, str]]
    tool_calls: List[ToolCallRecord] = field(default_factory=list)


def _parse_reply(reply: str) -> Dict[str, Any]:
    """Accept a bare JSON object, optionally wrapped in a ```json fence or surrounding prose."""
    text = reply.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object found")
    data = json.loads(text[start : end + 1])
    if not isinstance(data, dict) or not ({"tool", "final"} & set(data)):
        raise ValueError('JSON must contain "tool" or "final"')
    return data


def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + f" ...[truncated {len(text) - limit} chars; narrow your query or page]"


def run_tool_loop(
    llm: LLM,
    tools: ToolRegistry,
    messages: List[Dict[str, str]],
    max_steps: int = 6,
    guardrails: Sequence[Guardrail] = (),
    redact: bool = True,
    max_result_chars: int = 2000,
) -> LoopResult:
    """Run the tool-call loop until the model gives a final answer or the step budget runs out.

    Each model call is one step. Tool errors, bad arguments, blocked calls and malformed replies
    are all fed back to the model as observations; none of them crash the loop.
    """
    system = {"role": "system", "content": PROTOCOL.format(schemas=json.dumps(tools.schemas(), indent=1))}
    convo: List[Dict[str, str]] = [system] + list(messages)
    records: List[ToolCallRecord] = []

    for step in range(1, max_steps + 1):
        reply = llm(convo)
        convo.append({"role": "assistant", "content": reply})

        try:
            data = _parse_reply(reply)
        except ValueError as exc:  # malformed reply: tell the model how to fix it
            convo.append({"role": "user", "content": json.dumps({
                "error": f"Could not parse your reply ({exc}). Reply with one JSON object only."})})
            continue

        if "final" in data:
            return LoopResult("final", str(data["final"]), step, convo, records)

        name, arguments = str(data.get("tool")), data.get("arguments", {})
        blocked = next((r for r in (g(name, arguments) for g in guardrails) if r), None)
        if blocked:
            ok, result = False, f"BLOCKED by policy: {blocked}. Do not retry; use another tool or finish."
        else:
            try:
                ok, result = True, json.dumps(tools.call(name, arguments), ensure_ascii=False)
            except ToolError as exc:
                ok, result = False, f"ERROR: {exc}"
            except Exception as exc:  # an unexpected bug in a tool: report it, don't crash
                ok, result = False, f"ERROR: {name} failed unexpectedly ({type(exc).__name__}: {exc})."

        if redact:
            result = redact_pii(result)
        result = _truncate(result, max_result_chars)
        records.append(ToolCallRecord(step, name, arguments if isinstance(arguments, dict) else {}, ok, result))
        convo.append({"role": "user", "content": json.dumps({"tool": name, "ok": ok, "result": result},
                                                             ensure_ascii=False)})

    return LoopResult("budget_exceeded", None, max_steps, convo, records)


# --------------------------------------------------------------------------------------
# 5. Reliability wrappers
# --------------------------------------------------------------------------------------

TRANSIENT = (TimeoutError, ConnectionError)


def with_retry(
    llm: LLM,
    attempts: int = 3,
    base_delay: float = 0.5,
    retry_on: Tuple[type, ...] = TRANSIENT,
    sleep: Callable[[float], None] = time.sleep,
) -> LLM:
    """Retry transient failures with exponential backoff (0.5 s, 1 s, 2 s ...). Capped: a retry
    loop is also a loop."""

    def call(messages: List[Dict[str, str]]) -> str:
        for attempt in range(attempts):
            try:
                return llm(messages)
            except retry_on:
                if attempt == attempts - 1:
                    raise
                sleep(base_delay * (2 ** attempt))
        raise AssertionError("unreachable")

    return call


def with_fallback(primary: LLM, fallback: LLM, fall_back_on: Tuple[type, ...] = (Exception,)) -> LLM:
    """If the primary model fails (after its own retries), try the fallback model."""

    def call(messages: List[Dict[str, str]]) -> str:
        try:
            return primary(messages)
        except fall_back_on:
            return fallback(messages)

    return call
