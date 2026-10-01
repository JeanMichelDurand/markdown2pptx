"""The command line, run in-process on real files."""
import pytest

from markdown2pptx import __version__
from markdown2pptx.cli import main


def test_prints_one_line_per_file(tmp_path, capsys):
    f = tmp_path / "notes.txt"
    f.write_text("one two\nthree\n", encoding="utf-8")
    assert main([str(f)]) == 0
    assert capsys.readouterr().out == f"{f}: 2 lines, 3 words\n"


def test_bad_file_is_reported_and_the_others_still_run(tmp_path, capsys):
    good = tmp_path / "good.txt"
    good.write_text("hello", encoding="utf-8")
    empty = tmp_path / "empty.txt"
    empty.write_text("", encoding="utf-8")
    assert main([str(tmp_path / "missing.txt"), str(empty), str(good)]) == 1
    out, err = capsys.readouterr()
    assert "missing.txt: error:" in err and "empty.txt: error: the input is empty" in err
    assert "good.txt: 1 line, 1 word" in out


def test_version(capsys):
    with pytest.raises(SystemExit) as e:
        main(["--version"])
    assert e.value.code == 0
    assert capsys.readouterr().out.strip() == f"markdown2pptx {__version__}"
