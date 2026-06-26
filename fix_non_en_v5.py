#!/usr/bin/env python3
"""
Fix non-English tool pages - V5: Precise targeted fixes only.
STRATEGY: Replace ONLY the old nav HTML and style blocks.
NEVER touch content between HERO marker and B2B card.
"""

import os, re

ROOT = "/Users/nicky/ZCodeProject/carbide-site"

# ============================================================
# CLEAN CSS REPLACEMENTS
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

# ============================================================
# LANGUAGE NAV DATA
# ============================================================

LANG_DATA = {
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

TOGGLE_LANG_JS = '''<script>
function toggleLangDD(e) {
  e.stopPropagation();
  var dd = document.getElementById('lang-dd');
  if (dd) { dd.classList.toggle('open'); }
}
document.addEventListener('click', function(e) {
  var dd = document.getElementById('lang-dd');
  var btn = document.querySelector('.lang-btn');
  if (dd && dd.classList.contains('open') && !btn.contains(e.target)) {
    dd.classList.remove('open');
  }
});
</script>
'''


def build_lang_dropdown(current_lang, tool_path):
    """Build the language dropdown HTML."""
    parts = []
    for code, flag, label, full in ALL_LANGS:
        if code == "en":
            href = tool_path
        else:
            href = "/" + code + tool_path
        
        css_class = "current" if code == current_lang else ""
        parts.append(f'<a href="{href}" class="{css_class}"><span class="flag">{flag}</span><span class="lbl">{label}</span><span class="nm">{full}</span></a>')
    
    return "".join(parts)


def build_nav_html(lang_code, tool_path):
    """Build the complete nav HTML block."""
    ld = LANG_DATA[lang_code]
    nav_links = "\n".join(f'<a href="{href}">{text}</a>' for href, text in ld["links"])
    lang_dd = build_lang_dropdown(lang_code, tool_path)
    
    return f'''<!-- ===== NAV ===== -->
<nav id="nav-v2">
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


def detect_lang(filepath):
    """Detect language from file path."""
    rel = os.path.relpath(filepath, ROOT)
    for code in ["de", "jp", "es", "vi"]:
        if rel.startswith(code + "/"):
            return code
    return "en"


def detect_tool_path(filepath):
    """Get the tool path (e.g. /tools/speed-feed/) from the file path."""
    rel = os.path.relpath(filepath, ROOT)
    for prefix in ["de/", "jp/", "es/", "vi/"]:
        if rel.startswith(prefix):
            rel = rel[len(prefix):]
            break
    return "/" + rel.replace("index.html", "").rstrip("/")


def fix_file(filepath):
    """Precise fix: replace only style blocks + nav HTML. Never touch content."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    original = content
    lang = detect_lang(filepath)
    tool_path = detect_tool_path(filepath)
    changes = []
    
    # ── STEP 1: Replace nav-v2-style block ──
    s_start = '<style id="nav-v2-style">'
    nav_style_start = content.find(s_start)
    if nav_style_start == -1:
        return False, "no nav-v2-style"
    
    # Find the end of nav-v2-style: <style id="nav-v2-style"> ... </style>
    # Use the </style> that is followed by <style id="hero-atmo-style">
    hero_atmo_pos = content.find('<style id="hero-atmo-style">', nav_style_start)
    if hero_atmo_pos == -1:
        return False, "no hero-atmo-style"
    
    # Find the last </style> before hero-atmo-style
    end_nav = content.rfind('</style>', nav_style_start, hero_atmo_pos)
    if end_nav == -1:
        return False, "no close tag for nav-v2-style"
    end_nav += len('</style>')
    
    # Replace nav-v2-style block
    content = content[:nav_style_start] + NAV_V2_STYLE + content[end_nav:]
    changes.append("nav-v2-style")
    
    # Recalculate positions after modification
    # ── STEP 2: Replace hero-atmo-style block ──
    atmo_start = content.find('<style id="hero-atmo-style">')
    if atmo_start == -1:
        return False, "lost hero-atmo-style after step 1"
    
    # Find the end: </style> that comes before hero-img-style or head close
    img_style_pos = content.find('<style id="hero-img-style">', atmo_start)
    if img_style_pos == -1:
        return False, "no hero-img-style"
    
    end_atmo = content.rfind('</style>', atmo_start, img_style_pos)
    if end_atmo == -1:
        return False, "no close tag for hero-atmo-style"
    end_atmo += len('</style>')
    
    # Replace hero-atmo-style block
    content = content[:atmo_start] + HERO_ATMO_STYLE + content[end_atmo:]
    changes.append("hero-atmo-style")
    
    # ── STEP 3: Replace nav HTML block ──
    # The nav block is from <!-- ===== NAV ===== --> to <!-- ===== HERO ===== -->
    # OR from <nav id="nav-v2"> to <!-- ===== HERO ===== -->
    nav_marker = '<!-- ===== NAV ===== -->'
    hero_marker = '<!-- ===== HERO ===== -->'
    
    nav_pos = content.find(nav_marker)
    if nav_pos == -1:
        # Try finding <nav id="nav-v2"> directly
        nav_pos = content.find('<nav id="nav-v2">')
    
    hero_pos = content.find(hero_marker)
    
    if nav_pos != -1 and hero_pos != -1 and nav_pos < hero_pos:
        # Find the actual </nav> closest to hero marker
        between = content[nav_pos:hero_pos]
        # Find the end of the nav block
        closing_nav = between.rfind('</nav>')
        if closing_nav != -1:
            nav_end = nav_pos + closing_nav + len('</nav>')
            # Replace old nav with new nav
            new_nav = build_nav_html(lang, tool_path)
            content = content[:nav_pos] + new_nav + content[hero_pos:]
            changes.append("nav-html")
    else:
        return False, "no nav/hero markers"
    
    # ── STEP 4: Inject toggleLangDD JS before </body> if not present ──
    if 'function toggleLangDD' not in content:
        body_close = content.rfind('</body>')
        if body_close != -1:
            content = content[:body_close] + TOGGLE_LANG_JS + "\n" + content[body_close:]
            changes.append("lang-js")
    
    # ── STEP 5: Clean up duplicated engineering-directory CSS ──
    # Some V3 pages have the CSS twice
    eng_css = content.count('.engineering-directory a{')
    if eng_css > 1:
        # Remove duplicate occurrences - keep only the last one
        first_eng = content.find('.engineering-directory a{')
        # Find each occurrence and remove extras
        import re as re_mod
        pattern = re_mod.compile(r'<style>\s*\.engineering-directory a\{.*?</style>', re_mod.DOTALL)
        matches = list(pattern.finditer(content))
        if len(matches) > 1:
            # Keep the last one, remove earlier ones
            for m in matches[:-1]:
                content = content[:m.start()] + content[m.end():]
                changes.append("dedup-eng-css")
    
    # Write only if changed
    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True, " + ".join(changes)
    return False, "no change needed"


def verify_file(filepath):
    """Quick verification that the page still has hero section and calculator."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    issues = []
    if '<!-- ===== HERO ===== -->' not in content:
        issues.append("MISSING HERO MARKER")
    if '<!-- ===== CALCULATOR ===== -->' not in content:
        issues.append("MISSING CALC MARKER")
    if 'id="calculator"' not in content:
        issues.append("MISSING calculator id")
    if 'b2b-card' not in content:
        issues.append("MISSING b2b-card")
    
    return issues


def main():
    """Fix all non-English tool pages."""
    total = 0
    fixed = 0
    errors = 0
    verify_failures = []
    
    tool_dirs = [f"{d}/tools" for d in ["de", "jp", "es", "vi"]]
    
    for td in tool_dirs:
        full_td = os.path.join(ROOT, td)
        if not os.path.isdir(full_td):
            print(f"  SKIP dir: {td} (not found)")
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
                    # Verify
                    issues = verify_file(fp)
                    if issues:
                        print(f"  ⚠️  [{td}/{tool_name}]: {', '.join(issues)}")
                        verify_failures.append(fp)
                else:
                    errors += 1
                    print(f"  ❌ [{td}/{tool_name}]: {msg}")
            except Exception as e:
                errors += 1
                print(f"  💥 [{td}/{tool_name}]: {e}")
    
    print(f"\n{'='*60}")
    print(f"Total: {total} | Fixed: {fixed} | Errors: {errors}")
    if verify_failures:
        print(f"\n⚠️  Verification failures ({len(verify_failures)}):")
        for vf in verify_failures:
            print(f"  - {os.path.relpath(vf, ROOT)}")


if __name__ == "__main__":
    main()
