# -*- coding: utf-8 -*-
"""一次构建，双路发布：

  A. GitHub Pages  —— root: /buzhidaoo/，推到 gh-pages 分支
  B. Netlify       —— root: /，打包成 deploy-netlify.zip（拖拽用）

两套的 root 不一样，所以必须分别构建，不能共用一个 public/。
"""
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CFG = HERE / "_config.yml"
PUBLIC = HERE / "public"
NODE = Path(r"C:\Users\a'su's\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin\node.exe")
HEXO = HERE / "node_modules" / "hexo" / "bin" / "hexo"
REMOTE = "https://github.com/jnhjjbj/buzhidaoo.git"

PAGES_URL = "https://jnhjjbj.github.io/buzhidaoo"
PAGES_ROOT = "/buzhidaoo/"
NETLIFY_URL = "https://serene-elf-swws.netlify.app"
NETLIFY_ROOT = "/"


def run(cmd, cwd=None, quiet=True):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print("  [FAIL]", " ".join(str(c) for c in cmd))
        print("   ", (r.stderr or r.stdout or "").strip()[:500])
        sys.exit(1)
    return r


def hexo_build():
    run([str(NODE), str(HEXO), "clean"], cwd=HERE)
    run([str(NODE), str(HEXO), "generate"], cwd=HERE)


def set_url_root(url, root):
    text = CFG.read_bytes().decode("utf-8")
    if text.startswith("\ufeff"):
        text = text[1:]
    text = re.sub(r"(?m)^url:.*$", f"url: {url}", text)
    if re.search(r"(?m)^root:", text):
        text = re.sub(r"(?m)^root:.*$", f"root: {root}", text)
    else:
        text = text.replace(f"url: {url}", f"url: {url}\nroot: {root}", 1)
    CFG.write_bytes(text.encode("utf-8"))


def make_zip(dest: Path):
    if dest.exists():
        dest.unlink()
    files = [p for p in PUBLIC.rglob("*") if p.is_file()]
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in sorted(files):
            z.write(p, p.relative_to(PUBLIC).as_posix())
    with zipfile.ZipFile(dest) as z:
        names = z.namelist()
    bad = [n for n in names if "\\" in n]
    ok = "index.html" in names and "css/main.css" in names
    print(f"  zip: {len(names)} files, backslash={len(bad)}, ok={ok}, "
          f"{dest.stat().st_size/1024/1024:.2f} MB")
    if bad or not ok:
        sys.exit(1)


def push_pages():
    tmp = Path(tempfile.mkdtemp(prefix="ghpages-"))
    for item in PUBLIC.iterdir():
        if item.is_dir():
            shutil.copytree(item, tmp / item.name)
        else:
            shutil.copy2(item, tmp / item.name)
    (tmp / ".nojekyll").write_text("", encoding="utf-8")
    for cmd in (["git", "init", "-q"], ["git", "add", "-A"],
                ["git", "-c", "user.name=deploy-bot", "-c", "user.email=bot@local",
                 "commit", "-q", "-m", "deploy: update site"]):
        run(cmd, cwd=tmp)
    run(["git", "remote", "add", "origin", REMOTE], cwd=tmp)
    run(["git", "push", "-f", "origin", "HEAD:gh-pages"], cwd=tmp)
    shutil.rmtree(tmp, ignore_errors=True)
    print("  pushed gh-pages")


def push_main():
    """把源码改动提交并推到 main —— Netlify 靠这个触发自动构建。"""
    try:
        run(["git", "add", "-A"], cwd=HERE)
        st = subprocess.run(["git", "status", "--porcelain"], cwd=HERE,
                            capture_output=True, text=True)
        if not st.stdout.strip():
            print("  main: nothing to commit")
            return
        from datetime import datetime
        msg = "publish: " + datetime.now().strftime("%Y-%m-%d %H:%M")
        run(["git", "-c", "user.name=deploy-bot", "-c", "user.email=bot@local",
             "commit", "-q", "-m", msg], cwd=HERE)
        run(["git", "push", "origin", "main"], cwd=HERE)
        print("  main: committed and pushed (Netlify will auto-build)")
    except SystemExit:
        raise
    except Exception as exc:
        print("  main push skipped:", exc)


def main():
    original = CFG.read_bytes()

    print("[A] build for GitHub Pages")
    set_url_root(PAGES_URL, PAGES_ROOT)
    hexo_build()
    push_pages()
    print(f"    -> {PAGES_URL}/")

    print()
    print("[B] build for Netlify (root = /)")
    set_url_root(NETLIFY_URL, NETLIFY_ROOT)
    hexo_build()
    out = HERE / "deploy-netlify.zip"
    make_zip(out)
    print(f"    -> {NETLIFY_URL} (auto) / {out.name} (manual backup)")

    print()
    print("[C] restore config to Pages, rebuild, push source to main")
    CFG.write_bytes(original)
    hexo_build()
    push_main()
    print("    done.")


if __name__ == "__main__":
    main()
