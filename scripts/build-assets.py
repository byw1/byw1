"""Build the SVG assets for byw1's GitHub profile README.

Every SVG is self-contained (fonts subset + base64, icons inlined) because
GitHub serves README images through its camo proxy as <img>, which can't load
external fonts or images. CSS animations do run there.
"""
import base64, io, os, sys, html
from fontTools import subset
from fontTools.ttLib import TTFont
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = "/home/user/bywilliaml.com"
OUT = sys.argv[1]
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
    f = TTFont(f"{HERE}/fonts/{FONTS[fam]}")
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
    im = Image.open(f"{SITE}/public/projects/{name}.png").convert("RGBA")
    im = im.resize((size, size), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode()


def esc(s):
    return html.escape(s, quote=True)


# Signature paths, straight from src/components/ui/signature-intro.tsx.
sig_src = open(f"{SITE}/src/components/ui/signature-intro.tsx").read()
import re
SIG = re.findall(r"'(M [^']+)'", sig_src)
assert len(SIG) == 2, SIG

# ---------------------------------------------------------------- banner
W, H = 1200, 440
eyebrow = "WILLIAM LEE  ·  LOS ANGELES"
tag = "Operator who builds the tools that make businesses faster."
status = "code maxxing"
handle = "@bywilliaml"

# Seeded starfield so rebuilds are stable.
import random
rnd = random.Random(33)
stars = []
for i in range(70):
    x, y = rnd.uniform(16, W - 16), rnd.uniform(16, H - 16)
    r = rnd.choice([0.6, 0.8, 1.0, 1.3])
    d = rnd.uniform(0, 6)
    dur = rnd.uniform(3, 7)
    stars.append(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" class="st" style="animation-duration:{dur:.1f}s;animation-delay:-{d:.1f}s"/>'
    )

# Signature coordinate box is roughly x 86..876, y 52..337. Centre it.
SIG_SCALE = 0.62
sig_w = (876 - 86) * SIG_SCALE
sig_tx = W / 2 - (86 + (876 - 86) / 2) * SIG_SCALE
sig_ty = 34 - 52 * SIG_SCALE + 6

stroke1_dur, stroke2_dur, lift = 2.6, 0.9, 0.12

banner = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
<title id="t">William Lee</title>
<desc id="d">William Lee's signature drawing itself over a night sky. {esc(tag)} Status: {status}.</desc>
<defs>
<style>
{fonts_css({"P3": tag + eyebrow, "P4": status + handle + "bywilliaml.com", "P6": eyebrow})}
.st{{fill:#fff;opacity:.15;animation:tw ease-in-out infinite}}
@keyframes tw{{0%,100%{{opacity:.08}}50%{{opacity:.55}}}}
.sig path{{fill:none;stroke:url(#ink);stroke-width:7.5;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:1}}
.s1{{animation:draw {stroke1_dur}s cubic-bezier(.45,.05,.35,.95) .4s forwards}}
.s2{{animation:draw {stroke2_dur}s cubic-bezier(.45,.05,.35,.95) {0.4 + stroke1_dur + lift:.2f}s forwards}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}
.rise{{opacity:0;transform:translateY(10px);animation:rise .9s cubic-bezier(.22,1,.36,1) forwards}}
@keyframes rise{{to{{opacity:1;transform:none}}}}
.glow{{animation:breathe 9s ease-in-out infinite;transform-origin:600px 0}}
@keyframes breathe{{0%,100%{{opacity:.85;transform:scale(1)}}50%{{opacity:1;transform:scale(1.08)}}}}
.dot{{animation:pulse 2s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.35}}}}
.ring{{animation:ring 2s ease-out infinite;transform-box:fill-box;transform-origin:center}}
@keyframes ring{{0%{{opacity:.6;transform:scale(1)}}100%{{opacity:0;transform:scale(2.6)}}}}
.t-eyebrow{{font-family:P6,sans-serif;font-size:13px;letter-spacing:4.5px;fill:#a1a1aa}}
.t-tag{{font-family:P3,sans-serif;font-size:25px;fill:#e4e4e7}}
.t-pill{{font-family:P4,sans-serif;font-size:14px;fill:#d4d4d8}}
@media (prefers-reduced-motion:reduce){{
 .sig path{{animation:none;stroke-dashoffset:0}}
 .rise{{animation:none;opacity:1;transform:none}}
 .st,.glow,.dot,.ring{{animation:none}}
}}
</style>
<clipPath id="card"><rect width="{W}" height="{H}" rx="28"/></clipPath>
<radialGradient id="g1" cx="50%" cy="0%" r="62%">
 <stop offset="0" stop-color="#8b5cf6" stop-opacity=".42"/>
 <stop offset=".55" stop-color="#6366f1" stop-opacity=".08"/>
 <stop offset="1" stop-color="#000" stop-opacity="0"/>
</radialGradient>
<radialGradient id="g2" cx="92%" cy="105%" r="45%">
 <stop offset="0" stop-color="#c084fc" stop-opacity=".18"/>
 <stop offset="1" stop-color="#000" stop-opacity="0"/>
</radialGradient>
<radialGradient id="g3" cx="6%" cy="100%" r="40%">
 <stop offset="0" stop-color="#60a5fa" stop-opacity=".12"/>
 <stop offset="1" stop-color="#000" stop-opacity="0"/>
</radialGradient>
<linearGradient id="ink" gradientUnits="userSpaceOnUse" x1="86" y1="0" x2="876" y2="0">
 <stop offset="0" stop-color="#ffffff"/>
 <stop offset=".6" stop-color="#f5f3ff"/>
 <stop offset="1" stop-color="#c4b5fd"/>
</linearGradient>
<pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">
 <circle cx="1" cy="1" r="1" fill="#fff" fill-opacity=".07"/>
</pattern>
<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="#fff" stop-opacity=".9"/>
 <stop offset="1" stop-color="#fff" stop-opacity="0"/>
</linearGradient>
<mask id="gridmask"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>
<filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="6"/></filter>
<linearGradient id="edge" x1="0" y1="0" x2="1" y2="1">
 <stop offset="0" stop-color="#fff" stop-opacity=".22"/>
 <stop offset=".5" stop-color="#fff" stop-opacity=".04"/>
 <stop offset="1" stop-color="#a78bfa" stop-opacity=".25"/>
</linearGradient>
</defs>
<g clip-path="url(#card)">
 <rect width="{W}" height="{H}" fill="#000"/>
 <rect width="{W}" height="{H}" fill="url(#grid)" mask="url(#gridmask)"/>
 <rect class="glow" width="{W}" height="{H}" fill="url(#g1)"/>
 <rect width="{W}" height="{H}" fill="url(#g2)"/>
 <rect width="{W}" height="{H}" fill="url(#g3)"/>
 {''.join(stars)}
 <g transform="translate({sig_tx:.1f} {sig_ty:.1f}) scale({SIG_SCALE})">
  <g class="sig" opacity=".35" filter="url(#soft)">
   <path class="s1" pathLength="1" d="{SIG[0]}"/>
   <path class="s2" pathLength="1" d="{SIG[1]}"/>
  </g>
  <g class="sig">
   <path class="s1" pathLength="1" d="{SIG[0]}"/>
   <path class="s2" pathLength="1" d="{SIG[1]}"/>
  </g>
 </g>
 <g class="rise" style="animation-delay:3.6s">
  <text x="{W/2}" y="296" text-anchor="middle" class="t-eyebrow">{esc(eyebrow)}</text>
 </g>
 <g class="rise" style="animation-delay:3.85s">
  <text x="{W/2}" y="340" text-anchor="middle" class="t-tag">{esc(tag)}</text>
 </g>
 <g class="rise" style="animation-delay:4.1s">
  <g transform="translate({W/2 - 175} 368)">
   <rect width="160" height="34" rx="17" fill="#fff" fill-opacity=".06" stroke="#fff" stroke-opacity=".12"/>
   <circle class="ring" cx="22" cy="17" r="4.5" fill="none" stroke="#4ade80" stroke-width="1.5"/>
   <circle class="dot" cx="22" cy="17" r="4.5" fill="#4ade80"/>
   <text x="36" y="22" class="t-pill">{status}</text>
  </g>
  <g transform="translate({W/2 + 15} 368)">
   <rect width="160" height="34" rx="17" fill="#fff" fill-opacity=".06" stroke="#fff" stroke-opacity=".12"/>
   <text x="80" y="22" text-anchor="middle" class="t-pill">{handle}</text>
  </g>
 </g>
</g>
<rect x=".75" y=".75" width="{W-1.5}" height="{H-1.5}" rx="27.5" fill="none" stroke="url(#edge)" stroke-width="1.5"/>
</svg>"""
open(f"{OUT}/assets/banner.svg", "w").write(banner)

# ---------------------------------------------------------------- project cards
PROJECTS = [
    dict(slug="charades", name="Charades", status="iPhone · soon", live=False,
         tagline=["A forehead-card party game where you", "make your own decks. Offline, no ads."],
         accent=("#9B5CFF", "#FFE500"), tags=["iOS", "open source"]),
    dict(slug="imposter", name="Imposter", status="iPhone · soon", live=False,
         tagline=["Everyone knows the secret word,", "except one of you. Offline, no ads."],
         accent=("#FF4560", "#C8FF2E"), tags=["iOS", "open source"]),
    dict(slug="hired", name="Hired", status="live", live=True,
         tagline=["The ATS for applicants. Theirs keeps", "a record on you; this one keeps theirs."],
         accent=("#e4e4e7", "#71717a"), tags=["web", "open source"]),
    dict(slug="comms", name="Comms", status="live", live=True,
         tagline=["A shared team inbox for iMessage,", "with a help desk built in."],
         accent=("#60a5fa", "#818cf8"), tags=["web", "open source"]),
]
CW, CH = 600, 250
for i, p in enumerate(PROJECTS):
    a0, a1 = p["accent"]
    num = f"0{i+1}"
    text4 = "".join(p["tagline"]) + "".join(p["tags"]) + p["status"] + "↗"
    css = fonts_css({"P7": p["name"] + num, "P3": "".join(p["tagline"]), "P4": "".join(p["tags"]) + p["status"]})
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
 <text x="{CW-20}" y="{CH-14}" text-anchor="end" class="num">{num}</text>
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
<title id="t">On the shelf: {esc(', '.join(f'{t} by {a}' for t, a, *_ in BOOKS))}</title>
<defs>
<style>
{fonts_css({"P6": "".join(t for t, *_ in BOOKS), "P3": "".join(a for _, a, *_ in BOOKS), "P4": "ON THE SHELF"})}
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
 <text x="{BW/2}" y="38" text-anchor="middle" class="lbl">ON THE SHELF</text>
 {spines}
 <rect x="110" y="268" width="{BW-220}" height="14" rx="3" fill="url(#wood)"/>
 <rect x="110" y="282" width="{BW-220}" height="20" fill="#000" fill-opacity=".6"/>
 <ellipse cx="{BW/2}" cy="290" rx="{BW/2-120}" ry="8" fill="#000" fill-opacity=".8"/>
</g>
<rect x=".75" y=".75" width="{BW-1.5}" height="{BH-1.5}" rx="27.5" fill="none" stroke="#fff" stroke-opacity=".1" stroke-width="1.5"/>
</svg>"""
open(f"{OUT}/assets/bookshelf.svg", "w").write(shelf)

# ---------------------------------------------------------------- footer
FW, FH = 1200, 170
fs = 0.26
foot = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{FW}" height="{FH}" viewBox="0 0 {FW} {FH}" role="img" aria-labelledby="t">
<title id="t">Thanks for stopping by. bywilliaml.com</title>
<defs>
<style>
{fonts_css({"P3": "thanks for stopping by", "P4": "bywilliaml.com"})}
.sig path{{fill:none;stroke:#8b5cf6;stroke-width:9;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:1;animation:draw 2.2s cubic-bezier(.45,.05,.35,.95) .3s forwards}}
.sig .s2{{animation-duration:.8s;animation-delay:2.6s}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}
.a{{font-family:P3,sans-serif;font-size:15px;fill:#71717a;letter-spacing:1px}}
.b{{font-family:P4,sans-serif;font-size:15px;fill:#a78bfa;letter-spacing:1px}}
@media (prefers-reduced-motion:reduce){{.sig path{{animation:none;stroke-dashoffset:0}}}}
</style>
<linearGradient id="hr" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#a78bfa" stop-opacity="0"/><stop offset=".5" stop-color="#a78bfa" stop-opacity=".6"/><stop offset="1" stop-color="#a78bfa" stop-opacity="0"/></linearGradient>
</defs>
<rect x="300" y="4" width="600" height="1" fill="url(#hr)"/>
<g class="sig" transform="translate({FW/2 - 481*fs:.1f} {28 - 52*fs:.1f}) scale({fs})">
 <path class="s1" pathLength="1" d="{SIG[0]}"/>
 <path class="s2" pathLength="1" d="{SIG[1]}"/>
</g>
<text x="{FW/2}" y="136" text-anchor="middle"><tspan class="a">thanks for stopping by  ·  </tspan><tspan class="b">bywilliaml.com</tspan></text>
</svg>"""
open(f"{OUT}/assets/footer.svg", "w").write(foot)

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
