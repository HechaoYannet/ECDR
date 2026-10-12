"""Download arXiv full texts and reduce them to readable plain text.

Prefers the arXiv HTML rendering and falls back to the PDF plus pypdf. Text is
stripped of navigation and reference boilerplate so a reader spends its budget
on the argument rather than the furniture.
"""
from __future__ import annotations

import html
import pathlib
import re
import sys
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "literature" / "fulltext"
UA = "Mozilla/5.0 (compatible; ECDR-literature-review/0.1)"


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return r.read()
    except Exception:
        return None


def html_to_text(raw):
    raw = re.sub(r"<script[\s\S]*?</script>", " ", raw, flags=re.I)
    raw = re.sub(r"<style[\s\S]*?</style>", " ", raw, flags=re.I)
    raw = re.sub(r"<(nav|footer|header)[\s\S]*?</\1>", " ", raw, flags=re.I)
    raw = re.sub(r"<math[\s\S]*?</math>", " [MATH] ", raw, flags=re.I)
    raw = re.sub(r"<(h[1-6])[^>]*>", chr(10) + chr(10) + "## ", raw, flags=re.I)
    raw = re.sub(r"</(p|div|li|tr|h[1-6])>", chr(10), raw, flags=re.I)
    raw = re.sub(r"<[^>]+>", " ", raw)
    raw = html.unescape(raw)
    raw = raw.replace(chr(160), " ")
    raw = re.sub(r"[ \t]+", " ", raw)
    raw = re.sub(r"\n[ \t]*\n[ \t]*\n+", chr(10) + chr(10), raw)
    return raw.strip()


def pdf_to_text(data):
    try:
        import io
        from pypdf import PdfReader
    except ImportError:
        return ""
    try:
        reader = PdfReader(io.BytesIO(data))
        return chr(10).join((p.extract_text() or "") for p in reader.pages)
    except Exception:
        return ""


def cut_boilerplate(text):
    """Drop the reference list: long, and it adds nothing to the argument."""
    for marker in [chr(10) + "References" + chr(10), chr(10) + "REFERENCES" + chr(10)]:
        i = text.rfind(marker)
        if i > len(text) * 0.4:
            return text[:i].strip()
    return text.strip()


def fetch(arxiv_id, max_chars=260000):
    base = arxiv_id.split("v")[0]
    raw = _get("https://arxiv.org/html/" + arxiv_id)
    if raw and len(raw) > 5000:
        text = html_to_text(raw.decode("utf-8", "replace"))
        if len(text) > 4000:
            return cut_boilerplate(text)[:max_chars], "html"
    raw = _get("https://arxiv.org/pdf/" + arxiv_id)
    if raw:
        text = pdf_to_text(raw)
        if len(text) > 4000:
            return cut_boilerplate(text)[:max_chars], "pdf"
    raw = _get("https://arxiv.org/html/" + base)
    if raw and len(raw) > 5000:
        return cut_boilerplate(html_to_text(raw.decode("utf-8", "replace")))[:max_chars], "html-bare"
    return "", "failed"


def main(ids):
    OUT.mkdir(parents=True, exist_ok=True)
    for aid in ids:
        path = OUT / (aid + ".txt")
        if path.exists() and path.stat().st_size > 3000:
            print("  [skip] " + aid + " (" + str(path.stat().st_size) + " chars)")
            continue
        text, how = fetch(aid)
        if not text:
            print("  [FAIL] " + aid)
            continue
        path.write_text(text, encoding="utf-8")
        print("  [ok]   " + aid.ljust(14) + how.ljust(10) + str(len(text)) + " chars")
        time.sleep(2.0)


if __name__ == "__main__":
    main(sys.argv[1:])
