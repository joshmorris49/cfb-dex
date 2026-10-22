"""Fill the page template with the built dex data and write ../index.html."""
import json, re
page = open("template.html").read().replace("__DATA__", json.dumps(json.load(open("dex_colored.json")), ensure_ascii=False))
page = re.sub(r'const SPRITE_DIR = "[^"]*";', 'const SPRITE_DIR = "sprites/";', page, count=1)
open("../index.html", "w").write(page)
print("wrote ../index.html")
