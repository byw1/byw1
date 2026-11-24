"""Build the SVG assets for byw1's GitHub profile README.

    pip install fonttools brotli pillow
    python3 scripts/build-assets.py .        # writes ./assets/*.svg


Every SVG is self-contained (fonts subset + base64, icons inlined) because
GitHub serves README images through its camo proxy as <img>, which can't load
external fonts or images. CSS animations do run there.
"""
import base64, io, json, os, re, sys, html, random, urllib.request
from fontTools import subset
from fontTools.ttLib import TTFont
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(HERE)
FONT_DIR = f"{HERE}/.fonts"  # downloaded on first run, gitignored
os.makedirs(f"{OUT}/assets", exist_ok=True)

FONTS = {
    "P3": "Poppins-Light.ttf",
    "P4": "Poppins-Regular.ttf",
    "P6": "Poppins-SemiBold.ttf",
    "P7": "Poppins-Bold.ttf",
}


PREFIX = [""]

def font_face(fam, text):
    """woff2 subset of one font holding only the glyphs in `text`."""
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern", "liga"]
    opts.name_IDs = []
    opts.notdef_outline = True
    path = f"{FONT_DIR}/{FONTS[fam]}"
    if not os.path.exists(path):
        os.makedirs(FONT_DIR, exist_ok=True)
        urllib.request.urlretrieve(
            f"https://raw.githubusercontent.com/google/fonts/main/ofl/poppins/{FONTS[fam]}", path)
    f = TTFont(path)
    s = subset.Subsetter(opts)
    s.populate(text=text + " ")
    s.subset(f)
    buf = io.BytesIO()
    f.flavor = "woff2"
    f.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"@font-face{{font-family:{PREFIX[0]}{fam};src:url(data:font/woff2;base64,{b64}) format('woff2');font-display:swap;}}"


def fonts_css(uses):
    """uses: {fam: text}"""
    return "".join(font_face(k, v) for k, v in uses.items() if v)


