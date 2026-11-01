import hashlib
import json
import os
from pathlib import Path

import pytest

from shiptools import anchored_edit, deploylist, parity
from shiptools.manifest import build_manifest, read_manifest, write_manifest


def make_tree(root: Path, files: dict[str, str]) -> Path:
    for rel, text in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return root


BASE = {
    "app/main.py": "print('hello')\n",
    "app/templates/start.html": "<h1>Start</h1>\n",
    "tests/test_main.py": "def test_ok():\n    assert True\n",
}


# ------------------------------------------------------------------ manifest
def test_manifest_hashes_match_hashlib(tmp_path):
    make_tree(tmp_path, BASE)
    m = build_manifest(tmp_path)
    assert set(m) == set(BASE)
    for rel, text in BASE.items():
        assert m[rel] == hashlib.md5(text.encode()).hexdigest()


def test_manifest_skips_caches_secrets_and_symlinks(tmp_path):
    make_tree(tmp_path, {**BASE, ".env": "KEY=x\n", "app/__pycache__/main.cpython-313.pyc": "x",
                         ".git/HEAD": "ref", "app/.DS_Store": "x"})
    outside = tmp_path.parent / "outside.txt"
    outside.write_text("foreign", encoding="utf-8")
    os.symlink(outside, tmp_path / "app" / "link.txt")
    m = build_manifest(tmp_path)
    assert set(m) == set(BASE)


def test_manifest_include_restricts_to_top_level_paths(tmp_path):
    make_tree(tmp_path, {**BASE, "docs/notes.md": "x"})
    assert set(build_manifest(tmp_path, include=["app"])) == {"app/main.py", "app/templates/start.html"}


def test_manifest_roundtrip_and_md5sum_format(tmp_path):
    make_tree(tmp_path / "t", BASE)
    m = build_manifest(tmp_path / "t")
    write_manifest(m, tmp_path / "m.txt")
    assert read_manifest(tmp_path / "m.txt") == m
    # md5sum binary-mode marker and upper-case hex are accepted
    line = f"{m['app/main.py'].upper()} *app/main.py\n"
    (tmp_path / "m2.txt").write_text(line, encoding="utf-8")
    assert read_manifest(tmp_path / "m2.txt") == {"app/main.py": m["app/main.py"]}


def test_manifest_rejects_garbage(tmp_path):
    (tmp_path / "bad.txt").write_text("not a manifest\n", encoding="utf-8")
    with pytest.raises(ValueError):
        read_manifest(tmp_path / "bad.txt")


# ------------------------------------------------------------------ parity
def test_parity_ok_for_identical_trees(tmp_path, capsys):
    make_tree(tmp_path / "mac", BASE)
    make_tree(tmp_path / "server", BASE)
    assert parity.main([str(tmp_path / "mac"), str(tmp_path / "server")]) == 0
    assert "PARITY OK: 3/3 identical" in capsys.readouterr().out


def test_parity_reports_every_kind_of_difference(tmp_path):
    make_tree(tmp_path / "mac", {**BASE, "app/new.py": "x"})
    server = dict(BASE)
    server["app/main.py"] = "print('hotfix on the server')\n"
    server["app/stale.py"] = "old"
    make_tree(tmp_path / "server", server)
    rep = parity.compare(build_manifest(tmp_path / "mac"), build_manifest(tmp_path / "server"))
    assert not rep.ok
    assert rep.differ == ["app/main.py"]
    assert rep.only_left == ["app/new.py"]
    assert rep.only_right == ["app/stale.py"]
    assert rep.total == 5


def test_parity_tree_against_manifest_file(tmp_path):
    make_tree(tmp_path / "mac", BASE)
    write_manifest(build_manifest(tmp_path / "mac"), tmp_path / "server_md5.txt")
    assert parity.main([str(tmp_path / "mac"), str(tmp_path / "server_md5.txt"), "-q"]) == 0


def test_parity_include_applies_to_manifest_files_too(tmp_path):
    make_tree(tmp_path / "mac", {**BASE, "docs/x.md": "only on the mac"})
    write_manifest(build_manifest(tmp_path / "mac", include=["app", "tests"]), tmp_path / "srv.txt")
    assert parity.main([str(tmp_path / "mac"), str(tmp_path / "srv.txt"), "--include", "app", "tests"]) == 0
    assert parity.main([str(tmp_path / "mac"), str(tmp_path / "srv.txt")]) == 1


def test_parity_bad_input_exit_code(tmp_path):
    assert parity.main([str(tmp_path / "missing"), str(tmp_path)]) == 2


