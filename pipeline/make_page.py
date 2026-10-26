"""Fill the page template with the built dex data and write ../index.html as a complete HTML document."""
import json, re

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<style>
:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
body{margin:0;-webkit-text-size-adjust:100%;text-size-adjust:100%}
img{max-width:100%}
[hidden]{display:none!important}
</style>
<meta name="description" content="__DESC__">
<meta name="theme-color" content="#1f5a36">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%231f5a36'/%3E%3Cpolygon points='32,10 51,21 51,43 32,54 13,43 13,21' fill='%239e1b32' stroke='%23f7f8f4' stroke-width='4' stroke-linejoin='round'/%3E%3C/svg%3E">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Gridiron Dex">
<meta property="og:title" content="Gridiron Dex: every FBS team as a Pokémon">
<meta property="og:description" content="__DESC__">
<meta property="og:url" content="__SITE__">
<meta property="og:image" content="__SITE__og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Gridiron Dex: a team's six-stat radar chart on a football-field background">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Gridiron Dex: every FBS team as a Pokémon">
<meta name="twitter:description" content="__DESC__">
<meta name="twitter:image" content="__SITE__og.png">
"""
SITE = "https://joshmorris49.github.io/cfb-dex/"
DESC = ("Every FBS team's 2026 season as six Pokémon-style base stats, matched to the Pokémon it plays like. "
        "Plus this week's head-to-head matchups and a Gen 1 edition.")
HEAD = HEAD.replace("__SITE__", SITE).replace("__DESC__", DESC)

data = json.load(open("dex_colored.json"))
for d in data:  # drop fields the page never reads
    d["match"].pop("dist", None); d["g1"]["match"].pop("dist", None); d["col"].pop("all", None)
meta = json.load(open("dex_meta.json"))
through = open("data/through.txt").read().strip()
import csv
week = list(csv.DictReader(open("data/week.csv")))
body = (open("template.html").read()
        .replace("__DATA__", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
        .replace("__THROUGH__", through)
        .replace("__G1_UNUSED__", ", ".join(meta["g1_unused"]))
        .replace("__WEEK__", json.dumps(week, ensure_ascii=False, separators=(",", ":"))))
body = re.sub(r'const SPRITE_DIR = "[^"]*";', 'const SPRITE_DIR = "sprites/";', body, count=1)
body = body.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', "")
# head-level tags (title, font links, styles) go in <head>; the rest of the template is the body
split = body.index('<div class="wrap">')
page = HEAD + body[:split] + "</head>\n<body>\n" + body[split:] + "\n</body>\n</html>\n"
open("../index.html", "w").write(page)
print("wrote ../index.html")
