#!/usr/bin/env python3
"""Static site generator for the Alan T. Tran, M.D. website.

Reads content/site.json + content/pages.json and writes a complete site to public/.
No third-party packages needed (Python 3.8+).

Usage:  python3 build/build.py [--domain example.com]
        (SITE_DOMAIN in the environment also works)
"""
import html, json, os, re, shutil, sys, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public"
SRC = ROOT / "src"
site = json.loads((ROOT / "content/site.json").read_text())
pages = json.loads((ROOT / "content/pages.json").read_text())

domain = os.environ.get("SITE_DOMAIN", "")
if "--domain" in sys.argv:
    domain = sys.argv[sys.argv.index("--domain") + 1]
domain = domain or "alantran-plastic-surgery.com"
BASE = f"https://{domain}"
YEAR = datetime.date.today().year
IMAGE_VERSIONS = {"dr-alan-tran-practice-hero": "20261013"}

e = lambda s: html.escape(s or "", quote=True)

def img_url(name):
    url = f"/assets/img/{name}.webp"
    version = IMAGE_VERSIONS.get(name)
    return f"{url}?v={version}" if version else url

SERVICES = {}
for slug, p in pages.items():
    if p["kind"] == "service":
        SERVICES.setdefault(p["category"], []).append((slug, p["name"]))
CAT_ORDER = ["Breast", "Body", "Skin", "Face"]

# ---------------------------------------------------------------- layout
def logo(cls="", include_mark=False):
    mark = ('<img class="logo-mark" src="/assets/img/alan-tran-mark.png" '
            'alt="" width="79" height="90">' if include_mark else "")
    return (f'<a class="logo {cls}" href="/" aria-label="{e(site["practice_name"])} home">'
            f'{mark}<span class="logo-copy">'
            f'<span class="logo-name">{e(site["logo_name"])}</span>'
            f'<span class="logo-sub">{e(site["logo_sub"])}</span></span></a>')

def nav(active):
    mega = "".join(
        f'<div class="mega-col"><p class="mega-title">{c}</p><ul>' +
        "".join(f'<li><a href="/services/{s}/">{e(n)}</a></li>' for s, n in SERVICES[c]) +
        "</ul></div>" for c in CAT_ORDER)
    def a(href, label, key):
        cur = ' aria-current="page"' if active == key else ""
        return f'<a href="{href}"{cur}>{label}</a>'
    return f"""
<nav class="main-nav" id="main-nav" aria-label="Main">
  <ul class="nav-list">
    <li>{a('/', 'Home', 'home')}</li>
    <li class="has-sub">{a('/about/', 'About', 'about')}<button class="sub-toggle" aria-label="Show About menu" aria-expanded="false"></button>
      <ul class="sub">
        <li><a href="/tour-the-office/">Tour the Office</a></li>
        <li><a href="/meet-the-doctor/">Meet the Doctor</a></li>
      </ul></li>
    <li class="has-sub has-mega">{a('/services/', 'Services', 'services')}<button class="sub-toggle" aria-label="Show Services menu" aria-expanded="false"></button>
      <div class="sub mega">{mega}</div></li>
    <li>{a('/gallery/', 'Gallery', 'gallery')}</li>
    <li>{a('/testimonials/', 'Testimonials', 'testimonials')}</li>
    <li>{a('/specials/', 'Specials', 'specials')}</li>
    <li>{a('/contact/', 'Contact', 'contact')}</li>
  </ul>
</nav>"""

def header(active):
    return f"""
<a class="skip" href="#main">Skip to content</a>
<header class="site-header"><div class="wrap header-inner">
  {logo(include_mark=True)}
  <button class="nav-toggle" aria-controls="main-nav" aria-expanded="false"><span></span><span></span><span></span><span class="sr">Menu</span></button>
  {nav(active)}
  <div class="header-contact" aria-label="Practice contact information">
    <a class="header-contact-link header-address" href="https://www.google.com/maps/search/?api=1&amp;query=17931%20Euclid%20St%2C%20Fountain%20Valley%2C%20CA%2092708" target="_blank" rel="noopener" aria-label="Directions to {e(site['address_line'])}, {e(site['city'])}, {e(site['state'])} {e(site['zip'])}">
      <span class="header-contact-icon"><svg aria-hidden="true" viewBox="0 0 24 24"><path d="M12 2a7 7 0 0 0-7 7c0 5.25 7 13 7 13s7-7.75 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5z"/></svg></span>
      <span class="header-contact-text">{e(site['address_line'])}<small>{e(site['city'])}, {e(site['state'])} {e(site['zip'])}</small></span>
    </a>
    <a class="header-contact-link" href="tel:{site['phone_e164']}" aria-label="Call {e(site['phone'])}">
      <span class="header-contact-icon"><svg aria-hidden="true" viewBox="0 0 24 24"><path d="M6.6 10.8a15.5 15.5 0 0 0 6.6 6.6l2.2-2.2c.3-.3.7-.4 1.1-.2 1.2.4 2.4.6 3.7.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1C10.7 21 3 13.3 3 3.8c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.7.1.4 0 .8-.2 1.1l-2.3 2.2z"/></svg></span>
      <span class="header-contact-text">{e(site['phone'])}<small>Call the office</small></span>
    </a>
  </div>
  <a class="btn header-cta" href="/contact/">Request a Consultation</a>
</div></header>"""

