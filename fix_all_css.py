#!/usr/bin/env python3
"""Fix all CSS corruption in tool pages - clean rebuild of style blocks + nav HTML."""

import os, re

ROOT = "/Users/nicky/ZCodeProject/carbide-site"

# ============================================================
# CLEAN CSS BLOCKS (pristine, no corruption)
# ============================================================

NAV_V2_STYLE = '''<style id="nav-v2-style">
/* ── Apple Smart Nav v2 ── */
nav#nav-v2{position:sticky;top:0;z-index:100;background:rgba(255,255,255,.88);backdrop-filter:saturate(180%) blur(24px);-webkit-backdrop-filter:saturate(180%) blur(24px);border-bottom:1px solid rgba(0,0,0,.06);height:48px;display:flex;align-items:center}
nav#nav-v2 .nv-inner{display:flex;align-items:center;justify-content:space-between;width:100%;max-width:1100px;margin:0 auto;padding:0 24px}
nav#nav-v2 .nv-logo{font-size:14px;font-weight:700;letter-spacing:-.3px;color:#1d1d1f;text-decoration:none;display:flex;align-items:center;gap:6px;white-space:nowrap;flex-shrink:0}
nav#nav-v2 .nv-logo span{font-weight:800;color:#0066cc}
nav#nav-v2 .nv-links{display:flex;align-items:center;gap:0;flex-shrink:0}
nav#nav-v2 .nv-links>a{color:#1d1d1f;text-decoration:none;padding:0 14px;height:48px;display:flex;align-items:center;font-weight:500;font-size:12px;transition:color .15s;white-space:nowrap}
nav#nav-v2 .nv-links>a:hover{color:#0066cc}
nav#nav-v2 .nv-lang{position:relative;display:flex;align-items:center}
nav#nav-v2 .nv-right{display:flex;align-items:center;gap:8px;flex-shrink:0}
nav#nav-v2 .nv-quote{display:inline-flex;align-items:center;background:#0066cc;color:#fff;padding:6px 16px;border-radius:24px;font-size:11px;font-weight:600;text-decoration:none;transition:all .2s;white-space:nowrap}
nav#nav-v2 .nv-quote:hover{background:#0055aa;transform:translateY(-1px);box-shadow:0 4px 12px rgba(0,102,204,.25)}
@media(max-width:768px){
  nav#nav-v2 .nv-inner{flex-wrap:wrap;padding:10px 16px;gap:4px;align-items:center}
  nav#nav-v2 .nv-logo{font-size:14px;order:0;flex-shrink:0;margin-right:auto}
  nav#nav-v2 .nv-right{order:1;flex-shrink:0;width:auto;gap:6px}
  nav#nav-v2 .nv-links{display:flex;align-items:center;gap:0;flex-wrap:wrap;order:2;width:100%;justify-content:center;margin-top:2px;padding-top:2px;border-top:1px solid #f0f0f0}
  nav#nav-v2 .nv-links>a{padding:6px 12px;font-size:11px;height:auto;font-weight:500}
  nav#nav-v2 .nv-lang{position:relative!important}
  nav#nav-v2 .lang-dd{right:-30px;min-width:130px}
  nav#nav-v2 .nv-quote{padding:4px 10px;font-size:10px}
}
nav#nav-v2{font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif!important}
.lang-btn{display:flex;align-items:center;gap:4px;padding:4px 10px;border-radius:20px;background:#f5f5f7;border:1px solid #e8e8ed;font-size:12px;font-weight:600;color:#1d1d1f;cursor:pointer;transition:all .2s;position:relative;user-select:none;letter-spacing:.3px}
.lang-btn:hover{background:#e8e8ed;border-color:#d2d2d7}
.lang-btn .flag{font-size:14px;line-height:1}
.lang-btn .caret{font-size:8px;opacity:.5;margin-left:2px}
.lang-dd{display:none;position:absolute;top:calc(100% + 6px);right:0;background:#fff;border:1px solid #e8e8ed;border-radius:12px;box-shadow:0 8px 30px rgba(0,0,0,.12);padding:6px;z-index:300;min-width:140px}
.lang-dd.open{display:block;animation:ddIn .15s ease}
@keyframes ddIn{from{opacity:0;transform:translateY(-4px)}to{opacity:1;transform:translateY(0)}}
.lang-dd a{display:flex;align-items:center;gap:8px;padding:8px 12px;border-radius:8px;text-decoration:none;font-size:13px;color:#1d1d1f;transition:background .15s;white-space:nowrap;font-weight:500}
.lang-dd a:hover{background:#f5f5f7}
.lang-dd a.current{color:#0066cc;font-weight:700;background:#f0f7ff}
.lang-dd a .flag{font-size:18px;line-height:1}
.lang-dd a .lbl{font-weight:600;letter-spacing:.3px}
.lang-dd a .nm{font-weight:400;color:#86868b;font-size:11px;margin-left:auto}
</style>'''

