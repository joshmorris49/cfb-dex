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
"""

body = open("template.html").read().replace("__DATA__", json.dumps(json.load(open("dex_colored.json")), ensure_ascii=False))
body = re.sub(r'const SPRITE_DIR = "[^"]*";', 'const SPRITE_DIR = "sprites/";', body, count=1)
body = body.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', "")
# head-level tags (title, font links, styles) go in <head>; the rest of the template is the body
split = body.index('<div class="wrap">')
page = HEAD + body[:split] + "</head>\n<body>\n" + body[split:] + "\n</body>\n</html>\n"
open("../index.html", "w").write(page)
print("wrote ../index.html")