def footer():
    social = ""
    if site.get("instagram"):
        social += f'<a href="{e(site["instagram"])}" target="_blank" rel="noopener" aria-label="Instagram"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 7a5 5 0 1 0 0 10 5 5 0 0 0 0-10zm0 8.2a3.2 3.2 0 1 1 0-6.4 3.2 3.2 0 0 1 0 6.4zM17.3 5.5a1.2 1.2 0 1 0 0 2.4 1.2 1.2 0 0 0 0-2.4zM21.9 7.1c-.1-1.6-.4-3-1.6-4.2S17.6 1.3 16 1.2C14.3 1.1 9.7 1.1 8 1.2c-1.6.1-3 .4-4.2 1.6S2.2 5.5 2.1 7.1C2 8.8 2 13.4 2.1 15.1c.1 1.6.4 3 1.6 4.2s2.6 1.5 4.2 1.6c1.7.1 6.3.1 8 0 1.6-.1 3-.4 4.2-1.6s1.5-2.6 1.6-4.2c.1-1.7.1-6.3.2-8z"/></svg></a>'
    if site.get("yelp"):
        social += f'<a href="{e(site["yelp"])}" target="_blank" rel="noopener" aria-label="Yelp"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12.3 2.1c-.6-.2-4.4.9-5 1.3-.4.3-.5.7-.4 1.1l3.9 6.9c.6 1 2 .6 2-.6V3c0-.5-.2-.8-.5-.9zm-1.6 11.6-6.2 1.6c-.6.2-.8.5-.8 1 0 .8.7 3.3 1.3 4 .3.3.7.4 1.1.3l5-4.3c.9-.8.4-2.2-.4-2.6zm1.9 1.9c-.6-.9-2-.5-2 .6l.3 5.9c0 .4.3.8.7.9.7.2 3.5-.3 4.2-.8.3-.2.5-.6.3-1l-3.5-5.6zm7.9-.7-5.6-2.2c-1-.4-2 .7-1.4 1.6l3.3 4.9c.2.4.6.5 1 .4.7-.3 2.6-2.4 2.9-3.2.1-.6 0-1.3-.2-1.5zm-.4-5.4c-.4-.8-2.6-2.7-3.3-2.9-.4-.1-.8 0-1 .4L12.5 12c-.6.9.3 2.1 1.4 1.7l5.8-1.9c.4-.1.6-.5.6-.9 0-.4-.1-.9-.2-1.4z"/></svg></a>'
    return f"""
<footer class="site-footer">
  <div class="wrap footer-grid">
    <div class="footer-nav">
      <ul class="f-links">
        <li><a href="/">Home</a></li><li><a href="/about/">About</a></li><li><a href="/services/">Services</a></li>
        <li><a href="/gallery/">Gallery</a></li><li><a href="/testimonials/">Testimonials</a></li><li><a href="/specials/">Specials</a></li><li><a href="/contact/">Contact</a></li>
      </ul>
    </div>
    <div class="footer-identity" aria-label="Alan T. Tran, M.D. professional credentials">
      <p class="footer-name">Alan T. Tran, M.D.</p>
      <img class="footer-mark" src="/assets/img/alan-tran-mark.png" alt="Alan T. Tran monogram" width="79" height="90" loading="lazy">
      <div class="footer-credentials-crop credential-art">
        <img src="/assets/img/plastic-surgery-credentials.jpg" alt="Board certification and professional membership emblems" width="550" height="269" loading="lazy">
      </div>
    </div>
    <div class="footer-office">
      <p class="f-title">Office Info</p>
      <address>{e(site['address_line'])}<br>{e(site['city'])}, {e(site['state'])} {e(site['zip'])}<br>
      <a href="tel:{site['phone_e164']}">{e(site['phone'])}</a><br><a href="mailto:{e(site['email'])}">{e(site['email'])}</a></address>
      <p class="footer-hours"><strong>Mon-Fri:</strong> 10:00 AM-6:00 PM</p>
      <div class="social">{social}</div>
    </div>
  </div>
  <div class="wrap footer-bottom">
    <span>© {YEAR} {e(site['legal_name'])} All rights reserved.</span>
    <a href="/privacy-policy/">Privacy Policy</a>
  </div>
</footer>"""

def page(path, title, desc, body, active="", og_img="dr-alan-tran-practice-hero", jsonld=""):
    full_title = title if "Alan" in title else f"{title} | {site['practice_name']}"
    canonical = BASE + path
    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{BASE}{img_url(og_img)}">
<meta name="theme-color" content="#B3155A">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400&family=Old+Standard+TT:ital,wght@0,400;0,700;1,400&family=Fraunces:ital,opsz,wght@0,9..144,300..700;1,9..144,300..600&family=Montserrat:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/site.css?v={VERSION}">
{jsonld}
</head>
<body>
{header(active)}
<main id="main">
{body}
</main>
{footer()}
<script src="/assets/js/site.js?v={VERSION}" defer></script>
</body>
</html>
"""
    dest = OUT / path.strip("/") / "index.html" if path != "/" else OUT / "index.html"
    if path.endswith(".html"):
        dest = OUT / path.strip("/")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(doc)
    if path.endswith("/") and path not in SITEMAP:
        SITEMAP.append(path)

SITEMAP = []
VERSION = datetime.datetime.now().strftime("%Y%m%d%H%M")

# ---------------------------------------------------------------- building blocks
def render_blocks(blocks):
    out = []
    for b in blocks:
        t = b["t"]
        if t in ("ul", "ol"):
            out.append(f"<{t}>" + "".join(f"<li>{e(i)}</li>" for i in b["items"]) + f"</{t}>")
        elif t == "img":
            continue
        elif t == "h1":
            out.append(f"<h2>{e(b['x'])}</h2>")
        else:
            out.append(f"<{t}>{e(b['x'])}</{t}>")
    return "\n".join(out)

def cta_band():
    return f"""
