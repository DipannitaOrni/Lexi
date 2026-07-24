"""
Lightweight token estimation without an extra tokenizer dependency.
Heuristic: ~4 characters per token for English text. Good enough for
chunk-budgeting purposes; not used for anything that needs exact counts.
"""


def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    # A slightly conservative estimate (3.5 chars/token) errs toward
    # under-filling chunks rather than overflowing the model's context.
    return max(1, int(len(text) / 3.5))
