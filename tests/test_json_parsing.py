import pytest

from app.utils.json_parsing import JsonParseError, parse_json_safely


def test_parses_clean_json():
    raw = '{"rewritten_text": "hello", "mode": "dyslexia"}'
    result = parse_json_safely(raw)
    assert result["rewritten_text"] == "hello"


def test_parses_json_wrapped_in_markdown_fence():
    raw = '```json\n{"rewritten_text": "hello"}\n```'
    result = parse_json_safely(raw)
    assert result["rewritten_text"] == "hello"


def test_parses_json_with_surrounding_prose():
    raw = 'Here is the result:\n{"answer": "42"}\nHope that helps!'
    result = parse_json_safely(raw)
    assert result["answer"] == "42"


def test_raises_on_no_json_present():
    with pytest.raises(JsonParseError):
        parse_json_safely("This response has no JSON at all.")


def test_raises_on_empty_input():
    with pytest.raises(JsonParseError):
        parse_json_safely(None)
