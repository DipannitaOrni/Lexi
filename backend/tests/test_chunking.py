from app.utils.chunking import chunk_text
from app.utils.token_estimation import estimate_tokens


def test_chunk_text_respects_budget():
    text = "\n\n".join([f"This is paragraph number {i}. It has a few words in it." for i in range(50)])
    chunks = chunk_text(text, max_tokens_per_chunk=100)
    assert len(chunks) > 1
    for c in chunks:
        assert estimate_tokens(c.text) <= 100 + 20  # small tolerance for join overhead


def test_chunk_text_preserves_all_paragraphs():
    paragraphs = [f"Paragraph {i} content here." for i in range(10)]
    text = "\n\n".join(paragraphs)
    chunks = chunk_text(text, max_tokens_per_chunk=1000)
    combined = " ".join(c.text for c in chunks)
    for p in paragraphs:
        assert p in combined


def test_chunk_text_empty_input_returns_one_empty_chunk():
    chunks = chunk_text("", max_tokens_per_chunk=100)
    assert len(chunks) == 1
    assert chunks[0].text == ""


def test_oversized_single_paragraph_splits_by_sentence():
    long_paragraph = " ".join([f"Sentence number {i} is here." for i in range(200)])
    chunks = chunk_text(long_paragraph, max_tokens_per_chunk=50)
    assert len(chunks) > 1
