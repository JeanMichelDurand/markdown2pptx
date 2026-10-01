"""Inline Markdown as styled runs."""
from markdown2pptx.inline import plain_text, runs
from markdown2pptx.model import Run


def test_emphasis_code_and_links():
    assert runs("a **bold** and *it* `x = 1` [site](https://e.org) ~~old~~") == [
        Run("a "), Run("bold", bold=True), Run(" and "), Run("it", italic=True), Run(" "),
        Run("x = 1", code=True), Run(" "), Run("site", link="https://e.org"), Run(" "), Run("old", strike=True)]


def test_nesting_and_bold_italic():
    assert runs("**bold _and it_**") == [Run("bold ", bold=True), Run("and it", bold=True, italic=True)]
    assert runs("***both***") == [Run("both", bold=True, italic=True)]
    assert runs("[**strong link**](u)") == [Run("strong link", bold=True, link="u")]


def test_bare_stars_underscores_and_escapes_stay_text():
    assert plain_text("2 * 3 * 4, snake_case_name, \\*not\\* it") == "2 * 3 * 4, snake_case_name, *not* it"
    assert runs("`a*b*c`") == [Run("a*b*c", code=True)]


def test_entities_tags_images_and_line_breaks():
    assert plain_text("R&amp;D <span>team</span><br>next ![logo](l.png) line\nwrapped") == \
        "R&D team next logo line wrapped"
    assert runs("<https://e.org>") == [Run("https://e.org", link="https://e.org")]
