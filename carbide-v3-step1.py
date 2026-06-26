#!/usr/bin/env python3
"""
Carbide Site v3 — Step 1: Button + Homepage Rewrite
"""
import os, re, pathlib

ROOT = pathlib.Path("/Users/nicky/ZCodeProject/carbide-site")

# ── BUTTON TEXT FIX ──
def fix_button_text():
    btn_labels = {
        "en": "Calculators &amp; Tools",
        "de": "Rechner &amp; Werkzeuge",
        "jp": "計算機 &amp; ツール",
        "es": "Calculadoras &amp; Herramientas",
        "vi": "Máy Tính &amp; Công Cụ",
    }
    patterns = [
        r'Browse All 100\+ Tools →',
        r'View All 100 Tools →',
        r'View All 100\+ Tools →',
    ]
    # Homepage-specific broken buttons
    broken_de = [r'📊Härte wandler sofort zwischen HRC.*?konvertieren\.']
    broken_jp = [r'📊硬度コンバーターは.*?変換します。']
    broken_vi = [r'📊Chuyển đổi ngay lập tức.*?độ bền kéo\.']
    
    count = 0
    for f in ROOT.rglob("*.html"):
        if ".git" in str(f) or ".venv" in str(f):
            continue
        rel = str(f.relative_to(ROOT))
        lang = "en"
        if rel.startswith("de/"): lang = "de"
        elif rel.startswith("jp/"): lang = "jp"
        elif rel.startswith("es/"): lang = "es"
        elif rel.startswith("vi/"): lang = "vi"
        
        text = f.read_text(encoding="utf-8")
        new_text = text
        for pat in patterns:
            new_text = re.sub(pat, btn_labels[lang], new_text)
        if lang == "de":
            for pat in broken_de: new_text = re.sub(pat, btn_labels["de"], new_text)
        elif lang == "jp":
            for pat in broken_jp: new_text = re.sub(pat, btn_labels["jp"], new_text)
        elif lang == "vi":
            for pat in broken_vi: new_text = re.sub(pat, btn_labels["vi"], new_text)
        
        if new_text != text:
            f.write_text(new_text, encoding="utf-8")
            count += 1
    print(f"✅ Button text fixed in {count} files")

# ── ENGLISH HOMEPAGE BUTTON ──
def fix_en_homepage():
    f = ROOT / "index.html"
    text = f.read_text(encoding="utf-8")
    text = text.replace("Browse All 100+ Tools →", "Calculators &amp; Tools")
    f.write_text(text, encoding="utf-8")
    print("✅ EN homepage button fixed")

# ── HOMEPAGE REWRITE ──
# Read the English homepage CSS + style (everything before </head>)
def extract_head_section(lang_code, prefix):
    """Build the <head> section for a localized homepage."""
    en_home = ROOT / "index.html"
    en_text = en_home.read_text(encoding="utf-8")
    
    # Extract the CSS block (everything between <style> and </style>)
    css_match = re.search(r'<style>\n(.*?)\n</style>', en_text, re.DOTALL)
    if not css_match:
        css_match = re.search(r'<style>(.*?)</style>', en_text, re.DOTALL)
    css_content = css_match.group(1) if css_match else ""
    
    # Extract the nav-v2 style
    nav_style_match = re.search(r'<style id="nav-v2-style">(.*?)</style>', en_text, re.DOTALL)
    nav_style = nav_style_match.group(1) if nav_style_match else ""
    
    # Extract tailwind config
    tw_match = re.search(r'<script>\ntailwind\.config = \{(.*?)\n\}\n</script>', en_text, re.DOTALL)
    tw_config = tw_match.group(1) if tw_match else ""
    
    # Build hreflangs
    hreflangs = f'''<link href="https://carbide-tooling.com/{prefix}index.html" rel="canonical"/>
<link href="https://carbide-tooling.com/index.html" hreflang="x-default" rel="alternate"/>
<link href="https://carbide-tooling.com/index.html" hreflang="en" rel="alternate"/>
<link href="https://carbide-tooling.com/de/index.html" hreflang="de" rel="alternate"/>
<link href="https://carbide-tooling.com/jp/index.html" hreflang="ja" rel="alternate"/>
<link href="https://carbide-tooling.com/es/index.html" hreflang="es" rel="alternate"/>
<link href="https://carbide-tooling.com/vi/index.html" hreflang="vi" rel="alternate"/>'''
    
    return css_content, nav_style, tw_config, hreflangs

