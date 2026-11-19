# -*- coding: utf-8 -*-
"""Pack public/ into deploy.zip with forward-slash paths (Netlify requires it).

Usage: python pack.py   (run inside the blog folder)
Note: console output is ASCII-only so it renders correctly in cmd.
"""
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PUBLIC = HERE / "public"
ZIP = HERE / "deploy.zip"


def fail(msg):
    print(f"  [FAIL] {msg}")
    sys.exit(1)


if not PUBLIC.exists():
    fail("no public/ folder, run hexo generate first")

if ZIP.exists():
    ZIP.unlink()

files = [p for p in PUBLIC.rglob("*") if p.is_file()]
with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for p in sorted(files):
        z.write(p, p.relative_to(PUBLIC).as_posix())

with zipfile.ZipFile(ZIP) as z:
    names = z.namelist()
    bad = [n for n in names if "\\" in n]
    has_index = "index.html" in names
    has_css = "css/main.css" in names

print(f"  entries={len(names)} backslash_paths={len(bad)} index={has_index} css={has_css}")
print(f"  deploy.zip = {ZIP.stat().st_size / 1024 / 1024:.1f} MB")

if bad or not has_index or not has_css:
    fail("zip layout is wrong")
