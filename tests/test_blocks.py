"""The block reader: what each Markdown construct becomes."""
from markdown2pptx.blocks import cells, parse


def kinds(src):
    return [b.kind for b in parse(src)[1]]


def test_front_matter_headings_and_breaks():
    meta, blocks = parse("---\ntitle: 'Q3'\nauthor: Ann\n---\n# One\n\nText\n\n---\n\nSetext\n======\n")
    assert meta == {"title": "Q3", "author": "Ann"}
    assert [(b.kind, b.level, b.text) for b in blocks] == [
        ("heading", 1, "One"), ("para", 0, "Text"), ("break", 0, ""), ("heading", 1, "Setext")]
    assert blocks[0].line == 5


def test_a_dash_line_under_a_paragraph_is_a_heading_not_a_break():
    assert kinds("Title\n---\n") == ["heading"]
    assert kinds("Text\n\n---\n") == ["para", "break"]


def test_lists_nest_continue_and_carry_tasks():
    _, (b,) = parse("- a\n  more\n    - b\n\n- [x] c\n1. d\n")
    assert b.kind == "list"
    assert b.items == [(0, "-", "a\nmore", None), (4, "-", "b", None), (0, "-", "c", True), (0, "1.", "d", None)]


def test_fences_keep_their_content_verbatim():
    _, blocks = parse("```mermaid\nflowchart LR\n  A --> B\n# not a heading\n```\n~~~\nx\n~~~")
    assert [(b.kind, b.lang, b.text) for b in blocks] == [
        ("code", "mermaid", "flowchart LR\n  A --> B\n# not a heading"), ("code", "", "x")]


def test_tables_with_alignment_and_escaped_pipes():
    _, (t,) = parse("| a | b | c |\n|:--|:-:|--:|\n| 1 | x \\| y | 3 |\n")
    assert t.rows == [["a", "b", "c"], ["1", "x | y", "3"]] and t.align == ["left", "center", "right"]
    assert cells("a|b") == ["a", "b"]


def test_notes_quotes_callouts_and_images():
    src = "::: notes\nsay this\n:::\n<!-- and\nthis -->\n> [!WARNING]\n> careful\n\n![alt](img/a.png)\n"
    _, blocks = parse(src)
    assert [(b.kind, b.text) for b in blocks] == [
        ("notes", "say this"), ("notes", "and\nthis"), ("quote", "**Warning:** careful"), ("image", "alt")]
    assert blocks[-1].lang == "img/a.png"


def test_an_image_inside_a_paragraph_is_text():
    assert kinds("See ![x](a.png) here\n") == ["para"]