def build_homepage_file(lang, translations):
    """Build a complete localized homepage using the English CSS template."""
    t = translations
    pfx = t["prefix"]
    
    css_content, nav_style, tw_config, hreflangs = extract_head_section(t["lang_code"], pfx)
    
    # Build lang links for nav
    lang_links = {
        "de": '<a href="/">EN</a><span class="sep">·</span><a href="#" onclick="return false" class="active">DE</a><a href="/jp/">JP</a><span class="sep">·</span><a href="/es/">ES</a><a href="/vi/">VI</a>',
        "jp": '<a href="/">EN</a><span class="sep">·</span><a href="/de/">DE</a><a href="#" onclick="return false" class="active">JP</a><span class="sep">·</span><a href="/es/">ES</a><a href="/vi/">VI</a>',
        "es": '<a href="/">EN</a><span class="sep">·</span><a href="/de/">DE</a><a href="/jp/">JP</a><span class="sep">·</span><a href="#" onclick="return false" class="active">ES</a><a href="/vi/">VI</a>',
        "vi": '<a href="/">EN</a><span class="sep">·</span><a href="/de/">DE</a><a href="/jp/">JP</a><span class="sep">·</span><a href="/es/">ES</a><a href="#" onclick="return false" class="active">VI</a>',
    }
    
    # Build nav links
    nav_links = f'''<a href="{pfx}">{t["nav_home"]}</a>
<a href="{pfx}products/">{t["nav_prod"]}</a>
<a href="{pfx}tools/">{t["nav_tools"]}</a>
<a href="{pfx}guides/">{t["nav_guides"]}</a>
<a href="{pfx}about.html">{t["nav_about"]}</a>'''
    
    # Build body HTML (no f-string for CSS parts, just simple string)
    body_html = f'''
<body>
<!-- ===== NAV ===== -->
<nav id="nav-v2">
<div class="nv-inner">
<a class="nv-logo" href="{pfx}"><span>◆</span> Carbide Tooling</a>
<div class="nv-links">
{nav_links}
</div>
<div class="nv-right">
<div class="nv-lang">{lang_links[lang]}</div>
<a class="nv-quote" href="{pfx}quote.html">{t["nav_quote"]}</a>
</div>
</div>
</nav>
<!-- ===== HERO ===== -->
<section class="hero">
<div class="container" style="display:contents;">
<div class="hero-text">
<h1>{t["hero_h1"]}<br/><span class="accent">{t["hero_h1_break"]}</span></h1>
<p>{t["hero_p"]}</p>
<div class="hero-actions">
<a class="btn-primary" href="{pfx}products/">{t["hero_btn1"]}</a>
<a class="btn-secondary" href="{pfx}about.html">{t["hero_btn2"]}</a>
<a class="btn-secondary" href="{pfx}tools/speed-feed/">{t["hero_btn3"]}</a>
</div>
</div>
<div class="hero-img">
<img alt="{t["img_alt_hero"]}" loading="lazy" src="/images/hero.jpg"/>
</div>
</div>
</section>
<!-- ===== INDUSTRIAL INTELLIGENCE HUB ===== -->
<section class="section" style="padding-bottom:40px">
<div class="container">
<div class="section-title">
<div class="label">{t["hub_label"]}</div>
<h2>{t["hub_h2"]}</h2>
<p>{t["hub_p"]}</p>
</div>
<div class="hub-featured">
<a class="hub-card hub-primary" href="{pfx}tools/speed-feed/">
<div class="hub-card-bg"></div>
<div class="hub-icon">⚙️</div>
<div class="hub-info">
<h3>{t["hub_h3_1"]}</h3>
<p>{t["hub_p_1"]}</p>
<span class="hub-cta">{t["hub_cta_1"]}</span>
</div>
</a>
<a class="hub-card hub-secondary" href="{pfx}tools/carbide-grade-cross-ref-2/">
<div class="hub-icon">🔩</div>
<div class="hub-info">
<h3>{t["hub_h3_2"]}</h3>
<p>{t["hub_p_2"]}</p>
<span class="hub-cta">{t["hub_cta_2"]}</span>
</div>
</a>
<a class="hub-card hub-secondary" href="{pfx}tools/hardness-converter/">
<div class="hub-icon">📊</div>
<div class="hub-info">
<h3>{t["hub_h3_3"]}</h3>
<p>{t["hub_p_3"]}</p>
<span class="hub-cta">{t["hub_cta_3"]}</span>
</div>
</a>
</div>
<div class="hub-categories">
<a class="hub-cat" href="{pfx}tools/">
<span class="hub-cat-icon">⚡</span>
<span class="hub-cat-name">{t["cat1_name"]}</span>
<span class="hub-cat-count">{t["cat1_count"]}</span>
</a>
<a class="hub-cat" href="{pfx}tools/">
<span class="hub-cat-icon">🔧</span>
<span class="hub-cat-name">{t["cat2_name"]}</span>
<span class="hub-cat-count">{t["cat2_count"]}</span>
</a>
<a class="hub-cat" href="{pfx}tools/">
<span class="hub-cat-icon">🔩</span>
<span class="hub-cat-name">{t["cat3_name"]}</span>
<span class="hub-cat-count">{t["cat3_count"]}</span>
</a>
<a class="hub-cat" href="{pfx}tools/">
<span class="hub-cat-icon">📊</span>
<span class="hub-cat-name">{t["cat4_name"]}</span>
<span class="hub-cat-count">{t["cat4_count"]}</span>
</a>
</div>
<div style="text-align:center;margin-top:24px">
<a class="btn-secondary" href="{pfx}tools/" style="display:inline-flex;align-items:center;gap:8px;padding:10px 22px;border-radius:24px;font-size:13px;font-weight:500;text-decoration:none;color:#1d1d1f;background:rgba(0,0,0,.05)">{t["tools_btn"]}</a>
</div>
</div>
</section>
<!-- ===== TOOLBOX ===== -->
<section class="section">
<div class="container">
<div class="toolbox">
<div class="toolbox-title">
<div class="label">{t["tb_label"]}</div>
<h2>{t["tb_h2"]}</h2>
<p>{t["tb_p"]}</p>
</div>
<div class="toolbox-grid">
<a class="toolbox-card" href="{pfx}tools/speed-feed/">
<div class="icon">⚙️</div>
<div class="info"><h3>{t["tb_h3_1"]}</h3><p>{t["tb_p_1"]}</p></div>
</a>
<a class="toolbox-card" href="{pfx}tools/chip-load/">
<div class="icon">📐</div>
<div class="info"><h3>{t["tb_h3_2"]}</h3><p>{t["tb_p_2"]}</p></div>
</a>
<a class="toolbox-card" href="{pfx}tools/carbide-grade-cross-ref-2/">
<div class="icon">🔩</div>
<div class="info"><h3>{t["tb_h3_3"]}</h3><p>{t["tb_p_3"]}</p></div>
</a>
<a class="toolbox-card" href="{pfx}tools/hardness-converter/">
<div class="icon">📊</div>
<div class="info"><h3>{t["tb_h3_4"]}</h3><p>{t["tb_p_4"]}</p></div>
</a>
</div>
</div>
</div>
</section>
<!-- ===== PRODUCTS ===== -->
<section class="section">
<div class="container">
<div class="section-title">
<div class="label">{t["prod_label"]}</div>
<h2>{t["prod_h2"]}</h2>
<p>{t["prod_p"]}</p>
</div>
<div class="grid3">
<div class="card"><img alt="{t["img_alt_endmill"]}" loading="lazy" src="/images/endmills.jpg"/><div class="card-body"><h3>{t["card_h3_1"]}</h3><p>{t["card_p_1"]}</p></div></div>
<div class="card"><img alt="{t["img_alt_insert"]}" loading="lazy" src="/images/inserts.jpg"/><div class="card-body"><h3>{t["card_h3_2"]}</h3><p>{t["card_p_2"]}</p></div></div>
<div class="card"><img alt="{t["img_alt_drill"]}" loading="lazy" src="/images/drills.jpg"/><div class="card-body"><h3>{t["card_h3_3"]}</h3><p>{t["card_p_3"]}</p></div></div>
<div class="card"><img alt="{t["img_alt_holder"]}" loading="lazy" src="/images/holders.jpg"/><div class="card-body"><h3>{t["card_h3_4"]}</h3><p>{t["card_p_4"]}</p></div></div>
<div class="card"><img alt="{t["img_alt_boring"]}" loading="lazy" src="/images/boring.jpg"/><div class="card-body"><h3>{t["card_h3_5"]}</h3><p>{t["card_p_5"]}</p></div></div>
<div class="card"><img alt="{t["img_alt_thread"]}" loading="lazy" src="/images/boring.jpg"/><div class="card-body"><h3>{t["card_h3_6"]}</h3><p>{t["card_p_6"]}</p></div></div>
</div>
</div>
</section>
<!-- ===== GUIDES ===== -->
<section class="section" style="padding-top:0">
<div class="container">
<div class="section-title">
<div class="label">{t["guide_label"]}</div>
<h2>{t["guide_h2"]}</h2>
<p>{t["guide_p"]}</p>
</div>
<div class="grid2">
<a class="card card-link" href="{pfx}guides/end-mill-geometry.html"><div class="card-body"><h3>{t["guide_h3_1"]}</h3><p>{t["guide_p_1"]}</p></div></a>
<a class="card card-link" href="{pfx}guides/carbide-grades.html"><div class="card-body"><h3>{t["guide_h3_2"]}</h3><p>{t["guide_p_2"]}</p></div></a>
<a class="card card-link" href="{pfx}guides/coating-comparison.html"><div class="card-body"><h3>{t["guide_h3_3"]}</h3><p>{t["guide_p_3"]}</p></div></a>
<a class="card card-link" href="{pfx}guides/sourcing-from-china.html"><div class="card-body"><h3>{t["guide_h3_4"]}</h3><p>{t["guide_p_4"]}</p></div></a>
</div>
</div>
</section>
<!-- ===== TRUST MODULE ===== -->
<section class="trust-section">
<div class="container">
<div class="trust-title">
<div class="label">{t["trust_label"]}</div>
<h2>{t["trust_h2"]}</h2>
<p>{t["trust_p"]}</p>
</div>
<div class="trust-scroll">
<div class="trust-card"><div class="equip-icon">📐</div><h3>{t["trust_h3_1"]}</h3><p>{t["trust_p_1"]}</p></div>
<div class="trust-card"><div class="equip-icon">🔬</div><h3>{t["trust_h3_2"]}</h3><p>{t["trust_p_2"]}</p></div>
<div class="trust-card"><div class="equip-icon">⚖️</div><h3>{t["trust_h3_3"]}</h3><p>{t["trust_p_3"]}</p></div>
<div class="trust-card"><div class="equip-icon">🔍</div><h3>{t["trust_h3_4"]}</h3><p>{t["trust_p_4"]}</p></div>
<div class="trust-card"><div class="equip-icon">🌡️</div><h3>{t["trust_h3_5"]}</h3><p>{t["trust_p_5"]}</p></div>
<div class="trust-card"><div class="equip-icon">📋</div><h3>{t["trust_h3_6"]}</h3><p>{t["trust_p_6"]}</p></div>
</div>
<div style="text-align:center;margin-top:32px;font-size:13px;color:#86868b">{t["swipe"]}</div>
</div>
</section>
<!-- ===== CTA ===== -->
<div class="container">
<div class="cta-block">
<h2>{t["cta_h2"]}</h2>
<p>{t["cta_p"]}</p>
<div class="btn-group">
<a class="btn-primary" href="{pfx}quote.html">{t["cta_btn1"]}</a>
<a class="btn-secondary" href="mailto:info@carbide-tooling.com">{t["cta_btn2"]}</a>
</div>
</div>
</div>
<!-- ===== FOOTER ===== -->
<footer>
<div class="footer-grid">
<div>
<div class="brand"><span>◆</span> Carbide Tooling</div>
<div class="tagline">{t["footer_tagline"]}</div>
</div>
<div>
<h4>{t["footer_prod"]}</h4>
<a href="{pfx}products/end-mills.html">{t["footer_prod1"]}</a>
<a href="{pfx}products/turning-inserts.html">{t["footer_prod2"]}</a>
<a href="{pfx}products/drills.html">{t["footer_prod3"]}</a>
<a href="{pfx}products/tool-holders.html">{t["footer_prod4"]}</a>
<a href="{pfx}products/boring-tools.html">{t["footer_prod5"]}</a>
<a href="{pfx}products/threading-tools.html">{t["footer_prod6"]}</a>
</div>
<div>
<h4>{t["footer_res"]}</h4>
<a href="{pfx}guides/">{t["footer_res1"]}</a>
<a href="{pfx}tools/speed-feed/">{t["footer_res2"]}</a>
<a href="{pfx}guides/carbide-grades.html">{t["footer_res3"]}</a>
<a href="{pfx}guides/coating-comparison.html">{t["footer_res4"]}</a>
</div>
<div>
<h4>{t["footer_co"]}</h4>
<a href="{pfx}about.html">{t["footer_co1"]}</a>
<a href="{pfx}quote.html">{t["footer_co2"]}</a>
<a href="mailto:info@carbide-tooling.com">{t["footer_co3"]}</a>
</div>
</div>
<div class="bottom">{t["footer_copy"]}</div>
</footer>
<script>
function toggleLang(e){{e.stopPropagation();var m=document.getElementById('lang-menu');if(m)m.classList.toggle('show')}}
document.addEventListener('click',function(){{var m=document.getElementById('lang-menu');if(m)m.classList.remove('show')}});
</script>
</body>
</html>'''
    
    # Now build the complete page by copying the <head> section from English homepage
    # but replacing lang, title, description, hreflang, etc.
    en_home = ROOT / "index.html"
    en_html = en_home.read_text(encoding="utf-8")
    
    # Extract everything before <body> from EN, modify it for lang
    head_match = re.search(r'^(.*?)<body>', en_html, re.DOTALL)
    head_section = head_match.group(1) if head_match else ""
    
    # Modify the head section for the target language
    # Replace lang attribute
    head_section = re.sub(r'<html lang="en">', f'<html lang="{t["lang_code"]}">', head_section)
    # Replace title
    head_section = re.sub(r'<title>.*?</title>', f'<title>{t["title"]}</title>', head_section)
    # Replace meta description
    head_section = re.sub(r'<meta content=".*?" name="description"/>', f'<meta content="{t["desc"]}" name="description"/>', head_section)
    # Replace og:description
    head_section = re.sub(r'<meta content=".*?" property="og:description"/>', f'<meta content="{t["og_desc"]}" property="og:description"/>', head_section, count=1)
    # Replace og:title
    head_section = re.sub(r'<meta content=".*?" property="og:title"/>', f'<meta content="{t["og_title"]}" property="og:title"/>', head_section, count=1)
    # Replace canonical and hreflang block
    head_section = re.sub(r'<link href="https://carbide-tooling\.com/.*?html" rel="canonical"/>.*?(?:<link href="https://carbide-tooling\.com/.*?html" hreflang="[^"]*" rel="alternate"/>.*?)+', hreflangs, head_section, flags=re.DOTALL)
    
    # Combine head + body
    final_html = head_section + body_html
    
    # Write out
    out_file = ROOT / lang / "index.html"
    out_file.write_text(final_html, encoding="utf-8")
    print(f"✅ Homepage rewritten for {lang}: {out_file}")

