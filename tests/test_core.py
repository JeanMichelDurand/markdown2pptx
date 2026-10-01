"""The work itself: core.py, without the command line."""
import pytest

from markdown2pptx import InputError, Stats, count


def test_counts_lines_and_words():
    assert count("one two\nthree\n") == Stats(lines=2, words=3)


def test_summary_is_singular_for_one():
    assert Stats(1, 1).summary() == "1 line, 1 word"
    assert Stats(2, 0).summary() == "2 lines, 0 words"


def test_empty_input_is_an_input_error():
    with pytest.raises(InputError, match="empty"):
        count("  \n")
