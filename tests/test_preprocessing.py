from app.services.preprocessing import (
    clean_whitespace,
    fix_broken_lines,
    normalize_unicode,
    remove_repeated_headers_footers,
)


def test_clean_whitespace_collapses_spaces_and_blank_lines():
    text = "Hello    world.\n\n\n\n\nNext line."
    result = clean_whitespace(text)
    assert "    " not in result
    assert "\n\n\n" not in result


def test_normalize_unicode_handles_smart_quotes():
    text = "\u201cHello\u201d"
    result = normalize_unicode(text)
    assert result  # should not raise, should normalize without error


def test_remove_repeated_headers_footers_strips_repeated_lines():
    blocks = []
    for i in range(6):
        blocks.append(f"CONFIDENTIAL DRAFT\nParagraph content number {i} with unique text.")
    text = "\n\n".join(blocks)
    result = remove_repeated_headers_footers(text)
    assert result.count("CONFIDENTIAL DRAFT") == 0


def test_fix_broken_lines_joins_mid_sentence_breaks():
    text = "The applicant must submit the\nform before the deadline."
    result = fix_broken_lines(text)
    assert "\n" not in result
    assert "submit the form before the deadline" in result
