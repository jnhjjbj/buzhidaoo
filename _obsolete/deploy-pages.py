# -*- coding: utf-8 -*-
"""一键发布到 GitHub Pages：构建 + 推送 gh-pages 分支。

用法：python deploy-pages.py      （在 blog 目录）
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PUBLIC = HERE / "public"
REMOTE = "https://github.com/jnhjjbj/buzhidaoo.git"


def run(cmd, cwd=None, quiet=False):
    r = subprocess.run(cmd, cwd=cwd, shell=False,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0 and not quiet:
        print("  [FAIL]", " ".join(cmd))
        print("   ", (r.stderr or r.stdout or "").strip()[:400])
        sys.exit(1)
    return r


if not PUBLIC.exists():
    print("  no public/, run build first")
    sys.exit(1)

tmp = Path(tempfile.mkdtemp(prefix="ghpages-"))
print(f"  temp dir: {tmp}")
for item in PUBLIC.iterdir():
    if item.is_dir():
        shutil.copytree(item, tmp / item.name)
    else:
        shutil.copy2(item, tmp / item.name)
(tmp / ".nojekyll").write_text("", encoding="utf-8")

run(["git", "init", "-q"], cwd=tmp)
run(["git", "add", "-A"], cwd=tmp)
run(["git", "-c", "user.name=deploy-bot", "-c", "user.email=bot@local",
     "commit", "-q", "-m", "deploy: update site"], cwd=tmp)
run(["git", "remote", "add", "origin", REMOTE], cwd=tmp)

print("  pushing to gh-pages ...")
r = run(["git", "push", "-f", "origin", "HEAD:gh-pages"], cwd=tmp)
print("  push ok")

shutil.rmtree(tmp, ignore_errors=True)
print()
print("  Live: https://jnhjjbj.github.io/buzhidaoo/")
print("  Takes about 30-60 seconds to go live.")
