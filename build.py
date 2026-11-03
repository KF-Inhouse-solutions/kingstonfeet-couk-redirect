"""Forwarding site for kingstonfeet.co.uk: every page goes to the same page on kingstonfeet.com.

GitHub Pages can't send server redirects, so each known page is a tiny HTML page with an instant
meta refresh + canonical link (Google treats that as a permanent move), and 404.html forwards any
other address by script, keeping its path. The page list is read from the interim site's docs/.

Run: python3 build.py   (writes docs/)
"""
import re
import shutil
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
SITE = HERE.parent / "kingstonfeet-interim-site" / "docs"
OUT = HERE / "docs"
TARGET = "https://kingstonfeet.com"
DOMAIN = "kingstonfeet.co.uk"

PAGE = """<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>kingstonfeet has moved to kingstonfeet.com</title>
<link rel="canonical" href="{url}">
<meta http-equiv="refresh" content="0; url={url}">
<script>location.replace("{url}" + location.search + location.hash);</script>
</head>
<body style="font:16px/1.5 Helvetica, Arial, sans-serif; text-align:center; padding:60px 20px">
<p>kingstonfeet is now at <a href="{url}">{label}</a>.</p>
</body>
</html>
"""

NOT_FOUND = """<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>kingstonfeet has moved to kingstonfeet.com</title>
<meta name="robots" content="noindex">
<script>location.replace("{target}" + location.pathname + location.search + location.hash);</script>
<meta http-equiv="refresh" content="1; url={target}/">
</head>
<body style="font:16px/1.5 Helvetica, Arial, sans-serif; text-align:center; padding:60px 20px">
<p>kingstonfeet is now at <a href="{target}/">kingstonfeet.com</a>.</p>
</body>
</html>
"""


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    paths = sorted("/" + str(p.parent.relative_to(SITE)).replace(".", "").strip("/") + "/"
                   for p in SITE.rglob("index.html"))
    paths = [p.replace("//", "/") for p in paths]
    for path in paths:
        url = TARGET + path
        src = (SITE / path.strip("/") / "index.html").read_text()
        if 'http-equiv="refresh"' in src:   # an old page the .com already forwards: go straight to where it lands
            url = re.search(r'rel="canonical" href="([^"]+)"', src).group(1)
        d = OUT / path.strip("/")
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(PAGE.format(url=escape(url), label=escape(url.replace("https://", ""))))
    (OUT / "404.html").write_text(NOT_FOUND.format(target=TARGET))
    (OUT / "CNAME").write_text(DOMAIN + "\n")
    (OUT / ".nojekyll").write_text("")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n")
    print(len(paths), "pages forward to", TARGET)


if __name__ == "__main__":
    main()