<section class="band band-cta"><div class="wrap band-inner">
  <div><p class="eyebrow eyebrow-light">Begin Your Journey</p><h2>Schedule a Consultation</h2></div>
  <div class="band-actions"><a class="btn btn-white" href="/contact/">Contact Us</a><a class="btn btn-outline-light" href="tel:{site['phone_e164']}">{e(site['phone'])}</a></div>
</div></section>"""

def doctor_band(name):
    return f"""
<section class="doctor-band"><div class="wrap doctor-band-inner">
  <img src="{img_url('dr-alan-tran-office-portrait')}" alt="Dr. Alan T. Tran" loading="lazy" width="520" height="520">
  <div><p class="eyebrow">Dr. Alan T. Tran</p><h2>{e(name)} in Fountain Valley, California</h2>
  <p>Board-certified plastic and reconstructive surgeon, serving Orange County since 2000. You will spend quality time with Dr. Tran himself at every visit.</p>
  <a class="btn btn-pink" href="/meet-the-doctor/">Meet Dr. Tran</a></div>
</div></section>"""

def ready_band():
    return f"""
<section class="ready"><div class="wrap ready-inner">
  <p class="eyebrow">Ready when you are</p>
  <h2>Look your best, naturally<sup class="service-mark">℠</sup></h2>
  <div class="ready-actions"><a class="btn btn-pink" href="tel:{site['phone_e164']}">{e(site['phone'])}</a><a class="btn btn-outline" href="mailto:{e(site['email'])}">Email the office</a></div>
</div></section>"""

def page_hero(title, sub="", image=None, eyebrow=""):
    style = f' style="background-image:url(\'{img_url(image)}\')"' if image else ""
    cls = "page-hero has-img" if image else "page-hero"
    return f"""<section class="{cls}"{style}><div class="wrap">
  {f'<p class="eyebrow eyebrow-light">{e(eyebrow)}</p>' if eyebrow else ''}<h1>{e(title)}</h1>{f'<p class="lede">{e(sub)}</p>' if sub else ''}
</div></section>"""

# ---------------------------------------------------------------- service pages
def build_service(slug, p):
    secs = []
    for i, bl in enumerate(p["sections"]):
        imgs = [b for b in bl if b["t"] == "img"]
        inner = render_blocks(bl)
        alt = " alt-bg" if i % 2 else ""
        if imgs:
            im = imgs[0]
            side = "img-left" if i % 2 else "img-right"
            secs.append(f'<section class="svc-sec{alt}"><div class="wrap svc-split {side}"><div class="prose">{inner}</div>'
                        f'<figure><img src="{img_url(im["src"])}" alt="{e(im["alt"] or p["name"])}" loading="lazy"></figure></div></section>')
        else:
            secs.append(f'<section class="svc-sec{alt}"><div class="wrap prose prose-narrow">{inner}</div></section>')
    # Doctor banner + CTA after the 3rd content block (matches original order)
    insert_at = min(3, len(secs))
    secs.insert(insert_at, doctor_band(p["name"]) + cta_band())
    related = [(s, n) for s, n in SERVICES[p["category"]] if s != slug]
    rel = "".join(f'<li><a href="/services/{s}/">{e(n)}</a></li>' for s, n in related)
    body = page_hero(p["name"], "", p.get("hero_img"), eyebrow=f'{p["category"]} Procedures') + "\n".join(secs) + f"""
