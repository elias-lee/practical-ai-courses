"""A minimal tracer: nested spans with duration, tokens and cost, exportable as JSON.

It mirrors the shape of OpenTelemetry / Langfuse traces (trace -> spans -> child spans) so that
moving to a real backend later is a change of library, not of habits.

    tracer = Tracer()
    with tracer.span("sitrep_run", case_id="g01"):
        with tracer.span("llm.call", model="gpt-4o-mini") as s:
            reply = llm(messages)
            s.record_usage(input_tokens=812, output_tokens=240, cost_usd=0.0003)
    print(tracer.tree())
    tracer.export_json("trace.json")
"""
from __future__ import annotations

import json
import time
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Optional, Union

from llm import LLM


@dataclass
class Span:
    name: str
    span_id: str
    parent_id: Optional[str]
    start: float
    end: Optional[float] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    status: str = "ok"
    error: Optional[str] = None

    @property
    def duration_ms(self) -> float:
        return 0.0 if self.end is None else (self.end - self.start) * 1000

    def record_usage(self, input_tokens: int = 0, output_tokens: int = 0, cost_usd: float = 0.0) -> None:
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        self.cost_usd += cost_usd

    def set(self, **attributes: Any) -> None:
        self.attributes.update(attributes)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["duration_ms"] = round(self.duration_ms, 3)
        return d


class Tracer:
    def __init__(self, clock: Callable[[], float] = time.perf_counter):
        self.clock = clock
        self.spans: List[Span] = []
        self._stack: List[Span] = []

    @contextmanager
    def span(self, name: str, **attributes: Any) -> Iterator[Span]:
        parent = self._stack[-1].span_id if self._stack else None
        s = Span(name=name, span_id=uuid.uuid4().hex[:12], parent_id=parent, start=self.clock(),
                 attributes=dict(attributes))
        self.spans.append(s)
        self._stack.append(s)
        try:
            yield s
        except Exception as exc:
            s.status, s.error = "error", f"{type(exc).__name__}: {exc}"
            raise  # tracing records failures; it never swallows them
        finally:
            s.end = self.clock()
            self._stack.pop()

    def children(self, span: Span) -> List[Span]:
        return [s for s in self.spans if s.parent_id == span.span_id]

    def totals(self) -> Dict[str, float]:
        """Token and cost totals. Usage is recorded on leaf spans (the model calls), so summing
        every span does not double-count."""
        return {
            "input_tokens": sum(s.input_tokens for s in self.spans),
            "output_tokens": sum(s.output_tokens for s in self.spans),
            "cost_usd": round(sum(s.cost_usd for s in self.spans), 6),
            "llm_calls": sum(1 for s in self.spans if s.name.startswith("llm")),
            "errors": sum(1 for s in self.spans if s.status == "error"),
        }

    def tree(self) -> str:
        lines: List[str] = []

        def walk(span: Span, depth: int) -> None:
            usage = f" tokens={span.input_tokens}+{span.output_tokens} ${span.cost_usd:.5f}" if span.input_tokens else ""
            flag = " ERROR" if span.status == "error" else ""
            lines.append(f"{'  ' * depth}{span.name} {span.duration_ms:.0f}ms{usage}{flag}")
            for child in self.children(span):
                walk(child, depth + 1)

        for root in (s for s in self.spans if s.parent_id is None):
            walk(root, 0)
        return "\n".join(lines)

    def to_json(self) -> str:
        return json.dumps({"spans": [s.to_dict() for s in self.spans], "totals": self.totals()},
                          indent=1, ensure_ascii=False)

    def export_json(self, path: Union[str, Path]) -> None:
        Path(path).write_text(self.to_json(), encoding="utf-8")


def estimate_tokens(text: str) -> int:
    """Rough rule of thumb (about 4 characters per token in English). Use the provider's reported
    usage in production; other scripts and languages tokenize differently."""
    return max(1, len(text) // 4)


def traced_llm(llm: LLM, tracer: Tracer, model: str, usd_per_1m_input: float = 0.15,
               usd_per_1m_output: float = 0.60) -> LLM:
    """Wrap an LLM so every call becomes an ``llm.call`` span with tokens and cost.
    Default prices are illustrative placeholders, not any provider's current price list."""

    def call(messages: List[Dict[str, str]]) -> str:
        with tracer.span("llm.call", model=model) as s:
            reply = llm(messages)
            tin = estimate_tokens("".join(m["content"] for m in messages))
            tout = estimate_tokens(reply)
            s.record_usage(tin, tout, tin * usd_per_1m_input / 1e6 + tout * usd_per_1m_output / 1e6)
            return reply

    return call
