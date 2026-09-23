"""Token and cost estimator with a pluggable tokenizer.

A *tokenizer* here is any function ``text -> list of token strings``. The lab ships a
pure-Python approximation (``approx_tokenize``) so the tests need no packages; for real
numbers plug in your model's own tokenizer, e.g. ``tiktoken_tokenizer()``.

    python tokens.py            # compare six widely used languages and estimate a monthly bill

The approximation is deliberately simple and will not match any real tokenizer exactly.
It captures the pattern that matters for budgeting: tokenizers trained mostly on English
text split other scripts into more, shorter pieces, so the same message can cost more.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple

Tokenizer = Callable[[str], List[str]]

# Characters per token for each kind of run (rough, tuned by eye on real tokenizers).
CHARS_PER_TOKEN: Dict[str, int] = {
    "latin": 6,    # English, French, Spanish: common words are usually one token
    "cyrillic": 3,  # Russian
    "arabic": 3,    # Arabic
    "cjk": 1,       # Chinese (and Japanese) characters: roughly one token each
    "digits": 3,    # numbers are split into groups of up to three digits
    "other": 1,     # punctuation and symbols
}

_RUN = re.compile(
    r"(?P<space>\s*)(?:"
    r"(?P<latin>[A-Za-zÀ-ɏ]+)"
    r"|(?P<cyrillic>[Ѐ-ӿ]+)"
    r"|(?P<arabic>[؀-ۿݐ-ݿ]+)"
    r"|(?P<cjk>[぀-ヿ㐀-䶿一-鿿豈-﫿])"
    r"|(?P<digits>[0-9]+)"
    r"|(?P<other>\S))"
)


def approx_tokenize(text: str) -> List[str]:
    """Split text into approximate tokens. Leading spaces stick to the next token, as in
    most real tokenizers, so ``" households"`` is one piece."""
    pieces: List[str] = []
    for match in _RUN.finditer(text):
        kind = next(k for k in CHARS_PER_TOKEN if match.group(k))
        body = match.group(kind)
        size = CHARS_PER_TOKEN[kind]
        chunks = [body[i:i + size] for i in range(0, len(body), size)]
        chunks[0] = match.group("space") + chunks[0]
        pieces.extend(chunks)
    return pieces


def tiktoken_tokenizer(encoding: str = "o200k_base") -> Tokenizer:
    """A real tokenizer used by recent OpenAI models (``pip install tiktoken``).

    Other providers use different tokenizers; for exact counts use the provider's
    token-counting endpoint or the usage figures returned with each response.
    """
    import tiktoken  # lazy: only needed for real counts

    enc = tiktoken.get_encoding(encoding)
    return lambda text: [enc.decode([t]) for t in enc.encode(text)]


def count_tokens(text: str, tokenizer: Tokenizer = approx_tokenize) -> int:
    return len(tokenizer(text))


@dataclass(frozen=True)
class Price:
    """Price in USD per million tokens. Output tokens usually cost several times more."""
    input_per_million: float
    output_per_million: float


# ILLUSTRATIVE tiers only, not quotes. Look up your provider's current price list.
EXAMPLE_PRICES: Dict[str, Price] = {
    "small": Price(input_per_million=0.15, output_per_million=0.60),
    "large": Price(input_per_million=3.00, output_per_million=15.00),
}


@dataclass(frozen=True)
class CostEstimate:
    input_tokens: int
    output_tokens: int
    cost_usd: float

    def times(self, calls: int) -> "CostEstimate":
        """The same call repeated ``calls`` times (e.g. per month)."""
        return CostEstimate(self.input_tokens * calls, self.output_tokens * calls,
                            self.cost_usd * calls)


def estimate_cost(prompt: str, expected_output_tokens: int, price: Price,
                  tokenizer: Tokenizer = approx_tokenize) -> CostEstimate:
    """Estimate the cost of one call: tokens in the prompt plus the tokens you expect back."""
    input_tokens = count_tokens(prompt, tokenizer)
    cost = (input_tokens * price.input_per_million
            + expected_output_tokens * price.output_per_million) / 1_000_000
    return CostEstimate(input_tokens, expected_output_tokens, cost)


# The same (fictional) sentence in six widely used languages.
LANGUAGE_SAMPLE: Dict[str, str] = {
    "English": "Flooding in Aramu district has displaced about 1,200 households. "
               "Clean water is the most urgent need.",
    "French": "Les inondations dans le district d'Aramu ont déplacé environ 1 200 ménages. "
              "L'eau potable est le besoin le plus urgent.",
    "Spanish": "Las inundaciones en el distrito de Aramu han desplazado a unos 1.200 hogares. "
               "El agua potable es la necesidad más urgente.",
    "Russian": "Наводнение в районе Араму вынудило около 1200 домохозяйств покинуть свои дома. "
               "Чистая вода — самая насущная потребность.",
    "Arabic": "أدت الفيضانات في مقاطعة آرامو إلى نزوح نحو 1200 أسرة. "
              "والمياه النظيفة هي الحاجة الأكثر إلحاحاً.",
    "Chinese": "阿拉穆区的洪水已导致约1200户家庭流离失所。清洁饮用水是最紧迫的需求。",
}


def language_table(texts: Dict[str, str],
                   tokenizer: Tokenizer = approx_tokenize,
                   baseline: str = "English") -> List[Tuple[str, int, float]]:
    """(language, tokens, ratio to the baseline language) for each text."""
    base = count_tokens(texts[baseline], tokenizer)
    return [(lang, count_tokens(text, tokenizer), count_tokens(text, tokenizer) / base)
            for lang, text in texts.items()]


def main() -> None:
    print("Same message, six languages (approximate tokenizer):\n")
    print(f"{'Language':<10} {'Tokens':>6}  {'vs English':>10}")
    for lang, tokens, ratio in language_table(LANGUAGE_SAMPLE):
        print(f"{lang:<10} {tokens:>6}  {ratio:>9.2f}x")

    print("\nFirst tokens of the English sentence:",
          approx_tokenize(LANGUAGE_SAMPLE["English"])[:8])

    report = LANGUAGE_SAMPLE["English"] * 40  # stand-in for a ~2-page field report
    one = estimate_cost(report, expected_output_tokens=600, price=EXAMPLE_PRICES["large"])
    month = one.times(300 * 30)  # 300 reports a day for 30 days
    print(f"\nOne report on the 'large' tier: {one.input_tokens} in + {one.output_tokens} out"
          f" = USD {one.cost_usd:.4f}")
    print(f"300 reports a day for a month:  USD {month.cost_usd:,.2f}"
          " (illustrative prices, not a quote)")


if __name__ == "__main__":
    main()