<section class="closing"><div class="wrap"><h3>{e(p['closing'])}</h3></div></section>
<section class="related"><div class="wrap"><p class="eyebrow">More {e(p['category'].lower())} procedures</p><ul class="pill-list">{rel}</ul></div></section>
{ready_band()}"""
    page(f"/services/{slug}/", p["title"], p["description"], body, "services", og_img=p.get("hero_img") or "dr-alan-tran-office-portrait")

# ---------------------------------------------------------------- home
TESTIMONIALS = [
 "You think the best Dr. for nose jobs is in Hollywood or Newport Beach?! Nope! Alan Tran knocks around in the medical underground in Westminster. By far a superb and meticulous Dr. He takes his time and ensures everything is and will be correct w/ your nose. Staff was an 11 out of 10. Dr. Tran is concise w/ how he will proceed w/ the surgery and how he will ensure he will make everything better to the best of his ability. Dr. Tran goes about his occupation like art, pristine, will take his time, and will fix your structural being in Chanel glasses and Gucci flip flops. I am extremely pleased w/ the end result and would recommend Dr. Tran to anyone looking to fix their nose.",
 "Dr. Tran is an amazing surgeon. His attention to detail and making sure his patients are satisfied with the results is what makes him and his office successful. He does amazing breast reconstruction and cosmetic surgery. He takes the time to explain all of the options and his reasoning for choosing his products of choice for your specific needs.",
 "Dr. Alan T Tran is a very good surgeon! He is so good and I am proud of him. He did my surgery and it was absolutely good. He was the best surgeon in the world. I like him being my surgeon! Thank you very much for doing my surgery!",
 "I was very happy with my care. You really took the time to explain everything and let me know exactly what would happen. I am elated with the results and would recommend you to anyone in a heartbeat. Thanks for the great support and care. It is rare to find a doctor that cares so much about the patient and not the money.",
 "Dr. Tran is great! I’m amazed with his work. I can’t get over how meticulous he is. He is such a sweet, caring, and easy-going surgeon. He doesn’t rush you out the office to take another patient in. Every visit I had his undivided attention. He explained everything in detail. And if I asked the same question twice, no biggie. Great person and MD!",
]

def build_home():
    s = site
    tiles = [("Body", "body-contouring-procedures", "/services/#body"),
             ("Breast", "breast-surgery-procedures", "/services/#breast"),
             ("Skin", "skin-treatment-procedures", "/services/#skin"),
             ("Face", "facial-plastic-surgery-procedures", "/services/#face")]
    tiles_html = "".join(
        f'<button class="tile{" is-active" if n == 0 else ""}" type="button" data-service-tile="{t.lower()}" '
        f'aria-controls="tile-panel-{t.lower()}" aria-expanded="{"true" if n == 0 else "false"}">'
        f'<img src="{img_url(i)}" alt="{t} procedures" loading="lazy"><span>{e(t)}</span></button>'
        for n, (t, i, h) in enumerate(tiles))
    tile_panels = "".join(
        f'<div class="tile-panel{" is-active" if n == 0 else ""}" id="tile-panel-{c.lower()}" data-service-panel="{c.lower()}">'
        f'<h3>{e(c)} Procedures</h3><ul>' +
        "".join(f'<li><a href="/services/{slug}/">{e(name)}</a></li>' for slug, name in SERVICES[c]) +
        f'</ul><a class="tile-all" href="/services/#{c.lower()}">View all {e(c.lower())} procedures</a></div>'
        for n, c in enumerate(["Body", "Breast", "Skin", "Face"]))
    points = [("Over two decades in Fountain Valley", "Practicing continuously since 2000, refining one philosophy: natural over “done.”"),
              ("Direct time with Dr. Tran", "Consultations are spent with Dr. Tran himself, not handed off to a coordinator."),
              ("A full spectrum of care", "From rhinoplasty and breast augmentation to breast, nose, and post skin cancer reconstruction."),
              ("Board-certified plastic surgeon", "Certified by the American Board of Plastic Surgery, with more than two decades of practice in Orange County."),
              ("Your goals set the plan", "The procedure is chosen to fit you, never the other way around.")]
    points_html = "".join(f'<li><span class="pnum">{i+1:02d}</span><div><h4>{e(h)}</h4><p>{e(t)}</p></div></li>' for i, (h, t) in enumerate(points))
    slides = "".join(f'<figure class="slide"><div class="stars" aria-label="5 out of 5 stars">★★★★★</div><blockquote>“{e(t)}”</blockquote><figcaption>Verified patient review</figcaption></figure>' for t in TESTIMONIALS)
    dots = "".join(f'<button class="dot" aria-label="Show review {i+1}"></button>' for i in range(len(TESTIMONIALS)))
    # Rotating hero background, same six images and order as the legacy Duda slideshow
    hero_imgs = ["hero-procedures-collage", "plastic-surgery-hero-consultation",
                 "dr-alan-tran-practice-hero", "plastic-surgery-hero-patient",
                 "plastic-surgery-hero-natural-results", "orange-county-plastic-surgery-hero"]
    hero_slides = "".join(
        f'<div class="hero-slide is-active" style="background-image:url(\'{img_url(n)}\')"></div>' if i == 0
        else f'<div class="hero-slide" data-bg="{img_url(n)}"></div>'
        for i, n in enumerate(hero_imgs))
    body = f"""
<section class="hero" data-hero-slides>
  <div class="hero-slides" aria-hidden="true">{hero_slides}</div>
  <div class="wrap hero-inner">
    <p class="hero-tag">{e(s['tagline'])}</p>
    <h1>Look your best, <em>Naturally<sup class="service-mark">℠</sup></em></h1>
    <p class="lede">Dr. Alan Tran spends real, unhurried time with every patient, refining rhinoplasty, breast, body and facial procedures toward one goal: results that still look like you.</p>
    <div class="hero-actions"><a class="btn btn-pink" href="/contact/">Request a Consultation</a><a class="btn btn-outline-light" href="/about/">Meet Dr. Tran</a></div>
  </div>
</section>
<section class="asps"><div class="wrap"><h2>Member of the American Society of Plastic Surgeons since 2000</h2></div></section>
<section class="credentials" aria-labelledby="credentials-title"><div class="wrap credentials-inner">
  <div><p class="eyebrow">Professional Credentials</p><h2 id="credentials-title">Board-certified plastic surgery expertise</h2>
  <p>Training, certification, and professional membership support the careful, evidence-based approach Dr. Tran brings to every consultation and procedure.</p></div>
  <figure class="credential-art"><img src="/assets/img/plastic-surgery-credentials.jpg" alt="Plastic surgery board certification and professional credentials" loading="lazy" width="550" height="269"></figure>
</div></section>
<section class="cards3" data-feature-cards><div class="wrap">
  <div class="cards3-grid">
    <button class="card is-active" type="button" data-feature-card="experience" aria-controls="feature-experience" aria-expanded="true"><h3>Over 26 Years of Experience</h3></button>
    <button class="card" type="button" data-feature-card="charity" aria-controls="feature-charity" aria-expanded="false"><h3>Committed to Charitable Causes</h3></button>
    <button class="card" type="button" data-feature-card="trusted" aria-controls="feature-trusted" aria-expanded="false"><h3>Trusted by Physicians &amp; Insiders</h3></button>
  </div>
  <div class="feature-details" aria-live="polite">
    <div class="feature-detail is-active" id="feature-experience" data-feature-panel="experience"><h3>Serving Orange County since 2000</h3><p>For more than 26 years, Dr. Tran has cared for patients in the local community with personal attention, honest guidance, and results designed to look natural.</p></div>
    <div class="feature-detail" id="feature-charity" data-feature-panel="charity"><h3>Child Smiles</h3><p>Repairing children born with cleft lip and palate since 2002 through charitable surgical care in the United States and abroad.</p></div>
    <div class="feature-detail" id="feature-trusted" data-feature-panel="trusted"><h3>Trusted by health care professionals</h3><p>Physicians, nurses, scrub technicians, and other health care professionals choose Dr. Alan Tran for their own care because they value his meticulous technique, thoughtful planning, and natural-looking results.</p></div>
  </div>