# ── TRANSLATION DATA ──
# Import translations from a separate JSON file to avoid f-string CSS issues
import json

translations_file = ROOT / "homepage-translations.json"
if not translations_file.exists():
    # Write the translations JSON file
    t_data = {}
    
    # German
    t_data["de"] = {
        "lang_code": "de", "prefix": "/de/",
        "title": "Carbide Tooling — Präzisions-CNC-Schneidwerkzeuge aus China | Schaftfräser, Wendeeinsätze, Werkzeughalter",
        "desc": "Premium-Hartmetall-Schaftfräser, Wendeeinsätze, Bohrer und Werkzeughalter von Chinas führenden Herstellern. Fabrikdirektpreise, ISO-Qualität, Engineering-Support.",
        "og_desc": "Premium-Hartmetall-Schneidwerkzeuge von Chinas besten Herstellern. Fabrikdirektpreise, ISO-Qualität, Engineering-Support — keine Zwischenhändler.",
        "og_title": "Hartmetall-Werkzeuge — Präzisions-CNC-Schneidwerkzeuge",
        "hero_h1": "Schneidwerkzeuge,", "hero_h1_break": "richtig beschafft.",
        "hero_p": "Wir verbinden Präzisionsmaschinenwerkstätten mit den besten Hartmetallwerkzeug-Herstellern Chinas. Technische Spezifikationen, ISO-Qualität, Fabrikdirektpreise — keine Zwischenhändler.",
        "hero_btn1": "Produkte entdecken", "hero_btn2": "So funktioniert's", "hero_btn3": "⚙️ Rechner",
        "hub_label": "🤖 Industrial Intelligence Hub", "hub_h2": "Intelligente Werkzeuge für intelligente Bearbeitung.",
        "hub_p": "Kostenlose, professionelle Rechner und Referenzen, die täglich von Ingenieuren in Fortune-500-Unternehmen genutzt werden.",
        "hub_h3_1": "Schnittgeschwindigkeit- & Vorschub-Rechner", "hub_p_1": "RPM, IPM, Spanbelastung, MRR — optimiert für jede Werkzeug-Material-Kombination.",
        "hub_cta_1": "Jetzt berechnen →",
        "hub_h3_2": "Hartmetall-Sorten-Querverweis", "hub_p_2": "ISO P/M/K/S/H-Sorten vergleichen über Sandvik, Kennametal, Iscar und mehr.",
        "hub_cta_2": "Sorten vergleichen →",
        "hub_h3_3": "Härtekonverter", "hub_p_3": "Sofortige HRC-, HB-, HV- und Zugfestigkeits-Konvertierung für alle Engineering-Materialien.",
        "hub_cta_3": "Jetzt konvertieren →",
        "cat1_name": "Schnittparameter", "cat1_count": "18 Rechner",
        "cat2_name": "Bohren & Gewinde", "cat2_count": "15 Rechner",
        "cat3_name": "Materialien & Sorten", "cat3_count": "17 Rechner",
        "cat4_name": "Kosten, Toleranzen & Ref", "cat4_count": "22+ Rechner",
        "tools_btn": "Rechner & Werkzeuge",
        "tb_label": "🧰 Werkzeugkasten", "tb_h2": "Engineering-Werkzeuge, direkt vor Ort.",
        "tb_p": "Beschleunigen Sie Ihre Angebote und Bearbeitungsentscheidungen mit diesen kostenlosen professionellen Werkzeugen.",
        "tb_h3_1": "Schnittgeschwindigkeit- & Vorschub-Rechner", "tb_p_1": "RPM, IPM, Spanbelastung für Hartmetall-Schaftfräser über 10 Materialgruppen berechnen.",
        "tb_h3_2": "Spanbelastungs-Rechner", "tb_p_2": "Vorschub pro Zahn für maximale MRR und Werkzeuglebensdauer optimieren.",
        "tb_h3_3": "Hartmetall-Sorten-Querverweis", "tb_p_3": "ISO P/M/K/S/H-Sortenvergleich über alle großen Marken.",
        "tb_h3_4": "Härtekonverter", "tb_p_4": "Sofort zwischen HRC, HB, HV und Zugfestigkeit konvertieren.",
        "prod_label": "Produkte", "prod_h2": "Was wir abdecken.",
        "prod_p": "Jede Kategorie von Schneidwerkzeugen für CNC-Bearbeitung, bezogen von geprüften chinesischen Fabriken mit vollständiger QC-Rückverfolgbarkeit.",
        "card_h3_1": "Hartmetall-Schaftfräser", "card_p_1": "Vollhartmetall, 2- bis 6-Nut, AlTiN/TiSiN-Beschichtungen, Eckradius & Kugelnase. HRC bis 65.",
        "card_h3_2": "Wendeeinsätze", "card_p_2": "CNMG, WNMG, TNMG, DCMT — alle Sorten für Stahl, Edelstahl, Aluminium und Superlegierungen.",
        "card_h3_3": "Hartmetallbohrer", "card_p_3": "Vollhartmetall- und indexierbare Bohrer für Bohrarbeiten bis 20×D. Beschichtete und unbeschichtete Optionen.",
        "card_h3_4": "Werkzeughalter", "card_p_4": "BT40, BT30, HSK, SK — Spannzangenfutter, Schaftfräserhalter, ER-Spannzangen, Gewindehalter.",
        "card_h3_5": "Bohren & Reiben", "card_p_5": "Feinbohrköpfe, Hartmetallreibahlen, Patronen-Stil-Bohrstangen für enge Toleranzen.",
        "card_h3_6": "Gewindewerkzeuge", "card_p_6": "Gewindefräser, Hartmetallgewindebohrer, Gewindedreheinsätze für Unified- und Metric-Gewindestandards.",
        "guide_label": "Technische Bibliothek", "guide_h2": "Engineering-Leitfäden.",
        "guide_p": "Detaillierte Analysen von Werkzeuggeometrie, Beschichtungswissenschaft, Materialmetallurgie und Bearbeitungsoptimierung.",
        "guide_h3_1": "Schaftfräser-Geometrie", "guide_p_1": "Nutanzahl, Steigungswinkel, Eckradius, Kern-Durchmesser — wie jede Variable Schnittleistung, Spanabfuhr und Werkzeuglebensdauer beeinflusst.",
        "guide_h3_2": "Hartmetall-Sorten erklärt", "guide_p_2": "Submikron, Ultrafein, Konventionell — welche Korngröße und Bindemittelzusammensetzung für Stahl, Aluminium, Titan und gehärtete Materialien.",
        "guide_h3_3": "Beschichtungsvergleich", "guide_p_3": "AlTiN, TiSiN, TiAlN, AlCrN, diamantähnlicher Kohlenstoff — wann jede Beschichtung wichtig ist, welchen Temperaturbereich sie abdeckt.",
        "guide_h3_4": "Beschaffung aus China", "guide_p_4": "Schritt für Schritt: Lieferanten prüfen, Proben anfordern, MOQs verhandeln, QC-Inspektionen und Logistik verwalten.",
        "trust_label": "Qualitätssicherung", "trust_h2": "Inspektion & Messtechnik.",
        "trust_p": "Jede Charge wird vor Versand verifiziert. Unsere Partnerfabriken sind mit ISO-konformen Inspektions-systemen ausgestattet.",
        "trust_h3_1": "Zeiss CMM", "trust_p_1": "3D-Koordinatenmessung für Maßgenauigkeit bis ±2 μm bei kritischen Geometrien.",
        "trust_h3_2": "SEM + EDS", "trust_p_2": "Rasterelektronenmikroskopie für Schichtdicke, Kornstruktur und Elementaranalyse.",
        "trust_h3_3": "Härteprüfer", "trust_p_3": "Rockwell- und Vickers-Härteverifizierung in jeder Produktionscharge.",
        "trust_h3_4": "Werkzeug-Vorsetzer", "trust_p_4": "Zoller- und Parlec-Vorsetzer für Schneidengeometrie und Laufverifikation.",
        "trust_h3_5": "Beschichtungslabor", "trust_p_5": "In-house PVD- und CVD-Beschichtung mit Dicke-, Haftung- und Härte-Validierung.",
        "trust_h3_6": "ISO 9001:2025", "trust_p_6": "Zertifiziertes Qualitätsmanagementsystem. Volle Charge-Rückverfolgbarkeit mit CoC-Dokumentation.",
        "cta_h2": "Brauchen Sie ein Präzisionsangebot?", "cta_p": "Sagen Sie uns, was Sie bearbeiten — Material, Operation, Mengen, Zieltoleranzen. Wir verbinden Sie mit der richtigen Fabrik innerhalb von 48 Stunden.",
        "cta_btn1": "📩 Präzisionsangebot anfordern", "cta_btn2": "✉️ info@carbide-tooling.com",
        "swipe": "Wischen Sie, um alle Geräte zu sehen →",
        "footer_tagline": "Präzisionsschneidwerkzeuge von Chinas besten Herstellern. Engineering-Support, QC-Verifizierung, Fabrikdirektpreise.",
        "footer_prod": "Produkte", "footer_res": "Ressourcen", "footer_co": "Unternehmen",
        "footer_prod1": "Schaftfräser", "footer_prod2": "Wendeeinsätze", "footer_prod3": "Bohrer",
        "footer_prod4": "Werkzeughalter", "footer_prod5": "Bohrwerkzeuge", "footer_prod6": "Gewindewerkzeuge",
        "footer_res1": "Technische Leitfäden", "footer_res2": "Schnittgeschwindigkeits-Rechner", "footer_res3": "Sorten-Selektor", "footer_res4": "Beschichtungs-Leitfaden",
        "footer_co1": "Über uns", "footer_co2": "Angebot anfordern", "footer_co3": "Kontakt",
        "footer_copy": "© 2026 Carbide Tooling. Präzisionsbeschaffung für Präzisionsbearbeitung.",
        "nav_home": "Startseite", "nav_prod": "Produkte", "nav_tools": "Werkzeuge", "nav_guides": "Anleitungen", "nav_about": "Über uns", "nav_quote": "📩 Angebot anfordern",
        "img_alt_hero": "Präzisions-Hartmetall-Schneidwerkzeuge", "img_alt_endmill": "Hartmetall-Schaftfräser", "img_alt_insert": "Wendeeinsätze",
        "img_alt_drill": "Hartmetallbohrer", "img_alt_holder": "Werkzeughalter", "img_alt_boring": "Bohr- und Reibwerkzeuge", "img_alt_thread": "Gewindewerkzeuge",
    }
    
    # Japanese
    t_data["jp"] = {
        "lang_code": "ja", "prefix": "/jp/",
        "title": "Carbide Tooling — 精密CNC切削工具（中国調達） | エンドミル、インサート、ツールホルダー",
        "desc": "中国の大手メーカーから調達したプレミアム超硬エンドミル、旋回インサート、ドリル、ツールホルダー。工場直販価格、ISO品質、エンジニアリングサポート。",
        "og_desc": "中国最高のメーカーから調達したプレミアム超硬切削工具。工場直販価格、ISO品質、エンジニアリングサポート — 中間業者なし。",
        "og_title": "超硬工具 — 精密CNC切削工具",
        "hero_h1": "切削工具、", "hero_h1_break": "適正調達。",
        "hero_p": "精密機械工場と中国の最高の超硬工具メーカーを結びます。技術仕様、ISO品質、工場直販価格 — 中間業者なし。",
        "hero_btn1": "製品を見る", "hero_btn2": "仕組み", "hero_btn3": "⚙️ 計算機",
        "hub_label": "🤖 インテリジェントハブ", "hub_h2": "スマートな加工に、スマートな工具。",
        "hub_p": "Fortune 500のエンジニアが毎日使用する無料・プロフェッショナルグレードの計算機と参考文献。",
        "hub_h3_1": "切削速度・送り計算機", "hub_p_1": "RPM、IPM、チップ負荷、MRR — ツールと素材の組み合わせに最適化。",
        "hub_cta_1": "今すぐ計算 →",
        "hub_h3_2": "超硬グレード相互参照", "hub_p_2": "Sandvik、Kennametal、IscarなどのISO P/M/K/S/Hグレードを比較。",
        "hub_cta_2": "グレードを比較 →",
        "hub_h3_3": "硬度変換器", "hub_p_3": "すべてのエンジニアリング材料のHRC、HB、HV、引張強度の即時変換。",
        "hub_cta_3": "今すぐ変換 →",
        "cat1_name": "切削パラメータ", "cat1_count": "18 計算機",
        "cat2_name": "穴あけ & タップ", "cat2_count": "15 計算機",
        "cat3_name": "材料 & グレード", "cat3_count": "17 計算機",
        "cat4_name": "コスト・公差・参考", "cat4_count": "22+ 計算機",
        "tools_btn": "計算機 & ツール",
        "tb_label": "🧰 ツールボックス", "tb_h2": "エンジニアリングツール、すぐ手元に。",
        "tb_p": "これらの無料プロフェッショナルツールで、見積りと加工判断を加速。",
        "tb_h3_1": "切削速度・送り計算機", "tb_p_1": "10種の材料グループに対応する超硬エンドミルのRPM、IPM、チップ負荷を計算。",
        "tb_h3_2": "チップ負荷計算機", "tb_p_2": "最大MRRと工具寿命のための歯当たり送りを最適化。",
        "tb_h3_3": "超硬グレード相互参照", "tb_p_3": "すべての主要ブランドのISO P/M/K/S/Hグレード比較。",
        "tb_h3_4": "硬度変換器", "tb_p_4": "HRC、HB、HV、引張強度間の即時変換。",
        "prod_label": "製品", "prod_h2": "対象カテゴリー。",
        "prod_p": "CNC加工で使用されるすべての切削工具カテゴリー。QC完全トレーサビリティの審査済み中国工場からの調達。",
        "card_h3_1": "超硬エンドミル", "card_p_1": "全超硬、2～6フルート、AlTiN/TiSiNコーティング、コーナーR & ボールノーズ。HRC65まで対応。",
        "card_h3_2": "旋回インサート", "card_p_2": "CNMG、WNMG、TNMG、DCMT — 鋼、ステンレス、アルミ、超合金用の全グレード。",
        "card_h3_3": "超硬ドリル", "card_p_3": "全超硬およびインデックスドリル。20×Dまでの穴あけ用。コーティング・未コーティングオプション。",
        "card_h3_4": "ツールホルダー", "card_p_4": "BT40、BT30、HSK、SK — コレットチャック、エンドミルホルダー、ERコレット、タップホルダー。",
        "card_h3_5": "ボーリング & リーミング", "card_p_5": "微細ボーリングヘッド、超硬リーマ、カートリッジ式ボーリングバーで高精度公差対応。",
        "card_h3_6": "ねじ切り工具", "card_p_6": "ねじ切りフライス、超硬タップ、ユニファイドおよびメトリックねじ規格用のねじ旋回インサート。",
        "guide_label": "技術ライブラリ", "guide_h2": "エンジニアリングガイド。",
        "guide_p": "工具形状、コーティング科学、材料冶金、加工最適化の詳細解説。",
        "guide_h3_1": "エンドミル形状ガイド", "guide_p_1": "フルート数、ヘリカル角、コーナーR、コア径 — 各変数が切削性能、チップ排出、工具寿命にどう影響するか。",
        "guide_h3_2": "超硬グレード解説", "guide_p_2": "サブミクロン、超微細、従来型 — 鋼、アルミ、チタン、硬質材料にどの粒度と結合材組成を使用するか。",
        "guide_h3_3": "コーティング比較", "guide_p_3": "AlTiN、TiSiN、TiAlN、AlCrN、DLC — それぞれのコーティングが重要な場面、対応温度範囲、コスト。",
        "guide_h3_4": "中国からの調達", "guide_p_4": "ステップバイステップ：サプライヤ審査、サンプル依頼、MOQ交渉、QC検査・物流管理。",
        "trust_label": "品質保証", "trust_h2": "検査 & 測定技術。",
        "trust_p": "各ロットは出荷前に検証済み。提携工場はISO準拠の検査システムを完備。",
        "trust_h3_1": "Zeiss CMM", "trust_p_1": "重要形状の寸法精度±2 μmまでの3D座標測定。",
        "trust_h3_2": "SEM + EDS", "trust_p_2": "コーティング厚さ、粒構造、元素分析のための走査型電子顕微鏡。",
        "trust_h3_3": "硬度テスター", "trust_p_3": "各生産ロットのロックウェルおよびビッカース硬度検証。",
        "trust_h3_4": "ツールプリセッター", "trust_p_4": "Zoller・Parlecプリセッターで切削刃形状と振れ検証。",
        "trust_h3_5": "コーティングラボ", "trust_p_5": "社内PVD・CVDコーティング。厚さ、接着力、硬度のバリデーション。",
        "trust_h3_6": "ISO 9001:2025", "trust_p_6": "認証品質管理システム。CoC文書による完全ロットトレーサビリティ。",
        "cta_h2": "精密見積りが必要ですか？", "cta_p": "加工内容をお知らせください — 材料、加工、数量、目標公差。48時間以内に適切な工場をご紹介。",
        "cta_btn1": "📩 精密見積りを取得", "cta_btn2": "✉️ info@carbide-tooling.com",
        "swipe": "全装置を見るにはスワイプ →",
        "footer_tagline": "中国最高メーカーの精密切削工具。エンジニアリングサポート、QC検証、工場直販価格。",
        "footer_prod": "製品", "footer_res": "リソース", "footer_co": "企業情報",
        "footer_prod1": "エンドミル", "footer_prod2": "旋回インサート", "footer_prod3": "ドリル",
        "footer_prod4": "ツールホルダー", "footer_prod5": "ボーリング工具", "footer_prod6": "ねじ切り工具",
        "footer_res1": "技術ガイド", "footer_res2": "切削速度計算機", "footer_res3": "グレードセレクター", "footer_res4": "コーティングガイド",
        "footer_co1": "会社概要", "footer_co2": "見積りを取得", "footer_co3": "お問い合わせ",
        "footer_copy": "© 2026 Carbide Tooling. 精密加工に精密調達。",
        "nav_home": "ホーム", "nav_prod": "製品", "nav_tools": "ツール", "nav_guides": "ガイド", "nav_about": "会社概要", "nav_quote": "📩 見積り",
        "img_alt_hero": "精密超硬切削工具", "img_alt_endmill": "超硬エンドミル", "img_alt_insert": "旋回インサート",
        "img_alt_drill": "超硬ドリル", "img_alt_holder": "ツールホルダー", "img_alt_boring": "ボーリング・リーミング工具", "img_alt_thread": "ねじ切り工具",
    }
    
    # Spanish
    t_data["es"] = {
        "lang_code": "es", "prefix": "/es/",
        "title": "Carbide Tooling — Herramientas de corte CNC de precisión desde China | Fresas, insertos, portaherramientas",
        "desc": "Fresas de carburo premium, insertos de torneado, brocas y portaherramientas de los principales fabricantes de China. Precios directos de fábrica, calidad ISO, soporte técnico.",
        "og_desc": "Herramientas de corte de carburo premium de los mejores fabricantes de China. Precios directos de fábrica, calidad ISO, soporte técnico — sin intermediarios.",
        "og_title": "Herramientas de Carburo — Herramientas de corte CNC de precisión",
        "hero_h1": "Herramientas de corte,", "hero_h1_break": "bien adquiridas.",
        "hero_p": "Conectamos talleres de mecanizado de precisión con los mejores fabricantes de herramientas de carburo de China. Especificaciones técnicas, calidad ISO, precios directos de fábrica — sin intermediarios.",
        "hero_btn1": "Explorar productos", "hero_btn2": "Cómo funciona", "hero_btn3": "⚙️ Calculadora",
        "hub_label": "🤖 Centro de Inteligencia Industrial", "hub_h2": "Herramientas inteligentes para mecanizado inteligente.",
        "hub_p": "Calculadoras y referencias profesionales gratuitas utilizadas por ingenieros de Fortune 500 cada día.",
        "hub_h3_1": "Calculadora de velocidad y avance", "hub_p_1": "RPM, IPM, carga de viruta, MRR — optimizado para cualquier combinación de herramienta-material.",
        "hub_cta_1": "Calcular ahora →",
        "hub_h3_2": "Referencia cruzada de grados de carburo", "hub_p_2": "Comparar grados ISO P/M/K/S/H en Sandvik, Kennametal, Iscar y más.",
        "hub_cta_2": "Comparar grados →",
        "hub_h3_3": "Convertidor de dureza", "hub_p_3": "Conversiones instantáneas de HRC, HB, HV y resistencia a la tracción para todos los materiales de ingeniería.",
        "hub_cta_3": "Convertir ahora →",
        "cat1_name": "Parámetros de corte", "cat1_count": "18 calculadoras",
        "cat2_name": "Perforación y roscado", "cat2_count": "15 calculadoras",
        "cat3_name": "Materiales y grados", "cat3_count": "17 calculadoras",
        "cat4_name": "Costes, tolerancias y ref", "cat4_count": "22+ calculadoras",
        "tools_btn": "Calculadoras & Herramientas",
        "tb_label": "🧰 Caja de herramientas", "tb_h2": "Herramientas de ingeniería, en su sitio.",
        "tb_p": "Acelere sus decisiones de cotización y mecanizado con estas herramientas profesionales gratuitas.",
        "tb_h3_1": "Calculadora de velocidad y avance", "tb_p_1": "Calcule RPM, IPM, carga de viruta para fresas de carburo en 10 grupos de materiales.",
        "tb_h3_2": "Calculadora de carga de viruta", "tb_p_2": "Optimice avance por diente para máximo MRR y vida de herramienta.",
        "tb_h3_3": "Referencia cruzada de grados", "tb_p_3": "Comparación de grados ISO P/M/K/S/H de todas las marcas principales.",
        "tb_h3_4": "Convertidor de dureza", "tb_p_4": "Convierta instantáneamente entre HRC, HB, HV y resistencia a la tracción.",
        "prod_label": "Productos", "prod_h2": "Lo que cubrimos.",
        "prod_p": "Todas las categorías de herramientas de corte para mecanizado CNC, adquiridas de fábricas chinas auditadas con trazabilidad QC completa.",
        "card_h3_1": "Fresas de carburo", "card_p_1": "Carburo sólido, 2 a 6 flautas, recubrimientos AlTiN/TiSiN, radio de esquina y nariz de bola. HRC hasta 65.",
        "card_h3_2": "Insertos de torneado", "card_p_2": "CNMG, WNMG, TNMG, DCMT — todos los grados para acero, inoxidable, aluminio y superaleaciones.",
        "card_h3_3": "Brocas de carburo", "card_p_3": "Brocas de carburo sólido e indexables para perforación hasta 20×D.",
        "card_h3_4": "Portaherramientas", "card_p_4": "BT40, BT30, HSK, SK — mandriles, portafresas, cojinetes ER, portarroscas.",
        "card_h3_5": "Mandrinado y escariado", "card_p_5": "Cabezas de mandrinado fino, escariadores de carburo, barras tipo cartucho para tolerancias estrechas.",
        "card_h3_6": "Herramientas de roscado", "card_p_6": "Fresas de rosca, machos de carburo, insertos de torneado de rosca para estándares unified y métricos.",
        "guide_label": "Biblioteca técnica", "guide_h2": "Guías de ingeniería.",
        "guide_p": "Análisis detallados de geometría de herramientas, ciencia de recubrimientos, metalurgia de materiales y optimización de mecanizado.",
        "guide_h3_1": "Guía de geometría de fresas", "guide_p_1": "Número de flautas, ángulo de hélice, radio de esquina, diámetro del núcleo — cómo cada variable afecta el rendimiento.",
        "guide_h3_2": "Grados de carburo explicados", "guide_p_2": "Submicrón, ultrafino, convencional — qué tamaño de grano y composición usar para cada material.",
        "guide_h3_3": "Comparación de recubrimientos", "guide_p_3": "AlTiN, TiSiN, TiAlN, AlCrN, DLC — cuando importa cada recubrimiento y qué temperatura maneja.",
        "guide_h3_4": "Abastecimiento desde China", "guide_p_4": "Paso a paso: evaluación de proveedores, solicitud de muestras, negociación de MOQs, QC y logística.",
        "trust_label": "Garantía de calidad", "trust_h2": "Inspección y metrología.",
        "trust_p": "Cada lote se verifica antes del envío. Fábricas asociadas con sistemas de inspección compliantes con ISO.",
        "trust_h3_1": "Zeiss CMM", "trust_p_1": "Medición de coordenadas 3D para precisión de ±2 μm en geometrías críticas.",
        "trust_h3_2": "SEM + EDS", "trust_p_2": "Microscopía electrónica de barrido para espesor de recubrimiento y análisis elemental.",
        "trust_h3_3": "Probador de dureza", "trust_p_3": "Verificación de dureza Rockwell y Vickers en cada lote de producción.",
        "trust_h3_4": "Presetter de herramientas", "trust_p_4": "Presetters Zoller y Parlec para verificación de geometría de filo y desviación.",
        "trust_h3_5": "Laboratorio de recubrimientos", "trust_p_5": "Recubrimiento PVD y CVD in-house con validación de espesor, adhesión y dureza.",
        "trust_h3_6": "ISO 9001:2025", "trust_p_6": "Sistema de gestión de calidad certificado. Trazabilidad completa con documentación CoC.",
        "cta_h2": "¿Necesita una cotización de precisión?", "cta_p": "Díganos qué procesa — material, operación, cantidades, tolerancias. Conectaremos con la fábrica adecuada en 48 horas.",
        "cta_btn1": "📩 Obtener cotización de precisión", "cta_btn2": "✉️ info@carbide-tooling.com",
        "swipe": "Deslice para ver todos los equipos →",
        "footer_tagline": "Herramientas de corte de precisión de los mejores fabricantes de China. Soporte técnico, verificación QC, precios directos.",
        "footer_prod": "Productos", "footer_res": "Recursos", "footer_co": "Empresa",
        "footer_prod1": "Fresas", "footer_prod2": "Insertos de torneado", "footer_prod3": "Brocas",
        "footer_prod4": "Portaherramientas", "footer_prod5": "Herramientas de mandrinado", "footer_prod6": "Herramientas de roscado",
        "footer_res1": "Guías técnicas", "footer_res2": "Calculadora de velocidad", "footer_res3": "Selector de grados", "footer_res4": "Guía de recubrimientos",
        "footer_co1": "Sobre nosotros", "footer_co2": "Obtener cotización", "footer_co3": "Contacto",
        "footer_copy": "© 2026 Carbide Tooling. Abastecimiento de precisión para mecanizado de precisión.",
        "nav_home": "Inicio", "nav_prod": "Productos", "nav_tools": "Herramientas", "nav_guides": "Guías", "nav_about": "Sobre nosotros", "nav_quote": "📩 Cotización",
        "img_alt_hero": "Herramientas de corte de carburo de precisión", "img_alt_endmill": "Fresas de carburo", "img_alt_insert": "Insertos de torneado",
        "img_alt_drill": "Brocas de carburo", "img_alt_holder": "Portaherramientas", "img_alt_boring": "Herramientas de mandrinado y escariado", "img_alt_thread": "Herramientas de roscado",
    }
    
    # Vietnamese
    t_data["vi"] = {
        "lang_code": "vi", "prefix": "/vi/",
        "title": "Carbide Tooling — Dụng cụ cắt CNC chính xác từ Trung Quốc | Dao phay, chèn, gá dụng cụ",
        "desc": "Dao phay cacbua cao cấp, chèn tiện, mũi khoan và gá dụng cụ từ các nhà sản xuất hàng đầu Trung Quốc. Giá trực tiếp từ nhà máy, chất lượng ISO, hỗ trợ kỹ thuật.",
        "og_desc": "Dụng cụ cắt cacbua cao cấp từ các nhà sản xuất tốt nhất Trung Quốc. Giá trực tiếp từ nhà máy, chất lượng ISO, hỗ trợ kỹ thuật — không qua trung gian.",
        "og_title": "Dụng cụ Cacbua — Dụng cụ cắt CNC chính xác",
        "hero_h1": "Dụng cụ cắt,", "hero_h1_break": "tìm nguồn phù hợp.",
        "hero_p": "Chúng tôi kết nối xưởng gia công chính xác với các nhà sản xuất dụng cụ cacbua tốt nhất Trung Quốc. Thông số kỹ thuật, chất lượng ISO, giá trực tiếp từ nhà máy — không qua trung gian.",
        "hero_btn1": "Khám phá sản phẩm", "hero_btn2": "Cách hoạt động", "hero_btn3": "⚙️ Máy tính",
        "hub_label": "🤖 Trung tâm Tính toán Công nghiệp", "hub_h2": "Công cụ thông minh cho gia công thông minh.",
        "hub_p": "Máy tính và tài liệu tham khảo chuyên nghiệp miễn phí được sử dụng bởi các kỹ sư Fortune 500 mỗi ngày.",
        "hub_h3_1": "Máy tính tốc độ & lượng ăn dao", "hub_p_1": "RPM, IPM, tải phoi, MRR — tối ưu cho mọi tổ hợp dụng cụ-vật liệu.",
        "hub_cta_1": "Tính ngay →",
        "hub_h3_2": "Tham chiếu chéo cấp độ cacbua", "hub_p_2": "So sánh cấp độ ISO P/M/K/S/H trên Sandvik, Kennametal, Iscar và hơn thế nữa.",
        "hub_cta_2": "So sánh cấp độ →",
        "hub_h3_3": "Bộ chuyển đổi độ cứng", "hub_p_3": "Chuyển đổi tức thời HRC, HB, HV và độ bền kéo cho tất cả vật liệu kỹ thuật.",
        "hub_cta_3": "Chuyển đổi ngay →",
        "cat1_name": "Tham số cắt", "cat1_count": "18 máy tính",
        "cat2_name": "Khoan & Taro", "cat2_count": "15 máy tính",
        "cat3_name": "Vật liệu & Cấp độ", "cat3_count": "17 máy tính",
        "cat4_name": "Chi phí, dung sai & Tham khảo", "cat4_count": "22+ máy tính",
        "tools_btn": "Máy Tính & Công Cụ",
        "tb_label": "🧰 Hộp dụng cụ", "tb_h2": "Dụng cụ kỹ thuật, ngay tại trang.",
        "tb_p": "Tăng tốc quyết định báo giá và gia công với các công cụ chuyên nghiệp miễn phí này.",
        "tb_h3_1": "Máy tính tốc độ & lượng ăn dao", "tb_p_1": "Tính RPM, IPM, tải phoi cho dao phay cacbua trên 10 nhóm vật liệu.",
        "tb_h3_2": "Máy tính tải phoi", "tb_p_2": "Tối ưu lượng ăn dao mỗi răng cho MRR tối đa và tuổi thọ dụng cụ.",
        "tb_h3_3": "Tham chiếu chéo cấp độ cacbua", "tb_p_3": "So sánh cấp độ ISO P/M/K/S/H của tất cả thương hiệu lớn.",
        "tb_h3_4": "Bộ chuyển đổi độ cứng", "tb_p_4": "Chuyển đổi tức thời giữa HRC, HB, HV và độ bền kéo.",
        "prod_label": "Sản phẩm", "prod_h2": "Những gì chúng tôi bao phủ.",
        "prod_p": "Mọi danh mục dụng cụ cắt cho gia công CNC, nguồn cung từ nhà máy Trung Quốc đã kiểm định.",
        "card_h3_1": "Dao phay cacbua", "card_p_1": "Carbua rắn, 2 đến 6 cánh, lớp phủ AlTiN/TiSiN, bán kính góc & đầu cầu. HRC lên đến 65.",
        "card_h3_2": "Chèn tiện", "card_p_2": "CNMG, WNMG, TNMG, DCMT — tất cả cấp độ cho thép, inox, nhôm và siêu hợp kim.",
        "card_h3_3": "Mũi khoan cacbua", "card_p_3": "Mũi khoan cacbua rắn và có thể thay thế cho khoan lỗ đến 20×D.",
        "card_h3_4": "Gá dụng cụ", "card_p_4": "BT40, BT30, HSK, SK — kẹp collet, gá dao phay, collet ER, gá taro.",
        "card_h3_5": "Khoan & Doa", "card_p_5": "Đầu khoan tinh, doa cacbua, thanh khoan kiểu cartridge cho dung sai hẹp.",
        "card_h3_6": "Dụng cụ taro", "card_p_6": "Dao phay ren, taro cacbua, chèn tiện ren cho tiêu chuẩn unified và metric.",
        "guide_label": "Thư viện kỹ thuật", "guide_h2": "Hướng dẫn kỹ thuật.",
        "guide_p": "Phân tích chi tiết về hình học dụng cụ, khoa học lớp phủ, luyện kim vật liệu và tối ưu gia công.",
        "guide_h3_1": "Hướng dẫn hình học dao phay", "guide_p_1": "Số cánh, góc hélice, bán kính góc, đường kính lõi — cách mỗi biến số ảnh hưởng hiệu suất cắt.",
        "guide_h3_2": "Cấp độ cacbua giải thích", "guide_p_2": "Submicron, ultrafine, thông thường — kích thước hạt và chất kết dính nào cho từng vật liệu.",
        "guide_h3_3": "So sánh lớp phủ", "guide_p_3": "AlTiN, TiSiN, TiAlN, AlCrN, DLC — khi lớp phủ nào quan trọng, phạm vi nhiệt độ và chi phí.",
        "guide_h3_4": "Nguồn cung từ Trung Quốc", "guide_p_4": "Từng bước: đánh giá nhà cung cấp, yêu cầu mẫu, đàm phán MOQ, quản lý QC và logistics.",
        "trust_label": "Đảm bảo chất lượng", "trust_h2": "Kiểm tra & đo lường.",
        "trust_p": "Mỗi lô được xác minh trước khi gửi. Nhà máy đối tác trang bị hệ thống kiểm tra tuân thủ ISO.",
        "trust_h3_1": "Zeiss CMM", "trust_p_1": "Đo tọa độ 3D cho độ chính xác ±2 μm trên hình học quan trọng.",
        "trust_h3_2": "SEM + EDS", "trust_p_2": "Kính hiển vi điện tử quét cho độ dày lớp phủ và phân tích nguyên tố.",
        "trust_h3_3": "Máy đo độ cứng", "trust_p_3": "Kiểm tra độ cứng Rockwell và Vickers trên mỗi lô sản xuất.",
        "trust_h3_4": "Máy đặt trước dụng cụ", "trust_p_4": "Máy đặt trước Zoller và Parlec cho hình học lưỡi cắt và xác minh lệch.",
        "trust_h3_5": "Phòng lớp phủ", "trust_p_5": "Lớp phủ PVD và CVD tại chỗ với xác minh độ dày, độ bám và độ cứng.",
        "trust_h3_6": "ISO 9001:2025", "trust_p_6": "Hệ thống quản lý chất lượng được chứng nhận. Theo dõi lô đầy đủ với tài liệu CoC.",
        "cta_h2": "Bạn cần báo giá chính xác?", "cta_p": "Cho chúng tôi biết bạn đang gia công gì — vật liệu, thao tác, số lượng, dung sai mục tiêu. 48 giờ kết nối nhà máy phù hợp.",
        "cta_btn1": "📩 Nhận báo giá chính xác", "cta_btn2": "✉️ info@carbide-tooling.com",
        "swipe": "Vuốt để xem tất cả thiết bị →",
        "footer_tagline": "Dụng cụ cắt chính xác từ các nhà sản xuất tốt nhất Trung Quốc. Hỗ trợ kỹ thuật, xác minh QC, giá trực tiếp nhà máy.",
        "footer_prod": "Sản phẩm", "footer_res": "Tài nguyên", "footer_co": "Công ty",
        "footer_prod1": "Dao phay", "footer_prod2": "Chèn tiện", "footer_prod3": "Mũi khoan",
        "footer_prod4": "Gá dụng cụ", "footer_prod5": "Dụng cụ khoan", "footer_prod6": "Dụng cụ taro",
        "footer_res1": "Hướng dẫn kỹ thuật", "footer_res2": "Máy tính tốc độ", "footer_res3": "Bộ chọn cấp độ", "footer_res4": "Hướng dẫn lớp phủ",
        "footer_co1": "Về chúng tôi", "footer_co2": "Nhận báo giá", "footer_co3": "Liên hệ",
        "footer_copy": "© 2026 Carbide Tooling. Nguồn cung chính xác cho gia công chính xác.",
        "nav_home": "Trang chủ", "nav_prod": "Sản phẩm", "nav_tools": "Công cụ", "nav_guides": "Hướng dẫn", "nav_about": "Về chúng tôi", "nav_quote": "📩 Báo giá",
        "img_alt_hero": "Dụng cụ cắt cacbua chính xác", "img_alt_endmill": "Dao phay cacbua", "img_alt_insert": "Chèn tiện",
        "img_alt_drill": "Mũi khoan cacbua", "img_alt_holder": "Gá dụng cụ", "img_alt_boring": "Dụng cụ khoan & doa", "img_alt_thread": "Dụng cụ taro",
    }
    
    translations_file.write_text(json.dumps(t_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("✅ Translations JSON file written")

# Load translations
translations = json.loads(translations_file.read_text(encoding="utf-8"))

# ── MAIN ──
print("=== Carbide Site v3 — Step 1: Button + Homepage Rewrite ===")
fix_button_text()
fix_en_homepage()
for lang in ["de", "jp", "es", "vi"]:
    build_homepage_file(lang, translations[lang])

print()
print("=== Done — Step 1 complete ===")