HERO_ATMO_STYLE = '''<style id="hero-atmo-style">
.hero-atmo{position:relative;width:100%;height:200px;overflow:hidden;background:linear-gradient(180deg,#f5f5f7 0%,#e8e8ed 40%,#d2d2d7 100%);margin-bottom:-60px;z-index:0}
.hero-atmo::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 80% 60% at 20% 50%,rgba(0,102,204,.06) 0%,transparent 50%),radial-gradient(ellipse 60% 80% at 80% 40%,rgba(0,0,0,.04) 0%,transparent 50%),linear-gradient(180deg,rgba(255,255,255,0) 0%,rgba(255,255,255,.95) 90%,#fff 100%)}
.hero-atmo::after{content:'';position:absolute;bottom:0;left:0;right:0;height:80px;background:linear-gradient(0deg,#fff 0%,transparent 100%)}
.img-container{width:100%;aspect-ratio:1;background:#fff;border-radius:20px;border:1px solid #d2d2d7;overflow:hidden;display:flex;align-items:center;justify-content:center;position:relative}
.img-container img{width:100%;height:100%;object-fit:cover}
.img-placeholder{width:100%;height:100%;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#f0f0f3 0%,#e8e8ed 50%,#f0f0f3 100%);color:#c0c0c6;font-size:48px}
.img-placeholder::after{content:'\\25C6';font-size:48px;opacity:.3}
</style>'''

HERO_IMG_STYLE = '''<style id="hero-img-style">
.hero-img-wrapper{background:#f5f5f7;border-radius:24px;overflow:hidden;position:relative;aspect-ratio:16/9;max-height:320px;margin:0 auto 24px;box-shadow:0 2px 12px rgba(0,0,0,.06)}
.hero-img-wrapper img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .4s ease}
.hero-img-wrapper:hover img{transform:scale(1.03)}
.hero-img-wrapper .img-overlay{position:absolute;bottom:0;left:0;right:0;height:40%;background:linear-gradient(transparent,rgba(0,0,0,.12));pointer-events:none}
</style>'''


# ============================================================
# LANGUAGE NAV DATA
# ============================================================