</div></section>
<section class="stats"><div class="wrap stats-grid">
  <div><strong>2000</strong><span>Practice Established</span></div>
  <div><strong>9+</strong><span>Procedures Offered</span></div>
  <div><strong>1:1</strong><span>Time With Dr. Tran</span></div>
  <div><strong>OC</strong><span>Fountain Valley &amp; Orange County</span></div>
</div></section>
<section class="welcome"><div class="wrap welcome-grid">
  <figure class="welcome-img"><img src="{img_url('dr-alan-tran-portrait')}" alt="Dr. Alan T. Tran" loading="lazy"></figure>
  <div>
    <p class="eyebrow">Welcome</p>
    <h2>A practice built around honest conversation</h2>
    <p>Dr. Tran believes every patient deserves unhurried, personal time with their surgeon. He listens carefully, sets realistic expectations, and designs a plan around what will look natural for you, not a one-size-fits-all result.</p>
    <p class="pull">“Enhancing your natural beauty”</p>
    <p>You’ll spend real consultation time directly with Dr. Alan Tran, discussing your goals, your options, and what results you can realistically expect - in a setting built to feel supportive, not clinical.</p>
  </div>
</div></section>
<section class="tiles-sec"><div class="wrap">
  <p class="eyebrow center">Procedures</p>
  <h2 class="center">Care organized around where you want to see change</h2>
  <p class="center lede-dark">Explore cosmetic and reconstructive procedures by selecting a category.</p>
  <div class="tiles">{tiles_html}</div>
  <div class="tile-submenus" aria-live="polite">{tile_panels}</div>
</div></section>
<section class="meet"><div class="wrap meet-grid">
  <figure><img src="{img_url('dr-alan-tran-office-portrait')}" alt="Dr. Alan T. Tran in his office" loading="lazy"></figure>
  <div>
    <p class="eyebrow">Meet Dr. Tran</p>
    <h2>Helping you achieve your best natural look</h2>
    <p class="quote">“When you visit our office, you will spend quality time with me. Your desired appearance and questions about treatment and outcome will be thoroughly addressed. I want you to find me personable and attentive.” <span>- Dr. Alan Tran</span></p>
    <p>Thoughtful and analytical, Dr. Tran combines artistic judgment, meticulous attention to detail, and individualized planning to help each patient achieve a natural result.</p>
    <ol class="points">{points_html}</ol>
  </div>
</div></section>
<section class="testimonials" id="testimonials"><div class="wrap">
  <h2 class="center">Testimonials</h2>
  <div class="carousel" data-carousel>
    <button class="car-btn prev" aria-label="Previous review">‹</button>
    <div class="slides">{slides}</div>
    <button class="car-btn next" aria-label="Next review">›</button>
    <div class="dots">{dots}</div>
  </div>
</div></section>
<section class="reviews-cta"><div class="wrap center">
  <div class="stars">★★★★★</div>
  <h2>Real feedback from real patients across Orange County</h2>
  <p>We’re proud of how patients describe their experience with our practice. Read verified reviews, or share your own after your visit.</p>
  <div class="ready-actions center"><a class="btn btn-white" href="/testimonials/">Read Patient Reviews</a><a class="btn btn-outline-light" href="https://ratemy.pro/Alan" target="_blank" rel="noopener" data-review-popup>Leave a Review</a></div>
</div></section>
<section class="visit"><div class="wrap visit-grid">
  <div>
    <p class="eyebrow">Visit the Office</p>
    <h2>Schedule your consultation</h2>
    <dl class="visit-list">
      <dt>Address</dt><dd>{e(s['address_line'])}, {e(s['city'])}, {e(s['state'])} {e(s['zip'])}</dd>
      <dt>Phone</dt><dd><a href="tel:{s['phone_e164']}">{e(s['phone'])}</a></dd>
      <dt>Email</dt><dd><a href="mailto:{e(s['email'])}">{e(s['email'])}</a></dd>
      <dt>Hours</dt><dd>Mon–Fri, 10:00am–6:00pm · Sat–Sun, Closed</dd>
    </dl>
    <a class="btn btn-pink" href="tel:{s['phone_e164']}">Call to Book</a>
  </div>
  <figure><img src="{img_url('fountain-valley-plastic-surgery-office')}" alt="Our office building at 17931 Euclid St, Fountain Valley" loading="lazy"></figure>
</div></section>
{ready_band()}"""
    jsonld = f"""<script type="application/ld+json">{json.dumps({
        "@context": "https://schema.org", "@type": "Physician", "name": s["practice_name"], "url": BASE,
        "telephone": s["phone"], "email": s["email"], "medicalSpecialty": "PlasticSurgery",
        "address": {"@type": "PostalAddress", "streetAddress": s["address_line"], "addressLocality": s["city"], "addressRegion": s["state"], "postalCode": s["zip"], "addressCountry": "US"},
        "openingHours": "Mo-Fr 10:00-18:00", "foundingDate": s["established"], "image": BASE + img_url("dr-alan-tran-office-portrait")})}</script>"""
    page("/", "Alan T. Tran, M.D. | Plastic Surgery in Fountain Valley, Orange County",
         "Board-certified plastic and reconstructive surgeon Dr. Alan T. Tran has served Orange County since 2000. Breast, body, skin and facial procedures in Fountain Valley, CA.",
         body, "home", jsonld=jsonld)

# ---------------------------------------------------------------- other pages
def build_about():
    a = pages["about"]
    who = "".join(f"<p>{e(x)}</p>" for x in a["who"])
    body = page_hero("About Dr. Alan Tran", site["tagline"], "dr-alan-tran-practice-hero", "About") + f"""