# ------------------------------------------------------------------ deploy list
def test_deploy_list_against_production_base(tmp_path, capsys):
    make_tree(tmp_path / "prod", BASE)
    cand = dict(BASE)
    cand["app/templates/start.html"] = "<h1>Start here</h1>\n"
    cand["tests/test_start.py"] = "def test_start():\n    assert True\n"
    del cand["tests/test_main.py"]
    make_tree(tmp_path / "copy", cand)
    out_tsv = tmp_path / "list.tsv"
    assert deploylist.main([str(tmp_path / "prod"), str(tmp_path / "copy"), "--tsv", str(out_tsv)]) == 0
    rows = [r.split("\t") for r in out_tsv.read_text(encoding="utf-8").splitlines()]
    assert rows[0] == list(deploylist.HEADER)
    assert [(r[0], r[1]) for r in rows[1:]] == [
        ("changed", "app/templates/start.html"),
        ("new", "tests/test_start.py"),
        ("removed", "tests/test_main.py"),
    ]
    assert "1 changed, 1 new, 1 removed" in capsys.readouterr().out


def test_deploy_list_is_relative_to_the_base_not_to_another_copy(tmp_path):
    """Two parallel changes, each listed against production, never undo each other."""
    prod = build_manifest(make_tree(tmp_path / "prod", BASE))
    a = dict(BASE, **{"app/main.py": "print('change A')\n"})
    b = dict(BASE, **{"app/templates/start.html": "<h1>change B</h1>\n"})
    list_a = deploylist.deploy_list(prod, build_manifest(make_tree(tmp_path / "a", a)))
    list_b = deploylist.deploy_list(prod, build_manifest(make_tree(tmp_path / "b", b)))
    assert [e.path for e in list_a] == ["app/main.py"]
    assert [e.path for e in list_b] == ["app/templates/start.html"]
    # Listing B against copy A instead would wrongly ship A's file back to its old content.
    wrong = deploylist.deploy_list(build_manifest(tmp_path / "a"), build_manifest(tmp_path / "b"))
    assert {e.path for e in wrong} == {"app/main.py", "app/templates/start.html"}


def test_deploy_list_empty_when_nothing_changed(tmp_path):
    m = build_manifest(make_tree(tmp_path / "p", BASE))
    assert deploylist.deploy_list(m, m) == []
    assert "no differences" in deploylist.to_table([])


# ------------------------------------------------------------------ anchored edits
def write_plan(path: Path, edits: list[dict]) -> Path:
    path.write_text(json.dumps(edits), encoding="utf-8")
    return path


def test_anchored_edit_applies_once_and_refuses_a_second_run(tmp_path, capsys):
    root = make_tree(tmp_path / "copy", BASE)
    plan = write_plan(tmp_path / "plan.json", [
        {"file": "app/templates/start.html", "anchor": "<h1>Start</h1>", "replacement": "<h1>Start here</h1>"},
    ])
    assert anchored_edit.main([str(plan), str(root)]) == 0
    assert (root / "app/templates/start.html").read_text() == "<h1>Start here</h1>\n"
    assert anchored_edit.main([str(plan), str(root)]) == 1
    assert "applied twice" in capsys.readouterr().err


def test_anchored_edit_is_all_or_nothing(tmp_path):
    root = make_tree(tmp_path / "copy", BASE)
    before = build_manifest(root)
    plan = write_plan(tmp_path / "plan.json", [
        {"file": "app/main.py", "anchor": "hello", "replacement": "hi"},
        {"file": "app/templates/start.html", "anchor": "missing anchor", "replacement": "x"},
    ])
    assert anchored_edit.main([str(plan), str(root)]) == 1
    assert build_manifest(root) == before  # the valid first edit was not written either


def test_anchored_edit_rejects_ambiguous_anchor(tmp_path):
    root = make_tree(tmp_path / "copy", {"a.txt": "x = 1\nx = 1\n"})
    with pytest.raises(anchored_edit.PlanError, match="found 2 times"):
        anchored_edit.apply([anchored_edit.Edit("a.txt", "x = 1", "x = 2")], root)


def test_anchored_edit_dry_run_writes_nothing(tmp_path):
    root = make_tree(tmp_path / "copy", BASE)
    before = build_manifest(root)
    changed = anchored_edit.apply([anchored_edit.Edit("app/main.py", "hello", "hi")], root, dry_run=True)
    assert [p.name for p in changed] == ["main.py"]
    assert build_manifest(root) == before


def test_anchored_edit_cannot_leave_the_working_copy(tmp_path):
    root = make_tree(tmp_path / "copy", BASE)
    (tmp_path / "secret.txt").write_text("outside", encoding="utf-8")
    with pytest.raises(anchored_edit.PlanError, match="leaves the working copy"):
        anchored_edit.apply([anchored_edit.Edit("../secret.txt", "outside", "x")], root)


def test_anchored_edit_bad_plan(tmp_path):
    root = make_tree(tmp_path / "copy", BASE)
    plan = write_plan(tmp_path / "plan.json", [{"file": "app/main.py", "anchor": "x", "replacement": "x"}])
    assert anchored_edit.main([str(plan), str(root)]) == 2
    (tmp_path / "p2.json").write_text("{}", encoding="utf-8")
    assert anchored_edit.main([str(tmp_path / "p2.json"), str(root)]) == 2