LANG_DATA = {
    "en": {
        "code": "en", "flag": "🇺🇸", "label": "EN", "full": "English",
        "links": [
            ("/products/", "Products"),
            ("/tools/", "Calculators &amp; Tools"),
            ("/guides/", "Guides"),
            ("/about.html", "About"),
        ],
        "prefix": "",
        "quote": "📩 Get a Quote",
        "quote_url": "/quote.html",
    },
    "de": {
        "code": "de", "flag": "🇩🇪", "label": "DE", "full": "Deutsch",
        "links": [
            ("/de/products/", "Produkte"),
            ("/de/tools/", "Rechner &amp; Werkzeuge"),
            ("/de/guides/", "Anleitungen"),
            ("/de/about.html", "Über uns"),
        ],
        "prefix": "/de",
        "quote": "📩 Angebot",
        "quote_url": "/de/quote.html",
    },
    "jp": {
        "code": "jp", "flag": "🇯🇵", "label": "JP", "full": "日本語",
        "links": [
            ("/jp/products/", "製品"),
            ("/jp/tools/", "計算機 &amp; ツール"),
            ("/jp/guides/", "ガイド"),
            ("/jp/about.html", "会社概要"),
        ],
        "prefix": "/jp",
        "quote": "📩 見積依頼",
        "quote_url": "/jp/quote.html",
    },
    "es": {
        "code": "es", "flag": "🇪🇸", "label": "ES", "full": "Español",
        "links": [
            ("/es/products/", "Productos"),
            ("/es/tools/", "Calculadoras &amp; Herramientas"),
            ("/es/guides/", "Guías"),
            ("/es/about.html", "Acerca de"),
        ],
        "prefix": "/es",
        "quote": "📩 Cotización",
        "quote_url": "/es/quote.html",
    },
    "vi": {
        "code": "vi", "flag": "🇻🇳", "label": "VI", "full": "Tiếng Việt",
        "links": [
            ("/vi/products/", "Sản phẩm"),
            ("/vi/tools/", "Máy Tính &amp; Công Cụ"),
            ("/vi/guides/", "Hướng dẫn"),
            ("/vi/about.html", "Giới thiệu"),
        ],
        "prefix": "/vi",
        "quote": "📩 Báo giá",
        "quote_url": "/vi/quote.html",
    },
}

ALL_LANGS = [
    ("en", "🇺🇸", "EN", "English"),
    ("de", "🇩🇪", "DE", "Deutsch"),
    ("jp", "🇯🇵", "JP", "日本語"),
    ("es", "🇪🇸", "ES", "Español"),
    ("vi", "🇻🇳", "VI", "Tiếng Việt"),
]


def build_lang_dropdown(current_lang, tool_path):
    """Build the language dropdown HTML for a tool page."""
    # tool_path is like /tools/speed-feed/ (without language prefix)
    # current_lang is like "en", "de", "jp", "es", "vi"
    parts = []
    for d in ALL_LANGS:
        code = d[0]
        
        if code == "en":
            href = tool_path
        else:
            href = "/" + code + tool_path
        
        if current_lang == "en":
            # If currently on EN, adjust other lang paths
            pass  # Already correct above
        else:
            # If currently on non-EN, adjust the current lang path to include prefix
            if code == current_lang:
                href = "/" + current_lang + tool_path
            # For EN: just use tool_path (already set)
            # For other langs: href is already /{code}{tool_path}
        
        css_class = "current" if code == current_lang else ""
        parts.append(f'<a href="{href}" class="{css_class}"><span class="flag">{d[1]}</span><span class="lbl">{d[2]}</span><span class="nm">{d[3]}</span></a>')
    
    return "".join(parts)


def build_nav_html(lang_code, tool_path):
    """Build the complete <nav> HTML block for a given language."""
    ld = LANG_DATA[lang_code]
    
    # Build nav links
    nav_links = "\n".join(f'<a href="{href}">{text}</a>' for href, text in ld["links"])
    
    # Build language dropdown
    lang_dd = build_lang_dropdown(lang_code, tool_path)
    
    nav_html = f'''<nav id="nav-v2">
<div class="nv-inner">
<a class="nv-logo" href="{ld['prefix']}/"><span>◆</span> Carbide Tooling</a>
<div class="nv-links">
{nav_links}
</div>
<div class="nv-right">
<div class="nv-lang"><div class="lang-btn" onclick="toggleLangDD(event)"><span class="flag">{ld['flag']}</span><span>{ld['label']}</span><span class="caret">▼</span></div><div class="lang-dd" id="lang-dd">{lang_dd}</div></div>
<a class="nv-quote" href="{ld['quote_url']}">{ld['quote']}</a>
</div>
</div>
</nav>'''
    return nav_html