def icon_b64(name, size=112):
    im = Image.open(f"{HERE}/icons/{name}.png").convert("RGBA")
    im = im.resize((size, size), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode()


def esc(s):
    return html.escape(s, quote=True)


# Signature paths, traced for bywilliaml.com (src/components/ui/signature-intro.tsx).
SIG = json.load(open(f"{HERE}/signature.json"))
assert len(SIG) == 2, SIG

# ---------------------------------------------------------------- banner
# Just the signature drawing itself on black.
W, H = 1200, 360
SIG_SCALE = 0.72
sig_tx = W / 2 - (86 + (876 - 86) / 2) * SIG_SCALE
sig_ty = H / 2 - (52 + (337 - 52) / 2) * SIG_SCALE
stroke1_dur, stroke2_dur, lift = 2.6, 0.9, 0.12
banner = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t">
<title id="t">William Lee's signature</title>
<defs>
<style>
.sig path{{fill:none;stroke:#fff;stroke-width:7.5;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:1}}
.s1{{animation:draw {stroke1_dur}s cubic-bezier(.45,.05,.35,.95) .4s forwards}}
.s2{{animation:draw {stroke2_dur}s cubic-bezier(.45,.05,.35,.95) {0.4 + stroke1_dur + lift:.2f}s forwards}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}
@media (prefers-reduced-motion:reduce){{.sig path{{animation:none;stroke-dashoffset:0}}}}
</style>
</defs>
<rect width="{W}" height="{H}" rx="28" fill="#000"/>
<g class="sig" transform="translate({sig_tx:.1f} {sig_ty:.1f}) scale({SIG_SCALE})">
 <path class="s1" pathLength="1" d="{SIG[0]}"/>
 <path class="s2" pathLength="1" d="{SIG[1]}"/>
</g>
</svg>"""
open(f"{OUT}/assets/banner.svg", "w").write(banner)

# ---------------------------------------------------------------- project cards
PROJECTS = [
    dict(slug="hired", name="Hired", status="live", live=True,
         tagline=["The ATS for applicants. Theirs keeps", "a record on you; this one keeps theirs."],
         accent=("#e4e4e7", "#71717a"), tags=["web", "open source"]),
    dict(slug="recruited", name="Recruited", status="live", live=True,
         tagline=["Post one role to every job board, split-test", "it, and see which brings people worth hiring."],
         accent=("#e7dcc8", "#b08d57"), tags=["web", "open source"]),
    dict(slug="comms", name="Comms", status="live", live=True,
         tagline=["A shared team inbox for iMessage,", "with a help desk built in."],
         accent=("#60a5fa", "#818cf8"), tags=["web", "open source"]),
    dict(slug="charades", name="Charades", status="iPhone · soon", live=False,
         tagline=["A forehead-card party game where you", "make your own decks. Offline, no ads."],
         accent=("#9B5CFF", "#FFE500"), tags=["iOS", "open source"]),
    dict(slug="imposter", name="Imposter", status="iPhone · soon", live=False,
         tagline=["Everyone knows the secret word,", "except one of you. Offline, no ads."],
         accent=("#FF4560", "#C8FF2E"), tags=["iOS", "open source"]),
]
CW, CH = 600, 250
for i, p in enumerate(PROJECTS):
    a0, a1 = p["accent"]
    num = f"0{i+1}"
    text4 = "".join(p["tagline"]) + "".join(p["tags"]) + p["status"] + "↗"
    css = fonts_css({"P7": p["name"], "P3": "".join(p["tagline"]), "P4": "".join(p["tags"]) + p["status"]})
    pill_w = 22 + len(p["status"]) * 7.6 + 16
    pill_color = "#4ade80" if p["live"] else "#fbbf24"
    tag_svg, tx = "", 0
    for t in p["tags"]:
        w = 20 + len(t) * 7.3
        tag_svg += f'<g transform="translate({tx} 0)"><rect width="{w:.0f}" height="26" rx="13" fill="#fff" fill-opacity=".05" stroke="#fff" stroke-opacity=".1"/><text x="{w/2:.1f}" y="17.5" text-anchor="middle" class="tg">{t}</text></g>'
        tx += w + 8
    card = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{CW}" height="{CH}" viewBox="0 0 {CW} {CH}" role="img" aria-labelledby="t">
<title id="t">{p['name']}: {esc(' '.join(p['tagline']))}</title>
<defs>
<style>
{css}
.nm{{font-family:P7,sans-serif;font-size:30px;fill:#fff;letter-spacing:-.5px}}
.tl{{font-family:P3,sans-serif;font-size:16.5px;fill:#a1a1aa}}
.tg{{font-family:P4,sans-serif;font-size:12px;fill:#a1a1aa}}
.ps{{font-family:P4,sans-serif;font-size:12.5px;fill:#e4e4e7}}
.num{{font-family:P7,sans-serif;font-size:120px;fill:url(#numg);opacity:.16;letter-spacing:-6px}}
.orbit{{animation:spin 7s linear infinite;transform-origin:{CW/2}px {CH/2}px}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
.float{{animation:fl 5.5s ease-in-out infinite}}
@keyframes fl{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-6px)}}}}
.dot{{animation:pulse 2s ease-in-out infinite}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.35}}}}
@media (prefers-reduced-motion:reduce){{.orbit,.float,.dot{{animation:none}}}}
</style>
<clipPath id="c"><rect width="{CW}" height="{CH}" rx="24"/></clipPath>
<clipPath id="ic"><rect width="96" height="96" rx="22"/></clipPath>
<mask id="ring"><rect width="{CW}" height="{CH}" rx="24" fill="#fff"/><rect x="1.5" y="1.5" width="{CW-3}" height="{CH-3}" rx="22.5" fill="#000"/></mask>
<radialGradient id="glow" cx="18%" cy="0%" r="75%"><stop offset="0" stop-color="{a0}" stop-opacity=".30"/><stop offset="1" stop-color="{a0}" stop-opacity="0"/></radialGradient>
<radialGradient id="glow2" cx="100%" cy="100%" r="60%"><stop offset="0" stop-color="{a1}" stop-opacity=".12"/><stop offset="1" stop-color="{a1}" stop-opacity="0"/></radialGradient>
<linearGradient id="numg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{a0}"/><stop offset="1" stop-color="{a1}"/></linearGradient>
<linearGradient id="beam" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{a0}" stop-opacity="0"/><stop offset=".5" stop-color="{a0}"/><stop offset="1" stop-color="{a1}"/></linearGradient>
</defs>
<g clip-path="url(#c)">
 <rect width="{CW}" height="{CH}" fill="#09090b"/>
 <rect width="{CW}" height="{CH}" fill="url(#glow)"/>
 <rect width="{CW}" height="{CH}" fill="url(#glow2)"/>
</g>
<g mask="url(#ring)">
 <rect width="{CW}" height="{CH}" rx="24" fill="#fff" fill-opacity=".09"/>
 <g class="orbit"><rect x="{CW/2}" y="{CH/2 - 4}" width="{CW}" height="8" fill="url(#beam)" transform="rotate(-20 {CW/2} {CH/2})"/></g>
</g>
<g class="float" transform="translate(32 32)">
 <g transform="translate(32 32)">
  <rect width="96" height="96" rx="22" fill="#000"/>
  <image width="96" height="96" clip-path="url(#ic)" href="data:image/png;base64,{icon_b64(p['slug'])}"/>
  <rect width="96" height="96" rx="22" fill="none" stroke="#fff" stroke-opacity=".14"/>
 </g>
</g>
<g transform="translate({CW - 32 - pill_w:.0f} 36)">
 <rect width="{pill_w:.0f}" height="28" rx="14" fill="#000" fill-opacity=".5" stroke="#fff" stroke-opacity=".12"/>
 <circle class="dot" cx="16" cy="14" r="4" fill="{pill_color}"/>
 <text x="27" y="18.5" class="ps">{esc(p['status'])}</text>
</g>
<text x="176" y="110" class="nm">{p['name']}</text>
<text x="32" y="178" class="tl">{esc(p['tagline'][0])}</text>
<text x="32" y="200" class="tl">{esc(p['tagline'][1])}</text>
<g transform="translate(176 120)">{tag_svg}</g>
</svg>"""
    open(f"{OUT}/assets/project-{p['slug']}.svg", "w").write(card)

# ---------------------------------------------------------------- bookshelf
BOOKS = [
    ("Principles", "Ray Dalio", ("#0d1117", "#1a2332"), "#93c5fd"),
    ("Steve Jobs", "Walter Isaacson", ("#1a1a1a", "#2d1a1a"), "#ffffff"),
    ("Elon Musk", "Walter Isaacson", ("#1a1a2e", "#0d0d1a"), "#c4b5fd"),
    ("Good to Great", "Jim Collins", ("#1a2e1a", "#0d1a0d"), "#6ee7b7"),
    ("The Republic", "Plato", ("#2d2a1a", "#1a1700"), "#fcd34d"),
    ("Your Next Five Moves", "Patrick Bet-David", ("#2d1a1a", "#1a0d0d"), "#fdba74"),
]
BW, BH = 1200, 320
bt = "".join(t + a for t, a, *_ in BOOKS)
spines = ""
x = (1200 - (6*118 + 5*32)) / 2
rnd = random.Random(7)
for i, (title, author, (c0, c1), ink) in enumerate(BOOKS):
    w = 118
    h = rnd.choice([190, 198, 206, 214])
    lean = -4 if i == 3 else 0
    y = 268 - h
    words = title.split()
    lines = [title] if len(title) <= 12 else [" ".join(words[:2]), " ".join(words[2:])]
    tl = "".join(
        f'<text x="{w/2}" y="{52 + k*20}" text-anchor="middle" class="bt" fill="{ink}">{esc(l)}</text>'
        for k, l in enumerate(lines))
    spines += f"""<g class="bk" style="animation-delay:{i*0.12:.2f}s"><g transform="translate({x} {y}) rotate({lean} {w/2} {h})">
 <defs><linearGradient id="b{i}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c0}"/><stop offset="1" stop-color="{c1}"/></linearGradient></defs>
 <rect width="{w}" height="{h}" rx="5" fill="url(#b{i})"/>
 <rect width="{w}" height="{h}" rx="5" fill="url(#sheen)"/>
 <rect x="0" y="0" width="7" height="{h}" rx="3" fill="#000" fill-opacity=".35"/>
 <rect x="16" y="20" width="{w-30}" height="1" fill="{ink}" fill-opacity=".35"/>
 {tl}
 <rect x="16" y="{h-44}" width="{w-30}" height="1" fill="{ink}" fill-opacity=".35"/>
 <text x="{w/2}" y="{h-22}" text-anchor="middle" class="ba" fill="{ink}">{esc(author)}</text>
 <rect width="{w}" height="{h}" rx="5" fill="none" stroke="#fff" stroke-opacity=".1"/>
</g></g>"""
    x += w + 32
shelf = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{BW}" height="{BH}" viewBox="0 0 {BW} {BH}" role="img" aria-labelledby="t">
<title id="t">My favorite reads: {esc(', '.join(f'{t} by {a}' for t, a, *_ in BOOKS))}</title>
<defs>
<style>
{fonts_css({"P6": "".join(t for t, *_ in BOOKS), "P3": "".join(a for _, a, *_ in BOOKS), "P4": "MY FAVORITE READS"})}
.bt{{font-family:P6,sans-serif;font-size:15px}}
.ba{{font-family:P3,sans-serif;font-size:10.5px;opacity:.75}}
.lbl{{font-family:P4,sans-serif;font-size:12px;letter-spacing:4px;fill:#71717a}}
.bk{{opacity:0;animation:up .8s cubic-bezier(.22,1,.36,1) forwards}}
@keyframes up{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:none}}}}
@media (prefers-reduced-motion:reduce){{.bk{{animation:none;opacity:1}}}}
</style>
<clipPath id="c"><rect width="{BW}" height="{BH}" rx="28"/></clipPath>
<linearGradient id="sheen" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".25" stop-color="#fff" stop-opacity=".07"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/></linearGradient>
<radialGradient id="lamp" cx="50%" cy="0%" r="70%"><stop offset="0" stop-color="#f59e0b" stop-opacity=".16"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>
<linearGradient id="wood" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3f2a17"/><stop offset="1" stop-color="#1c1209"/></linearGradient>
</defs>
<g clip-path="url(#c)">
 <rect width="{BW}" height="{BH}" fill="#000"/>
 <rect width="{BW}" height="{BH}" fill="url(#lamp)"/>
 <text x="{BW/2}" y="38" text-anchor="middle" class="lbl">MY FAVORITE READS</text>
 {spines}
 <rect x="110" y="268" width="{BW-220}" height="14" rx="3" fill="url(#wood)"/>
 <rect x="110" y="282" width="{BW-220}" height="20" fill="#000" fill-opacity=".6"/>
 <ellipse cx="{BW/2}" cy="290" rx="{BW/2-120}" ry="8" fill="#000" fill-opacity=".8"/>
</g>
<rect x=".75" y=".75" width="{BW-1.5}" height="{BH-1.5}" rx="27.5" fill="none" stroke="#fff" stroke-opacity=".1" stroke-width="1.5"/>
</svg>"""
open(f"{OUT}/assets/bookshelf.svg", "w").write(shelf)


for f in sorted(os.listdir(f"{OUT}/assets")):
    print(f, os.path.getsize(f"{OUT}/assets/{f}"))

# Chrome shares a font cache across SVG images on one page, keyed by family
# name, so two SVGs with different subsets under "P7" can steal each other's
# glyphs. Give every file its own family names.
for f in sorted(os.listdir(f"{OUT}/assets")):
    p = f"{OUT}/assets/{f}"
    slug = re.sub(r"[^a-z]", "", f.replace(".svg", ""))
    s = open(p).read()
    s = re.sub(r"font-family:(P\d)", lambda m: f"font-family:{slug}{m.group(1)}", s)
    open(p, "w").write(s)
