import csv, json, colorsys

def rgb(h):
    h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
def hexs(c): return '#' + ''.join(f'{round(max(0, min(1, v)) * 255):02X}' for v in c)
def lum(h):
    def ch(v): return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = rgb(h); return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)
def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True); return (la + 0.05) / (lb + 0.05)
def chroma(h):
    c = rgb(h); return max(c) - min(c)

INK_DARK, INK_LIGHT = '#111111', '#FFFFFF'
SURF_LIGHT, SURF_DARK = '#FFFFFF', '#18201B'

def chart_color(cols):
    """A shade of the team's main hue that reads on both the light and dark card surface (about 3:1 or better)."""
    base = next((c for c in cols if chroma(c) > 0.12 and 0.02 < lum(c) < 0.9), cols[0])
    h, l, s = colorsys.rgb_to_hls(*rgb(base))
    lo, hi = 0.14, 0.22
    cur = lum(base)
    if lo <= cur <= hi: return base.upper()
    target = 0.15 if cur < lo else 0.21
    a, b = (l, 1.0) if cur < lo else (0.0, l)
    for _ in range(40):
        m = (a + b) / 2
        if lum(hexs(colorsys.hls_to_rgb(h, m, s))) < target: a = m
        else: b = m
    return hexs(colorsys.hls_to_rgb(h, (a + b) / 2, s))

colors = {r['team']: ['#' + c.upper() for c in r['colors'].split(';')] for r in csv.DictReader(open(__import__('sys').argv[3] if len(__import__('sys').argv)>3 else 'fbs/colors.csv'))}
dex = json.load(open(__import__('sys').argv[1]))
worst = []
for d in dex:
    cols = colors[d['team']]
    c1 = cols[0]
    fg = INK_LIGHT if contrast(c1, INK_LIGHT) >= contrast(c1, INK_DARK) else INK_DARK
    c2 = next((c for c in cols[1:] if contrast(c, c1) >= 1.5), fg)
    tc = chart_color(cols)
    d['col'] = {'c1': c1, 'c2': c2, 'fg': fg, 'tc': tc, 'all': cols}
    worst.append((round(contrast(c1, fg), 2), round(contrast(tc, SURF_LIGHT), 2), round(contrast(tc, SURF_DARK), 2), d['team']))
json.dump(dex, open(__import__('sys').argv[2], 'w'), ensure_ascii=False)
print('lowest band text contrast:', sorted(worst)[:5])
print('lowest chart contrast on light:', sorted(worst, key=lambda w: w[1])[:4])
print('lowest chart contrast on dark:', sorted(worst, key=lambda w: w[2])[:4])
for t in ['Alabama', 'Iowa', 'Missouri', 'Penn State', 'Tennessee', 'Vanderbilt', 'Army', 'North Carolina', 'Oregon']:
    d = next(x for x in dex if x['team'] == t); print(t, d['col'])