<section class="svc-sec"><div class="wrap svc-split img-right">
  <div class="prose"><p class="eyebrow">Welcome to our clinic</p><h2>Helping you achieve your best natural look</h2><p class="quote">{e(a['welcome'])}</p><p class="sig">- Dr. Alan Tran</p></div>
  <figure><img src="{img_url('dr-alan-tran-office-portrait')}" alt="Dr. Alan T. Tran" loading="lazy"></figure>
</div></section>
<section class="svc-sec alt-bg"><div class="wrap prose prose-narrow"><h2>Who we are</h2>{who}</div></section>
<section class="related"><div class="wrap"><ul class="pill-list"><li><a href="/meet-the-doctor/">Meet the Doctor</a></li><li><a href="/tour-the-office/">Tour the Office</a></li><li><a href="/services/">Our Procedures</a></li></ul></div></section>
{cta_band()}"""
    page("/about/", "About Dr. Alan Tran", "Dr. Alan T. Tran is a board-certified plastic and reconstructive surgeon practicing in Orange County since 2000.", body, "about")

def build_meet():
    body = page_hero("Meet the Doctor", "Alan T. Tran, M.D.", None, "About") + f"""
<section class="svc-sec"><div class="wrap svc-split img-left">
  <div class="prose">
    <p class="eyebrow">Dr. Alan T. Tran</p>
    <h2>A third-generation physician with an artist’s eye</h2>
    <p>Dr. Alan Tran is a third-generation physician. He is board certified in Plastic Surgery and General Surgery, and has been caring for patients in Orange County since 2000. His love for the arts (piano, sketching and gardening) brings an artistic eye to his practice. His approach to plastic surgery is science- and evidence-based, enhanced with creativity and a holistic style.</p>
    <p>In addition to his practice in Orange County, California, Dr. Tran’s special interest is providing surgery and care for underprivileged children with cleft lip and palate deformities in the United States and abroad. Since 2002, much of that work has taken place at White Memorial Medical Center in East Los Angeles.</p>
    <p>Dr. Alan Tran is a kind, patient and compassionate doctor with whom you will find it easy to establish rapport.</p>
    <p class="pull">Let us help you look your best… naturally.</p>
    <a class="btn btn-pink" href="/contact/">Request a Consultation</a>
  </div>
  <figure><img src="{img_url('dr-alan-tran-portrait')}" alt="Dr. Alan T. Tran" loading="lazy"></figure>
</div></section>
{cta_band()}"""
    page("/meet-the-doctor/", "Meet Dr. Alan T. Tran", "Meet Dr. Alan T. Tran, a third-generation physician board certified in Plastic Surgery and General Surgery.", body, "about")

def build_tour():
    photos = [("fountain-valley-plastic-surgery-office", "Our office at 17931 Euclid St, Fountain Valley"), ("dr-alan-tran-office-portrait", "Dr. Tran in the office")]
    figs = "".join(f'<figure><img src="{img_url(i)}" alt="{e(a)}" loading="lazy"><figcaption>{e(a)}</figcaption></figure>' for i, a in photos)
    body = page_hero("Tour the Office", f"{site['address_line']}, {site['city']}, {site['state']} {site['zip']}", None, "About") + f"""
<section class="svc-sec"><div class="wrap">
  <div class="prose prose-narrow center"><p>Our office in Fountain Valley was built to feel welcoming and personal, not clinical. Consultations and many in-office procedures take place here, and you’ll always spend your time with Dr. Tran himself.</p></div>
  <div class="tour-grid">{figs}</div>
</div></section>
<section class="svc-sec alt-bg"><div class="wrap"><div class="map-wrap"><iframe title="Map to our office" loading="lazy" referrerpolicy="no-referrer-when-downgrade" src="https://maps.google.com/maps?q={e(site['map_query']).replace(' ', '+')}&amp;output=embed"></iframe></div></div></section>
{ready_band()}"""
    page("/tour-the-office/", "Tour the Office", "Visit Dr. Alan T. Tran's plastic surgery office at 17931 Euclid St, Fountain Valley, CA.", body, "about")

def build_services_index():
    cols = ""
    blurbs = {"Breast": "Augmentation, lifts, reductions, revisions and reconstruction, planned around your proportions.",
              "Body": "Contouring procedures that restore shape after weight loss, pregnancy or aging.",
              "Skin": "In-office treatments, scar care and skin cancer reconstruction.",
              "Face": "Subtle facial procedures that refresh your look while keeping it yours."}
    for c in CAT_ORDER:
        items = "".join(f'<li><a href="/services/{s}/">{e(n)}</a></li>' for s, n in SERVICES[c])
        cols += f'<div class="svc-cat" id="{c.lower()}"><h2>{c}</h2><p>{blurbs[c]}</p><ul>{items}</ul></div>'
    body = page_hero("Our Procedures", "Cosmetic and reconstructive care, all performed by Dr. Alan T. Tran.", None, "Services") + f"""
