#!/usr/bin/env python3
"""Download the site's images from the original CDN and optimize them to WebP.

Reads assets/manifest.tsv (local-name <TAB> source-url), saves originals to assets/src/
and writes resized WebP files (max 1600px wide) to public/assets/img/<name>.webp.
Safe to re-run: existing files are skipped. Needs Pillow (apt: python3-pil, pip: pillow).
"""
import os, sys, urllib.request, concurrent.futures as cf
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets/src"; OUT = ROOT / "public/assets/img"
SRC.mkdir(parents=True, exist_ok=True); OUT.mkdir(parents=True, exist_ok=True)
try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow is required: sudo apt-get install -y python3-pil   (or: pip install pillow)")

def one(line):
    name, url = line.rstrip("\n").split("\t")
    stem = name.rsplit(".", 1)[0]
    dst = OUT / f"{stem}.webp"
    if dst.exists() and dst.stat().st_size: return f"ok    {dst.name}"
    raw = SRC / name
    if not raw.exists() or not raw.stat().st_size:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (site asset fetch)"})
        with urllib.request.urlopen(req, timeout=60) as r, open(raw, "wb") as f: f.write(r.read())
    im = Image.open(raw)
    if im.mode not in ("RGB", "RGBA"):
        im = im.convert("RGBA" if "A" in im.mode or "transparency" in im.info else "RGB")
    if im.width > 1600: im = im.resize((1600, round(im.height * 1600 / im.width)), Image.LANCZOS)
    im.save(dst, "WEBP", quality=80, method=4)
    return f"saved {dst.name}"

lines = [l for l in open(ROOT / "assets/manifest.tsv") if l.strip()]
failed = 0
with cf.ThreadPoolExecutor(8) as ex:
    for fut in cf.as_completed([ex.submit(one, l) for l in lines]):
        try: print(fut.result())
        except Exception as err: failed += 1; print("FAIL ", err)
print(f"{len(lines) - failed}/{len(lines)} images ready in {OUT}")
sys.exit(1 if failed else 0)
