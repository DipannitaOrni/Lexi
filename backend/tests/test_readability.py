from app.utils.readability import compute_readability


def test_complex_text_scores_higher_grade_than_simple_text():
    complex_text = (
        "The applicant must submit the requisite documentation prior to the "
        "stipulated deadline, notwithstanding any extenuating circumstances."
    )
    simple_text = "You must send the papers before the deadline. Send them even if something goes wrong."

    complex_stats = compute_readability(complex_text)
    simple_stats = compute_readability(simple_text)

    assert complex_stats.flesch_kincaid_grade > simple_stats.flesch_kincaid_grade


def test_empty_text_returns_zeroed_stats():
    stats = compute_readability("")
    assert stats.word_count == 0
    assert stats.flesch_kincaid_grade == 0.0