<section class="svc-sec"><div class="wrap svc-cats">{cols}</div></section>
{cta_band()}"""
    page("/services/", "Procedures & Services", "Breast, body, skin and facial plastic surgery procedures with Dr. Alan T. Tran in Fountain Valley, Orange County.", body, "services")

def build_gallery():
    g = pages["gallery"]
    cats = " · ".join(e(c) for c in g["categories"])
    items = "".join(f'<a class="g-item" href="{img_url(i)}" data-lightbox><img src="{img_url(i)}" alt="Before and after photo {n+1}" loading="lazy"></a>' for n, i in enumerate(g["images"]))
    body = page_hero("Gallery", "Before & after results", None, "Our Work") + f"""
<section class="svc-sec"><div class="wrap">
  <p class="center gallery-cats">{cats}</p>
  <div class="gallery-grid">{items}</div>
  <p class="center small">Individual results vary. Photos are of actual patients of Dr. Tran and are shared with permission.</p>
</div></section>
<div class="lightbox" hidden><button class="lb-close" aria-label="Close">×</button><button class="lb-prev" aria-label="Previous">‹</button><img alt=""><button class="lb-next" aria-label="Next">›</button></div>
{cta_band()}"""
    page("/gallery/", "Before & After Gallery", "Before and after photos of patients of Dr. Alan T. Tran, Fountain Valley plastic surgeon.", body, "gallery")


REVIEWS = [
    ("Kelly T.", "Westminster, CA", "Dr. Alan T Tran is a very good surgeon! He is so good and I am proud of him. He did my surgery and it was absolutely good. He was the best surgeon in the world. I like him being my surgeon!!!! Thank you very much for doing my surgery!!!!"),
    ("Shane G.", "Anaheim, CA", "Dr. Tran is an amazing surgeon. His attention to detail and making sure his patients are satisfied with the results is what makes him and his office successful. He does amazing breast reconstruction and cosmetic surgery. He takes the time to explain all of the options and his reasoning for choosing his products of choice for your specific needs."),
    ("Marcos L.", "Aliso Viejo, CA", "You think the best Dr. for nose jobs is in Hollywood or Newport Beach?! Nope! Alan Tran knocks around in the medical underground in Westminster. By far a superb and meticulous Dr. He takes his time and ensures everything is and will be correct w/ your nose. Staff was an 11 out of 10 Dr. Tran is concise w/ how he will proceed w/ the surgery and how he will ensure, he will make everything better to best of his ability. Dr. Tran goes about his occupation like art, pristine, will take his time, and will fix your structural being in Channel glasses and Gucci flip flops. I am extremely pleased w/ the end result and would recommend Dr. Tran to anyone looking to fix their nose."),
    ("Sandy S.", "Federal Way, WA", "Dr. Tran is great!! I’m amazed with his work. I can’t get over how meticulous he is. He is such a sweet, caring, and easy-going surgeon. He doesn’t rush you out the office to take another patient in. Every visit I had his undivided attention. He explained everything in details. And if I asked the same question twice, no biggie. Great person and MD!!!"),
]

def build_testimonials():
    cards = "".join(
        f'<article class="review-card"><div class="stars" aria-label="5 out of 5 stars">★★★★★</div>'
        f'<blockquote>“{e(quote)}”</blockquote><p class="review-by">{e(name)}<small>{e(place)}</small></p></article>'
        for name, place, quote in REVIEWS)
    body = page_hero("Patient Testimonials", "Real stories from patients who have transformed their lives through expert care and personalized surgical solutions.", None, "Patient Journeys with Dr. Tran") + f"""
<section class="svc-sec"><div class="wrap">
  <p class="eyebrow center">Patient Stories and Feedback</p>
  <h2 class="center">What patients say about Dr. Tran</h2>
  <div class="review-list">{cards}</div>
  <div class="ready-actions center review-actions"><a class="btn btn-pink" href="https://ratemy.pro/Alan" target="_blank" rel="noopener" data-review-popup>Leave a Review</a><a class="btn btn-outline" href="/contact/">Request a Consultation</a></div>
</div></section>
{cta_band()}"""
    page("/testimonials/", "Patient Testimonials", "Patient stories and reviews of Dr. Alan T. Tran, plastic surgeon in Fountain Valley, Orange County.", body, "testimonials")

def build_specials():
    body = page_hero("Specials", "Current offers from our office", None) + f"""
<section class="svc-sec"><div class="wrap prose prose-narrow center">
  <p class="eyebrow center">Current Special</p>
  <h2>Xeomin® for $10 per unit</h2>
  <p>Smooth forehead lines, crow’s feet and frown lines with Xeomin at $10 per unit (regular price $12.50 a unit). Call the office to book your appointment or ask any questions.</p>
  <figure class="special-flyer"><a href="/assets/img/specials-xeomin-flyer.webp" target="_blank" rel="noopener"><img src="/assets/img/specials-xeomin-flyer.webp" alt="Xeomin special: $10 per unit, regular price $12.50 a unit. Reduces forehead lines, softens crow’s feet and smooths frown lines. Call 714-966-2888, 17931 Euclid Street, Fountain Valley, CA 92708." width="1024" height="1536" loading="lazy"></a></figure>
  <div class="ready-actions center"><a class="btn btn-pink" href="tel:{site['phone_e164']}">Call {e(site['phone'])}</a><a class="btn btn-outline" href="/contact/">Send a Message</a></div>
  <p class="special-note">We also periodically offer savings on other injectables, skin treatments and select procedures. Call or send us a message to hear what’s available right now.</p>
</div></section>"""
    page("/specials/", "Specials", "Xeomin special at $10 per unit and other current offers from the office of Dr. Alan T. Tran in Fountain Valley.", body, "specials")

def contact_form(svc_options):
    return f"""
