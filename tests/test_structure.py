"""Which headings are chapters and slides, what each slide holds: the plan, before any drawing."""
import pytest

from markdown2pptx import InputError, Options, plan
from markdown2pptx.model import Code, ListBlock, Mermaid, Paragraph, Picture, Subheading, Table
from helpers import png


def outline(deck):
    return [(s.chapter, s.title, s.kind) for s in deck.slides]


def test_a_lone_h1_is_the_title_and_a_short_line_under_it_the_subtitle():
    d = plan("# Talk\n\nA subtitle\n\n## One\n\ntext\n\n## Two\n\nmore\n")
    assert (d.title, d.subtitle) == ("Talk", "A subtitle")
    assert outline(d) == [(None, "One", "text"), (None, "Two", "text")]


def test_slide_level_is_the_highest_heading_followed_by_content():
    d = plan("# Part A\n## Slide 1\nx\n## Slide 2\ny\n# Part B\n## Slide 3\nz\n#### detail\nw\n", name="f")
    assert d.title == "f"
    assert outline(d) == [("Part A", "Slide 1", "text"), ("Part A", "Slide 2", "text"), ("Part B", "Slide 3", "text")]
    assert isinstance(d.slides[2].blocks[1], Subheading)
    assert d.chapters() == ["Part A", "Part B"]


def test_slide_level_option_and_front_matter():
    src = "---\ntitle: Deck\nsubtitle: Sub\nauthor: Ann\n---\n# A\ntext\n## B\nmore\n"
    d = plan(src, Options(slide_level=2))
    assert (d.title, d.subtitle, d.author) == ("Deck", "Sub", "Ann")
    assert outline(d) == [("A", "A", "text"), ("A", "B", "text")]       # content under a chapter: its own slide
    assert plan(src, Options(title="Mine", author="")).title == "Mine"


def test_a_break_starts_a_slide_with_the_same_title_and_a_second_visual_too():
    d = plan("## S\n\none\n\n---\n\ntwo\n\n| a |\n|---|\n| 1 |\n\n```mermaid\nflowchart LR\nA-->B\n```\n")
    assert outline(d) == [(None, "S", "text"), (None, "S", "table"), (None, "S", "diagram")]
    assert isinstance(d.slides[1].blocks[0], Paragraph) and isinstance(d.slides[1].visual, Table)
    assert isinstance(d.slides[2].visual, Mermaid) and d.slides[2].visual.src == "flowchart LR\nA-->B"


def test_headings_only_split_by_breaks():
    d = plan("first\n\n---\n\nsecond\n", name="notes")
    assert outline(d) == [(None, "notes", "text"), (None, "notes", "text")]


def test_lists_get_levels_and_numbers():
    d = plan("## L\n\n3. a\n4. b\n   - c\n   - d\n5. e\n")
    items = d.slides[0].blocks[0].items
    assert isinstance(d.slides[0].blocks[0], ListBlock)
    assert [(it.level, it.number) for it in items] == [(0, 3), (0, 4), (1, None), (1, None), (0, 5)]


def test_code_tables_and_notes():
    d = plan("## C\n\n::: notes\nhello\n:::\n\n```python\nx = 1\n```\n\n<!-- more -->\n")
    s = d.slides[0]
    assert isinstance(s.blocks[0], Code) and s.blocks[0].lang == "python" and s.notes == "hello\n\nmore"
    d = plan("<!-- before -->\n## A\ntext\n")
    assert d.slides[0].notes == "before"


def test_images_are_read_next_to_the_markdown(tmp_path):
    (tmp_path / "img").mkdir()
    (tmp_path / "img" / "a.png").write_bytes(png())
    (tmp_path / "b.svg").write_text("<svg xmlns='http://www.w3.org/2000/svg'/>")
    src = "## P\n\n![chart](img/a.png)\n\n## Q\n\n![missing](nope.png)\n\n![vector](b.svg)\n\n![web](https://x.org/a.png)\n"
    d = plan(src, Options(base_dir=tmp_path))
    assert isinstance(d.slides[0].visual, Picture) and d.slides[0].visual.alt == "chart"
    assert [w.split(": ", 1)[1].split(" ")[0] for w in d.warnings] == ["image", "b.svg", "https://x.org/a.png"]
    assert [b.runs[0].text for b in d.slides[1].blocks] == ["[missing]", "[vector]", "[web]"]


def test_empty_and_bad_options():
    with pytest.raises(InputError, match="empty"):
        plan("\n\n<!-- only a comment -->\n")
    with pytest.raises(ValueError, match="aspect"):
        plan("x", Options(aspect="1:1"))
    with pytest.raises(ValueError, match="slide level"):
        plan("x", Options(slide_level=7))


def test_summary_counts_kinds_and_chapters():
    d = plan("# A\n## s\n```mermaid\nflowchart LR\nA-->B\n```\n## t\ntext\n# B\n## u\n| a |\n|---|\n| 1 |\n")
    assert d.summary() == "3 content slides (1 diagram, 1 table, 1 text), 2 chapters"