def detect_lang(filepath):
    """Detect language from file path."""
    rel = os.path.relpath(filepath, ROOT)
    for code in ["de", "jp", "es", "vi"]:
        if rel.startswith(code + "/") or rel.startswith(code + "\\"):
            return code
    return "en"


def detect_tool_path(filepath):
    """Get the tool path (e.g. /tools/speed-feed/) from the file path."""
    rel = os.path.relpath(filepath, ROOT)
    # Remove language prefix if present
    for code in ["de/", "jp/", "es/", "vi/"]:
        if rel.startswith(code):
            rel = rel[len(code):]
            break
    # The tool path is /tools/XXXX/
    return "/" + rel.replace("index.html", "").rstrip("/")


def fix_file(filepath):
    """Fix CSS corruption in a single HTML file."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    original = content
    lang = detect_lang(filepath)
    tool_path = detect_tool_path(filepath)
    
    # ---- FIX 1: Replace corrupted nav-v2-style block ----
    # Find <style id="nav-v2-style"> ... until matching </style>
    start_marker = '<style id="nav-v2-style">'
    start_idx = content.find(start_marker)
    if start_idx == -1:
        return False, "no nav-v2-style"
    
    # Find the end of nav-v2-style: search for </style> that comes BEFORE hero-atmo
    # Look for the first </style> after nav-v2-style start
    search_from = start_idx + len(start_marker)
    end_idx = content.find('</style>', search_from)
    if end_idx == -1:
        return False, "no close for nav-v2-style"
    end_idx += len('</style>')
    
    # ---- FIX 2: Replace corrupted hero-atmo-style block ----
    hero_atmo_start = '<style id="hero-atmo-style">'
    hero_atmo_idx = content.find(hero_atmo_start, end_idx)
    if hero_atmo_idx == -1:
        return False, "no hero-atmo-style"
    
    # Find where hero-atmo-style ends - it's the </style> that comes before <nav id="nav-v2">
    # But on corrupted pages, there might be raw <nav> inside. We need to find the REAL end.
    # Strategy: find the first </style> that appears AFTER hero-atmo-start AND is followed by something that looks like nav HTML or hero section
    
    search_atmo = hero_atmo_idx + len(hero_atmo_start)
    
    # Find all </style> occurrences after hero-atmo start
    rest_content = content[search_atmo:]
    
    # Strategy: find the </style> that is followed by either:
    # 1. <nav id="nav-v2"> directly
    # 2. \n\n<nav (with potential whitespace)
    # 3. <<a (broken DE nav)
    
    pattern = re.search(r'</style>\s*(<nav\s|<section\s|<!--\s*=====\s*HERO|<<a)', rest_content)
    if not pattern:
        # Fallback: just find the last </style> before <!-- HERO -->
        hero_marker = rest_content.find('<!-- ===== HERO ===== -->')
        if hero_marker == -1:
            hero_marker = rest_content.find('<section class="hero">')
        if hero_marker == -1:
            return False, "no hero marker"
        # Find the closest </style> before hero marker
        end_atmo = rest_content.rfind('</style>', 0, hero_marker)
        if end_atmo == -1:
            return False, "no close for hero-atmo"
        end_atmo += len('</style>')
        hero_atmo_end = search_atmo + end_atmo
    else:
        end_atmo = pattern.end()  # includes </style> and whitespace
        hero_atmo_end = search_atmo + end_atmo
    
    # Now check if there's a hero-img-style block. It might be corrupted.
    after_atmo = content[hero_atmo_end:]
    
    # Check for the corrupted pattern: <style id="hero-img-style"> inside content
    # or the pattern where .hero-img-wrapper appears after nav HTML
    # We need to clean everything between hero_atmo_end and <!-- ===== HERO ===== -->
    
    hero_section_marker = '<!-- ===== HERO ===== -->'
    hero_section_idx = after_atmo.find(hero_section_marker)
    if hero_section_idx == -1:
        hero_section_marker = '<section class="hero">'
        hero_section_idx = after_atmo.find(hero_section_marker)
    
    if hero_section_idx != -1:
        # The section between hero_atmo_end and hero_section is corrupted - strip it all
        after_clean = after_atmo[hero_section_idx:]
    else:
        # No hero section found, process normally
        after_clean = after_atmo
    
    # ---- Rebuild: clean CSS blocks + nav HTML + hero section ----
    rebuilt = NAV_V2_STYLE + "\n\n" + HERO_ATMO_STYLE + "\n\n" + HERO_IMG_STYLE + "\n\n"
    rebuilt += build_nav_html(lang, tool_path) + "\n"
    rebuilt += after_clean
    
    new_content = content[:start_idx] + rebuilt
    
    # ---- FIX: Clean up double <<a (German pages) ----
    new_content = new_content.replace('<<a class="nv-logo"', '<a class="nv-logo"')
    
    # Remove only EXTRA nav blocks that appear BEFORE the intended one (inside style/content)
    # Count nav-v2 occurrences. We want exactly 1.
    nav_matches = list(re.finditer(r'<nav id="nav-v2">', new_content))
    if len(nav_matches) > 1:
        # Keep only the LAST nav block (the one closest to hero section)
        for m in nav_matches[:-1]:
            # Find the </nav> that closes this block
            nav_start = m.start()
            nav_end = new_content.find('</nav>', m.end())
            if nav_end != -1:
                nav_end += len('</nav>')
                # Remove this extra nav block (replace with empty string)
                new_content = new_content[:nav_start] + new_content[nav_end:]
    
    # Check for any remaining corruption
    if '<style id="hero-atmo-style">' in new_content and new_content.count('<style id="nav-v2-style">') > 1:
        # Multiple nav-v2-style blocks - remove the extras
        first_nav = new_content.find('<style id="nav-v2-style">')
        second_nav = new_content.find('<style id="nav-v2-style">', first_nav + 1)
        if second_nav != -1:
            # Find the real nav that should stay (comes after img-style)
            img_style_end = new_content.find('</style>', new_content.find('id="hero-img-style"'))
            if img_style_end != -1:
                nav_start = new_content.find('<nav id="nav-v2">', img_style_end)
                if nav_start != -1:
                    # Keep content from start to end of img-style, then nav to end
                    # But wait, we already rebuilt this. Second nav-v2 might come from hero content.
                    # Just remove the first occurrence
                    pass
    
    # Write only if changed
    if new_content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True, "fixed"
    return False, "no change needed"


def main():
    """Fix all tool pages (all languages)."""
    total = 0
    fixed = 0
    errors = 0
    
    # Process ALL tool directories: tools/, de/tools/, jp/tools/, es/tools/, vi/tools/
    tool_dirs = ["tools"] + [f"{d}/tools" for d in ["de", "jp", "es", "vi"]]
    
    for td in tool_dirs:
        full_td = os.path.join(ROOT, td)
        if not os.path.isdir(full_td):
            continue
        
        for tool_name in sorted(os.listdir(full_td)):
            fp = os.path.join(full_td, tool_name, "index.html")
            if not os.path.isfile(fp):
                continue
            
            total += 1
            try:
                ok, msg = fix_file(fp)
                if ok:
                    fixed += 1
                else:
                    errors += 1
                    print(f"  SKIP [{td}/{tool_name}]: {msg}")
            except Exception as e:
                errors += 1
                print(f"  ERROR [{td}/{tool_name}]: {e}")
    
    print(f"\n{'='*60}")
    print(f"Total: {total} | Fixed: {fixed} | Errors/Skipped: {errors}")


if __name__ == "__main__":
    main()