<form class="contact-form" action="/lead-webhook" method="post" data-lead-form novalidate>
  <div class="hp" aria-hidden="true"><label>Leave this empty <input type="text" name="website" tabindex="-1" autocomplete="off"></label></div>
  <div class="form-status" role="status" aria-live="polite"></div>
  <div class="row2">
    <label>Full name<input type="text" name="name" required maxlength="100" autocomplete="name"></label>
    <label>Phone<input type="tel" name="phone" maxlength="30" autocomplete="tel"></label>
  </div>
  <label>Email<input type="email" name="email" required maxlength="150" autocomplete="email"></label>
  <label>Procedure of interest<select name="service"><option value="">Select one (optional)</option>{svc_options}</select></label>
  <label>Message<textarea name="message" rows="5" maxlength="4000" required></textarea></label>
  <p class="small">Please don’t include detailed medical information. We’ll reply by phone or email within one business day.</p>
  <button class="btn btn-pink" type="submit">Send Message</button>
</form>"""

def build_contact():
    opts = "".join(f'<optgroup label="{c}">' + "".join(f"<option>{e(n)}</option>" for s, n in SERVICES[c]) + "</optgroup>" for c in CAT_ORDER)
    body = page_hero("Contact Dr. Alan T. Tran’s Office", "Reach out to schedule your consultation or ask about our surgical and aesthetic services.", None, "Contact") + f"""
<section class="svc-sec"><div class="wrap contact-grid">
  <div class="contact-info">
    <h2>Quick Contact</h2>
    <address>{e(site['address_line'])}<br>{e(site['city'])}, {e(site['state'])} {e(site['zip'])}</address>
    <p><strong>Phone</strong><br><a href="tel:{site['phone_e164']}">{e(site['phone'])}</a></p>
    <p><strong>Fax</strong><br>{e(site['fax'])}</p>
    <p><strong>Email</strong><br><a href="mailto:{e(site['email'])}">{e(site['email'])}</a></p>
    <p><strong>Hours</strong><br>Monday – Friday, 10:00 AM – 6:00 PM<br>Saturday &amp; Sunday, Closed</p>
  </div>
  <div class="form-card"><h2>Send Us a Message</h2>{contact_form(opts)}</div>
</div></section>
<section class="svc-sec alt-bg"><div class="wrap"><h2 class="center">Our Location</h2><div class="map-wrap"><iframe title="Map to our office" loading="lazy" referrerpolicy="no-referrer-when-downgrade" src="https://maps.google.com/maps?q={e(site['map_query']).replace(' ', '+')}&amp;output=embed"></iframe></div></div></section>"""
    page("/contact/", "Contact Us", "Contact the office of Dr. Alan T. Tran at 17931 Euclid St, Fountain Valley, CA. Call (714) 966-2888.", body, "contact")

def build_thanks():
    body = page_hero("Thank You", "", None) + f"""
<section class="svc-sec"><div class="wrap prose prose-narrow center">
  <h2>Thank you for your request.</h2><p>One of our team members will get back to you shortly. If you need us sooner, please call <a href="tel:{site['phone_e164']}">{e(site['phone'])}</a>.</p><p>Have a great day!</p>
  <a class="btn btn-pink" href="/">Back to Home</a>
</div></section>"""
    page("/thank-you/", "Thank You", "Thank you for contacting our office.", body)

def build_privacy():
    blocks = pages["privacy-policy"]["blocks"]
    inner = render_blocks([dict(b, x=b["x"].replace("{{SITE_DOMAIN}}", domain)) if "x" in b else b for b in blocks])
    body = page_hero("Privacy Policy", "", None) + f'<section class="svc-sec"><div class="wrap prose prose-narrow">{inner}</div></section>'
    page("/privacy-policy/", "Privacy Policy", "Privacy policy for the website of Alan T. Tran, M.D., Inc.", body)

def build_404():
    body = page_hero("Page Not Found", "", None) + """
<section class="svc-sec"><div class="wrap prose prose-narrow center"><p>Sorry, we couldn’t find that page. It may have moved when we updated our website.</p>
<div class="ready-actions center"><a class="btn btn-pink" href="/">Home</a><a class="btn btn-outline" href="/services/">Our Procedures</a></div></div></section>"""
    page("/404.html", "Page Not Found", "Page not found.", body)

# ---------------------------------------------------------------- main
def main():
    if OUT.exists():
        for child in OUT.iterdir():
            if child.name == "assets":
                for sub in child.iterdir():
                    if sub.name != "img":
                        shutil.rmtree(sub) if sub.is_dir() else sub.unlink()
            else:
                shutil.rmtree(child) if child.is_dir() else child.unlink()
    OUT.mkdir(exist_ok=True)
    shutil.copytree(SRC / "static", OUT, dirs_exist_ok=True)
    build_home(); build_about(); build_meet(); build_tour(); build_services_index()
    for slug, p in pages.items():
        if p["kind"] == "service":
            build_service(slug, p)
    build_gallery(); build_testimonials(); build_specials(); build_contact(); build_thanks(); build_privacy(); build_404()
    today = datetime.date.today().isoformat()
    sm = "".join(f"<url><loc>{BASE}{p}</loc><lastmod>{today}</lastmod></url>" for p in SITEMAP if p != "/thank-you/")
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n')
    (OUT / "robots.txt").write_text(f"User-agent: *\nDisallow: /thank-you/\nSitemap: {BASE}/sitemap.xml\n")
    print(f"Built {len(SITEMAP)} pages into {OUT} for {BASE}")

if __name__ == "__main__":
    main()
