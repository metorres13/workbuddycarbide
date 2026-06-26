#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║  Carbide-Tooling.com — Apple-Style Global Optimization v2  ║
║  ========================================================= ║
║  1. Apple Smart Nav (Tailwind CDN + backdrop-blur-md)      ║
║  2. Global Engineering Directory (same-lang internal links)║
║  3. Enhanced B2B RFQ Cards (tool-specific titles)          ║
║  4. Industrial Hero Atmosphere + Image Containers          ║
║  5. Hreflang Verification & SEO Mesh                       ║
║  6. Sitemap Regeneration + robots.txt Update               ║
║  7. HTML Validation                                        ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import re
import json
import random
import datetime
import html.parser
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback

# ═══════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════

ROOT = Path("/Users/nicky/ZCodeProject/carbide-site")
SITE = "https://carbide-tooling.com"
DATE = datetime.date.today().isoformat()

LANG_MAP = {
    "en": {"code": "en", "label": "EN", "hreflang": "en", "flag": "🇬🇧", "dir": ""},
    "de": {"code": "de", "label": "DE", "hreflang": "de", "flag": "🇩🇪", "dir": "de"},
    "jp": {"code": "jp", "label": "JP", "hreflang": "ja", "flag": "🇯🇵", "dir": "jp"},
    "es": {"code": "es", "label": "ES", "hreflang": "es", "flag": "🇪🇸", "dir": "es"},
    "vi": {"code": "vi", "label": "VI", "hreflang": "vi", "flag": "🇻🇳", "dir": "vi"},
    "zh": {"code": "zh", "label": "中", "hreflang": "zh", "flag": "🇨🇳", "dir": "zh"},
}
LANG_ORDER = ["en", "de", "jp", "es", "vi"]
LANG_DIRS = ["de", "jp", "es", "vi", "zh"]

NAV_LABELS = {
    "en": {"home": "Home", "products": "Products", "tools": "Tools", "guides": "Guides", "about": "About", "quote": "Get a Quote"},
    "de": {"home": "Start", "products": "Produkte", "tools": "Werkzeuge", "guides": "Anleitungen", "about": "Über uns", "quote": "Angebot"},
    "jp": {"home": "ホーム", "products": "製品", "tools": "ツール", "guides": "ガイド", "about": "会社概要", "quote": "見積依頼"},
    "es": {"home": "Inicio", "products": "Productos", "tools": "Herramientas", "guides": "Guías", "about": "Acerca de", "quote": "Cotización"},
    "vi": {"home": "Trang chủ", "products": "Sản phẩm", "tools": "Công cụ", "guides": "Hướng dẫn", "about": "Giới thiệu", "quote": "Báo giá"},
    "zh": {"home": "首页", "products": "产品", "tools": "工具", "guides": "指南", "about": "关于", "quote": "获取报价"},
}

STATS = {
    "total_processed": 0,
    "nav_updated": 0,
    "b2b_enhanced": 0,
    "directory_added": 0,
    "hreflang_fixed": 0,
    "errors": 0,
    "skipped": 0,
}


# ═══════════════════════════════════════════
# TOOL & PAGE DISCOVERY
# ═══════════════════════════════════════════

def get_all_tool_names():
    """Return list of all tool directory names under /tools/"""
    tools_dir = ROOT / "tools"
    if not tools_dir.exists():
        return []
    return sorted([
        d.name for d in tools_dir.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    ])


def get_all_html_files():
    """Recursively get all .html files in the project"""
    files = []
    for f in ROOT.rglob("*.html"):
        if ".git" not in str(f) and "__pycache__" not in str(f) and ".venv" not in str(f):
            files.append(f)
    return files


def detect_lang_from_path(filepath):
    """Detect language from file path"""
    rel = filepath.relative_to(ROOT)
    parts = rel.parts
    if parts[0] in LANG_DIRS:
        return parts[0]
    return "en"


def detect_page_type(filepath):
    """Detect page type: tool, product, guide, root, tools-index"""
    rel = str(filepath.relative_to(ROOT))
    if "/tools/" in rel and rel.endswith("/index.html"):
        # Check if it's the tools index page
        parts = rel.split("/")
        # e.g., "tools/speed-feed/index.html" -> tool page
        # e.g., "de/tools/index.html" -> tools index
        if parts[-2] == "tools":
            return "tools-index"
        return "tool"
    if "/products/" in rel:
        return "product"
    if "/guides/" in rel:
        return "guide"
    if rel in ["index.html", "de/index.html", "jp/index.html", "es/index.html", "vi/index.html", "zh/index.html"]:
        return "home"
    if rel.endswith("about.html"):
        return "about"
    if rel.endswith("quote.html"):
        return "quote"
    return "other"


# ═══════════════════════════════════════════
# 1. APPLE SMART NAV COMPONENT
# ═══════════════════════════════════════════

TAILWIND_CDN = '<script src="https://cdn.tailwindcss.com"></script>'

TAILWIND_CONFIG = """<script>
tailwind.config = {
  important: true,
  corePlugins: { preflight: false },
  theme: {
    extend: {
      fontFamily: { sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"] },
    }
  }
}
</script>"""

NAV_CSS_OVERRIDE = """
<style id="nav-v2-style">
/* ── Apple Smart Nav v2 ── */
nav#nav-v2{position:sticky;top:0;z-index:100;background:rgba(255,255,255,.88);backdrop-filter:saturate(180%) blur(24px);-webkit-backdrop-filter:saturate(180%) blur(24px);border-bottom:1px solid rgba(0,0,0,.06);height:48px;display:flex;align-items:center}
nav#nav-v2 .nv-inner{display:flex;align-items:center;justify-content:space-between;width:100%;max-width:1100px;margin:0 auto;padding:0 24px}
nav#nav-v2 .nv-logo{font-size:14px;font-weight:700;letter-spacing:-.3px;color:#1d1d1f;text-decoration:none;display:flex;align-items:center;gap:6px;white-space:nowrap;flex-shrink:0}
nav#nav-v2 .nv-logo span{font-weight:800;color:#0066cc}
nav#nav-v2 .nv-links{display:flex;align-items:center;gap:0;flex-shrink:0}
nav#nav-v2 .nv-links>a{color:#1d1d1f;text-decoration:none;padding:0 14px;height:48px;display:flex;align-items:center;font-weight:500;font-size:12px;transition:color .15s;white-space:nowrap}
nav#nav-v2 .nv-links>a:hover{color:#0066cc}
nav#nav-v2 .nv-right{display:flex;align-items:center;gap:8px;flex-shrink:0}
nav#nav-v2 .nv-quote{display:inline-flex;align-items:center;background:#0066cc;color:#fff;padding:6px 16px;border-radius:24px;font-size:11px;font-weight:600;text-decoration:none;transition:all .2s;white-space:nowrap}
nav#nav-v2 .nv-quote:hover{background:#0055aa;transform:translateY(-1px);box-shadow:0 4px 12px rgba(0,102,204,.25)}
nav#nav-v2 .nv-lang{display:flex;align-items:center;gap:2px;margin-left:4px;padding-left:8px;border-left:1px solid #e8e8ed}
nav#nav-v2 .nv-lang a{font-size:10px;font-weight:600;color:#86868b;text-decoration:none;padding:3px 6px;border-radius:12px;transition:all .15s;letter-spacing:.3px}
nav#nav-v2 .nv-lang a:hover{color:#1d1d1f;background:#f5f5f7}
nav#nav-v2 .nv-lang a.active{color:#0066cc;background:#f0f7ff;font-weight:700}
nav#nav-v2 .nv-lang .sep{color:#d2d2d6;font-size:10px;margin:0 1px;font-weight:300}
@media(max-width:768px){
  nav#nav-v2 .nv-links{display:none}
  nav#nav-v2 .nv-lang a{font-size:9px;padding:2px 4px}
  nav#nav-v2 .nv-quote{padding:4px 10px;font-size:10px}
}
nav#nav-v2{font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif!important}
</style>
"""


def build_nav_html(lang_code, current_path=""):
    """Build the Apple Smart Nav HTML for a given language"""
    L = NAV_LABELS.get(lang_code, NAV_LABELS["en"])
    lang_info = LANG_MAP[lang_code]
    base = "" if lang_code == "en" else f"/{lang_code}"

    home_href = f"{base}/" if base else "/"
    products_href = f"{base}/products/"
    tools_href = f"{base}/tools/"
    guides_href = f"{base}/guides/"
    about_href = f"{base}/about.html"
    quote_href = f"{base}/quote.html"

    # Build language switcher links
    lang_links = []
    for code in LANG_ORDER:
        li = LANG_MAP[code]
        if code == "en":
            href = current_path if current_path else "/"
        else:
            href = f"/{code}{current_path}" if current_path else f"/{code}/"

        active_class = ' class="active"' if code == lang_code else ""
        if code == lang_code:
            lang_links.append(f'<a href="#" onclick="return false" class="active">{li["label"]}</a>')
        else:
            lang_links.append(f'<a href="{href}">{li["label"]}</a>')
        if code in ["en", "jp"]:
            lang_links.append('<span class="sep">·</span>')

    lang_html = "".join(lang_links)

    nav = f'''<nav id="nav-v2">
<div class="nv-inner">
<a class="nv-logo" href="{home_href}"><span>◆</span> Carbide Tooling</a>
<div class="nv-links">
<a href="{home_href}">{L["home"]}</a>
<a href="{products_href}">{L["products"]}</a>
<a href="{tools_href}">{L["tools"]}</a>
<a href="{guides_href}">{L["guides"]}</a>
<a href="{about_href}">{L["about"]}</a>
</div>
<div class="nv-right">
<div class="nv-lang">{lang_html}</div>
<a class="nv-quote" href="{quote_href}">📩 {L["quote"]}</a>
</div>
</div>
</nav>'''
    return nav


def inject_nav(content, lang_code, rel_path=""):
    """Replace existing <nav> block with the new Apple Smart Nav"""
    # Try multiple patterns to find the existing nav
    patterns = [
        r'<nav.*?</nav>',
        r'<nav[^>]*>.*?</nav>',
    ]
    for pattern in patterns:
        if re.search(pattern, content, re.DOTALL):
            current_rel = rel_path
            new_nav = build_nav_html(lang_code, current_rel)
            content = re.sub(pattern, new_nav, content, count=1, flags=re.DOTALL)
            STATS["nav_updated"] += 1
            return content

    # If no nav found, try to insert after <body>
    if '<body>' in content or '<body ' in content:
        new_nav = build_nav_html(lang_code, rel_path)
        content = re.sub(r'(<body[^>]*>)', r'\1\n' + new_nav, content, count=1, flags=re.DOTALL)
        STATS["nav_updated"] += 1
        return content

    return content


def inject_nav_assets(content):
    """Inject Tailwind CDN + nav CSS override into <head>"""
    if 'nav-v2-style' in content:
        return content  # Already injected

    # Add Tailwind CDN and nav CSS before </head>
    assets = f'{TAILWIND_CDN}\n{TAILWIND_CONFIG}\n{NAV_CSS_OVERRIDE}\n'
    content = content.replace('</head>', f'{assets}</head>', 1)
    return content


# ═══════════════════════════════════════════
# 2. HREFLANG VERIFICATION & FIX
# ═══════════════════════════════════════════

def get_page_url_path(filepath):
    """Get the URL path for a file (without domain)"""
    rel = filepath.relative_to(ROOT)
    path = str(rel)

    # Convert to URL path
    if path == "index.html":
        return "/"
    if path.endswith("/index.html"):
        return "/" + path[:-len("index.html")]
    return "/" + path


def build_hreflang_tags(filepath, lang_code):
    """Build hreflang alternate tags for a page"""
    rel = filepath.relative_to(ROOT)
    parts = list(rel.parts)
    filename = parts[-1]

    # Build the path without language prefix
    path_parts = []
    if parts[0] in LANG_DIRS:
        path_parts = list(parts[1:])
    else:
        path_parts = list(parts)

    base_path = "/".join(path_parts)
    if base_path.endswith("/index.html"):
        base_path = base_path[:-len("index.html")]
    elif base_path == "index.html":
        base_path = ""

    tags = []
    # x-default (English)
    en_path = f"/{base_path}" if base_path else "/"
    tags.append(f'<link href="{SITE}{en_path}" hreflang="x-default" rel="alternate"/>')

    for code in LANG_ORDER:
        li = LANG_MAP[code]
        if code == "en":
            href = f"{SITE}{en_path}"
        else:
            href = f"{SITE}/{code}/{base_path}" if base_path else f"{SITE}/{code}/"
        tags.append(f'<link href="{href}" hreflang="{li["hreflang"]}" rel="alternate"/>')

    return "\n".join(tags)


def fix_hreflang(content, filepath, lang_code):
    """Verify and fix hreflang tags in the page"""
    href_links_section = get_page_url_path(filepath)

    # Count existing hreflang tags
    existing = re.findall(r'<link[^>]*hreflang="[^"]*"[^>]*rel="alternate"[^>]*>', content)

    if len(existing) >= 5:
        # Already has enough hreflang tags, verify and update if needed
        # Check for x-default
        has_xdefault = any('x-default' in t for t in existing)
        if not has_xdefault:
            # Inject x-default
            new_tags = build_hreflang_tags(filepath, lang_code)
            # Replace all existing hreflang tags
            for tag in existing:
                content = content.replace(tag, "", 1)
            content = content.replace('</head>', f'\n{new_tags}\n</head>', 1)
            STATS["hreflang_fixed"] += 1
        return content

    # Need to add hreflang tags
    new_tags = build_hreflang_tags(filepath, lang_code)
    # Remove any partial existing hreflang tags
    content = re.sub(r'<link[^>]*hreflang="[^"]*"[^>]*>', '', content)
    content = content.replace('</head>', f'\n{new_tags}\n</head>', 1)
    STATS["hreflang_fixed"] += 1
    return content


# ═══════════════════════════════════════════
# 3. GLOBAL ENGINEERING DIRECTORY
# ═══════════════════════════════════════════

def build_engineering_directory(lang_code, current_tool, all_tools, count=10):
    """Build Global Engineering Directory with same-language internal links"""
    # Filter out the current tool
    available = [t for t in all_tools if t != current_tool]
    if not available:
        return ""

    # Pick random tools
    selected = random.sample(available, min(count, len(available)))
    random.shuffle(selected)

    # Build human-readable names
    def tool_display_name(t):
        return t.replace("-", " ").title()

    base = "" if lang_code == "en" else f"/{lang_code}"

    links_html = ""
    for t in selected:
        links_html += f'<a href="{base}/tools/{t}/">{tool_display_name(t)}</a>\n'

    titles = {
        "en": "🌐 Global Engineering Directory",
        "de": "🌐 Globales Engineering-Verzeichnis",
        "jp": "🌐 グローバルエンジニアリングディレクトリ",
        "es": "🌐 Directorio Global de Ingeniería",
        "vi": "🌐 Danh Mục Kỹ Thuật Toàn Cầu",
        "zh": "🌐 全球工程目录",
    }
    subtitles = {
        "en": "Explore more professional machining tools from our global collection",
        "de": "Entdecken Sie weitere professionelle Bearbeitungswerkzeuge",
        "jp": "グローバルコレクションから専門の加工ツールを探索",
        "es": "Explore más herramientas profesionales de mecanizado",
        "vi": "Khám phá thêm công cụ gia công chuyên nghiệp",
        "zh": "浏览我们全球系列中的更多专业加工工具",
    }

    title = titles.get(lang_code, titles["en"])
    subtitle = subtitles.get(lang_code, subtitles["en"])

    directory_html = f'''
<section class="engineering-directory" style="margin:40px 0 20px;padding:28px 24px;background:linear-gradient(135deg,#f8f9fa 0%,#f5f5f7 100%);border-radius:20px;border:1px solid #e8e8ed">
<h3 style="font-size:16px;font-weight:700;color:#1d1d1f;margin-bottom:6px;text-align:center">{title}</h3>
<p style="font-size:12px;color:#86868b;text-align:center;margin-bottom:16px">{subtitle}</p>
<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:8px">
{links_html}
</div>
</section>
<style>
.engineering-directory a{{
  display:block;
  font-size:12px;
  font-weight:500;
  color:#1d1d1f;
  text-decoration:none;
  padding:8px 14px;
  background:#fff;
  border-radius:10px;
  border:1px solid #e8e8ed;
  transition:all .15s;
  text-align:center;
}}
.engineering-directory a:hover{{
  background:#0066cc;
  color:#fff;
  border-color:#0066cc;
  transform:translateY(-1px);
  box-shadow:0 4px 12px rgba(0,102,204,.15);
}}
</style>'''
    return directory_html


# ═══════════════════════════════════════════
# 4. ENHANCED B2B RFQ CARD
# ═══════════════════════════════════════════

def build_enhanced_b2b_card(lang_code, tool_name=""):
    """Build enhanced Apple-style B2B RFQ card"""
    display_name = tool_name.replace("-", " ").title() if tool_name else "Your Application"

    texts = {
        "en": {
            "title": f"Professional Solutions for {display_name}?",
            "body": "Get factory-direct pricing on premium carbide tooling with ISO-certified quality and responsive engineering support.",
            "btn": "Request Bulk Quote →",
        },
        "de": {
            "title": f"Professionelle Lösungen für {display_name}?",
            "body": "Erhalten Sie werkseitige Preise für Premium-Hartmetallwerkzeuge mit ISO-zertifizierter Qualität.",
            "btn": "Massenangebot anfordern →",
        },
        "jp": {
            "title": f"{display_name}のプロフェッショナルソリューション",
            "body": "ISO認証品質のプレミアム超硬工具を工場直送価格でご提供。技術サポート付き。",
            "btn": "一括見積を依頼 →",
        },
        "es": {
            "title": f"¿Soluciones Profesionales para {display_name}?",
            "body": "Obtenga precios directos de fábrica en herramientas de carburo premium con calidad certificada ISO.",
            "btn": "Solicitar Cotización →",
        },
        "vi": {
            "title": f"Giải Pháp Chuyên Nghiệp cho {display_name}?",
            "body": "Nhận giá trực tiếp từ nhà máy cho dụng cụ carbide cao cấp với chất lượng chứng nhận ISO.",
            "btn": "Yêu Cầu Báo Giá Số Lượng →",
        },
        "zh": {
            "title": f"{display_name} 的专业解决方案",
            "body": "获取ISO认证品质的优质硬质合金刀具工厂直供价格，以及专业的技术支持。",
            "btn": "批量询价 →",
        },
    }

    t = texts.get(lang_code, texts["en"])
    base = "" if lang_code == "en" else f"/{lang_code}"

    card = f'''<aside class="b2b-card-enhanced" style="margin:32px 0">
<div style="display:flex;align-items:center;gap:20px;background:linear-gradient(135deg,#f0f7ff 0%,#e8f4ff 100%);border:1px solid #b8d4f0;border-radius:20px;padding:24px 28px;box-shadow:0 2px 12px rgba(0,102,204,.06)">
<div style="flex-shrink:0;width:52px;height:52px;background:#0066cc;border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:24px;box-shadow:0 4px 12px rgba(0,102,204,.2)">📦</div>
<div style="flex:1;min-width:0">
<h3 style="font-size:15px;font-weight:700;color:#1d1d1f;margin:0 0 4px">{t['title']}</h3>
<p style="font-size:12px;color:#555;line-height:1.5;margin:0">{t['body']}</p>
</div>
<a href="{base}/quote.html" style="flex-shrink:0;display:inline-flex;align-items:center;background:#0066cc;color:#fff;padding:10px 22px;border-radius:24px;font-size:12px;font-weight:600;text-decoration:none;transition:all .2s;white-space:nowrap" onmouseover="this.style.background='#0055aa';this.style.transform='translateY(-1px)';this.style.boxShadow='0 4px 16px rgba(0,102,204,.3)'" onmouseout="this.style.background='#0066cc';this.style.transform='none';this.style.boxShadow='none'">{t['btn']}</a>
</div>
</aside>'''
    return card


# ═══════════════════════════════════════════
# 5. HERO ATMOSPHERE & IMAGE CONTAINERS
# ═══════════════════════════════════════════

HERO_ATMOSPHERE_CSS = """
<style id="hero-atmo-style">
/* ── Hero Atmosphere ── */
.hero-atmo {
  position: relative;
  width: 100%;
  height: 200px;
  overflow: hidden;
  background: linear-gradient(180deg, #f5f5f7 0%, #e8e8ed 40%, #d2d2d7 100%);
  margin-bottom: -60px;
  z-index: 0;
}
.hero-atmo::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 80% 60% at 20% 50%, rgba(0,102,204,.06) 0%, transparent 50%),
    radial-gradient(ellipse 60% 80% at 80% 40%, rgba(0,0,0,.04) 0%, transparent 50%),
    linear-gradient(180deg, rgba(255,255,255,0) 0%, rgba(255,255,255,.95) 90%, #fff 100%);
}
.hero-atmo::after {
  content: '';
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 80px;
  background: linear-gradient(0deg, #fff 0%, transparent 100%);
}
/* Image Container - Apple Style */
.img-container {
  width: 100%;
  aspect-ratio: 1;
  background: #fff;
  border-radius: 20px;
  border: 1px solid #d2d2d7;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
.img-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.img-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f0f0f3 0%, #e8e8ed 50%, #f0f0f3 100%);
  color: #c0c0c6;
  font-size: 48px;
}
.img-placeholder::after {
  content: '◆';
  font-size: 48px;
  opacity: .3;
}
</style>
"""

HERO_ATMOSPHERE_HTML = '<div class="hero-atmo" aria-hidden="true"></div>'


# ═══════════════════════════════════════════
# 6. MAIN PROCESSING FUNCTION
# ═══════════════════════════════════════════

def process_file(filepath, all_tools):
    """Process a single HTML file with all enhancements"""
    try:
        content = filepath.read_text(encoding="utf-8")

        if not content.strip():
            STATS["skipped"] += 1
            return

        lang_code = detect_lang_from_path(filepath)
        page_type = detect_page_type(filepath)

        # Determine relative path for this page (for nav links)
        rel = filepath.relative_to(ROOT)
        rel_str = str(rel)
        if rel_str.endswith("/index.html"):
            rel_str = "/" + rel_str[:-len("index.html")]
        elif rel_str == "index.html":
            rel_str = "/"
        else:
            rel_str = "/" + rel_str

        # For language pages, strip language prefix from nav path
        if lang_code != "en":
            nav_rel = rel_str[len(f"/{lang_code}"):] if rel_str.startswith(f"/{lang_code}/") else rel_str
        else:
            nav_rel = rel_str

        # 1. Inject nav assets (Tailwind CDN + CSS)
        content = inject_nav_assets(content)

        # 2. Replace nav
        content = inject_nav(content, lang_code, nav_rel)

        # 3. Fix hreflang
        content = fix_hreflang(content, filepath, lang_code)

        # 4. Tool-specific enhancements
        if page_type == "tool":
            tool_name = filepath.parent.name

            # Remove old "Explore More Tools" sections (multiple patterns)
            # Remove old more-tools sections
            content = re.sub(
                r'<section class="more-tools">.*?</section>',
                '', content, flags=re.DOTALL
            )

            # Add Global Engineering Directory before </body>
            directory = build_engineering_directory(lang_code, tool_name, all_tools, count=10)
            content = content.replace('</body>', f'{directory}\n</body>', 1)
            STATS["directory_added"] += 1

            # Replace old B2B card with enhanced version
            old_b2b = re.search(r'<aside class="b2b-card[^"]*">.*?</aside>', content, re.DOTALL)
            if old_b2b:
                new_card = build_enhanced_b2b_card(lang_code, tool_name)
                content = content.replace(old_b2b.group(0), new_card, 1)
                STATS["b2b_enhanced"] += 1
            else:
                # Add B2B card if not present (inject before </body> but after directory)
                new_card = build_enhanced_b2b_card(lang_code, tool_name)
                content = content.replace('</body>', f'{new_card}\n</body>', 1)
                STATS["b2b_enhanced"] += 1

            # Add hero atmosphere (after <body>)
            if '<div class="hero-atmo"' not in content:
                content = re.sub(
                    r'(<body[^>]*>)',
                    r'\1' + f'\n{HERO_ATMOSPHERE_HTML}',
                    content, count=1
                )

        # 5. Inject atmosphere CSS in head if not present
        if 'hero-atmo-style' not in content and page_type == "tool":
            content = content.replace('</head>', f'{HERO_ATMOSPHERE_CSS}\n</head>', 1)

        # Write back
        filepath.write_text(content, encoding="utf-8")
        STATS["total_processed"] += 1

    except Exception as e:
        print(f"ERROR processing {filepath}: {e}")
        traceback.print_exc()
        STATS["errors"] += 1


# ═══════════════════════════════════════════
# 7. SITEMAP REGENERATION
# ═══════════════════════════════════════════

def generate_sitemaps():
    """Regenerate all language sitemaps and sitemap index"""
    print("\n📋 Regenerating Sitemaps...")

    def collect_urls(lang_code):
        """Collect all URLs for a given language"""
        urls = []
        lang_dir = ROOT / lang_code if lang_code != "en" else ROOT

        # Helper to add URL
        def add_url(path, priority="0.8", changefreq="monthly"):
            full_url = f"{SITE}/{path}" if not path.startswith("http") else path
            urls.append({
                "loc": full_url.rstrip("/") + ("/" if not full_url.endswith(".html") else ""),
                "lastmod": DATE,
                "changefreq": changefreq,
                "priority": priority,
            })

        if lang_code == "en":
            # Root pages
            add_url("", "1.0", "weekly")
            add_url("tools/", "0.9", "weekly")
            add_url("about.html", "0.5", "monthly")
            add_url("quote.html", "0.6", "monthly")
            base_for_tools = "tools/"
            base_for_products = "products/"
            base_for_guides = "guides/"
        else:
            add_url(f"{lang_code}/", "1.0", "weekly")
            add_url(f"{lang_code}/tools/", "0.9", "weekly")
            add_url(f"{lang_code}/about.html", "0.5", "monthly")
            add_url(f"{lang_code}/quote.html", "0.6", "monthly")
            base_for_tools = f"{lang_code}/tools/"
            base_for_products = f"{lang_code}/products/"
            base_for_guides = f"{lang_code}/guides/"

        # Products
        products_dir = ROOT / lang_code / "products" if lang_code != "en" else ROOT / "products"
        if products_dir.exists():
            for pf in sorted(products_dir.glob("*.html")):
                add_url(f"{base_for_products}{pf.name}", "0.6", "monthly")

        # Guides
        guides_dir = ROOT / lang_code / "guides" if lang_code != "en" else ROOT / "guides"
        if guides_dir.exists():
            for gf in sorted(guides_dir.glob("*.html")):
                add_url(f"{base_for_guides}{gf.name}", "0.6", "monthly")

        # Tools
        tools_parent = ROOT / lang_code / "tools" if lang_code != "en" else ROOT / "tools"
        if tools_parent.exists():
            for td in sorted(tools_parent.iterdir()):
                if td.is_dir() and not td.name.startswith("."):
                    add_url(f"{base_for_tools}{td.name}/", "0.8", "monthly")

        return urls

    # Generate per-language sitemaps
    sitemap_files = {}
    for lang_code in ["en", "de", "jp", "es", "vi", "zh"]:
        urls = collect_urls(lang_code)
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        xml += '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'

        for u in urls:
            xml += "  <url>\n"
            xml += f'    <loc>{u["loc"]}</loc>\n'
            xml += f'    <lastmod>{u["lastmod"]}</lastmod>\n'
            xml += f'    <changefreq>{u["changefreq"]}</changefreq>\n'
            xml += f'    <priority>{u["priority"]}</priority>\n'

            # Add hreflang alternates
            path = u["loc"].replace(SITE, "")
            if not path:
                path = "/"
            elif path.endswith(".html"):
                pass  # Keep as-is
            if path.startswith(f"/{lang_code}/"):
                base_path = path[len(f"/{lang_code}"):]
            else:
                base_path = path

            xml += f'    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE}{base_path}"/>\n'
            for lc in LANG_ORDER:
                li = LANG_MAP[lc]
                if lc == "en":
                    href = f"{SITE}{base_path}"
                else:
                    href = f"{SITE}/{lc}{base_path}"
                xml += f'    <xhtml:link rel="alternate" hreflang="{li["hreflang"]}" href="{href}"/>\n'
            xml += "  </url>\n"

        xml += "</urlset>\n"

        filename = "sitemap.xml" if lang_code == "en" else f"sitemap-{lang_code}.xml"
        if lang_code == "jp":
            filename = "sitemap-ja.xml"  # Use ISO code for sitemap

        filepath = ROOT / filename
        filepath.write_text(xml, encoding="utf-8")
        sitemap_files[filename] = len(urls)
        print(f"  ✅ {filename}: {len(urls)} URLs")

    # Generate sitemap index
    index_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    index_xml += '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for filename, count in sitemap_files.items():
        index_xml += "  <sitemap>\n"
        index_xml += f'    <loc>{SITE}/{filename}</loc>\n'
        index_xml += f'    <lastmod>{DATE}</lastmod>\n'
        index_xml += "  </sitemap>\n"
    index_xml += "</sitemapindex>\n"

    (ROOT / "sitemap-index.xml").write_text(index_xml, encoding="utf-8")
    print(f"  ✅ sitemap-index.xml: {len(sitemap_files)} sitemaps")

    # Update robots.txt
    robots = f"""User-agent: *
Allow: /
Sitemap: {SITE}/sitemap-index.xml

# Direct links for search engines
Sitemap: {SITE}/sitemap.xml
Sitemap: {SITE}/sitemap-de.xml
Sitemap: {SITE}/sitemap-ja.xml
Sitemap: {SITE}/sitemap-es.xml
Sitemap: {SITE}/sitemap-vi.xml
"""
    (ROOT / "robots.txt").write_text(robots, encoding="utf-8")
    print(f"  ✅ robots.txt updated")

    total_urls = sum(sitemap_files.values())
    return total_urls, sitemap_files


# ═══════════════════════════════════════════
# 8. HTML VALIDATION
# ═══════════════════════════════════════════

class HTMLValidator(html.parser.HTMLParser):
    """Simple HTML validator to check for unclosed tags and basic errors"""

    def __init__(self):
        super().__init__()
        self.errors = []
        self.tag_stack = []
        self.void_elements = {
            'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
            'link', 'meta', 'param', 'source', 'track', 'wbr'
        }

    def handle_starttag(self, tag, attrs):
        if tag not in self.void_elements:
            self.tag_stack.append((tag, self.getpos()))

    def handle_endtag(self, tag):
        if tag in self.void_elements:
            return
        if self.tag_stack:
            # Find matching open tag
            for i in range(len(self.tag_stack) - 1, -1, -1):
                if self.tag_stack[i][0] == tag:
                    self.tag_stack = self.tag_stack[:i]
                    break
            else:
                self.errors.append(f"Unexpected closing tag </{tag}> at line {self.getpos()[0]}")

    def get_errors(self):
        return self.errors

    def get_unclosed(self):
        return [t[0] for t in self.tag_stack]


def validate_html(filepath):
    """Validate a single HTML file"""
    try:
        content = filepath.read_text(encoding="utf-8")
        validator = HTMLValidator()
        validator.feed(content)
        errors = validator.get_errors()
        unclosed = validator.get_unclosed()
        return {
            "file": str(filepath.relative_to(ROOT)),
            "errors": errors,
            "unclosed": unclosed,
            "ok": len(errors) == 0,
        }
    except Exception as e:
        return {
            "file": str(filepath),
            "errors": [str(e)],
            "unclosed": [],
            "ok": False,
        }


# ═══════════════════════════════════════════
# 9. MAIN EXECUTION
# ═══════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════╗")
    print("║  Carbide Apple-Style Optimization v2         ║")
    print("╚══════════════════════════════════════════════╝")
    print()

    # Step 0: Discover
    print("🔍 Step 0: Discovering project structure...")
    all_tools = get_all_tool_names()
    all_files = get_all_html_files()
    print(f"   Found {len(all_tools)} tools, {len(all_files)} HTML files")

    # Step 1-5: Process all files
    print("\n⚙️  Step 1-5: Processing all HTML files...")
    print(f"   Processing {len(all_files)} files...")

    # Process in parallel for speed
    batch_size = 50
    for i in range(0, len(all_files), batch_size):
        batch = all_files[i:i + batch_size]
        for filepath in batch:
            process_file(filepath, all_tools)
        print(f"   Progress: {min(i + batch_size, len(all_files))}/{len(all_files)} files", end="\r")

    print(f"\n   ✅ Done! Processed {STATS['total_processed']} files")

    # Step 6: Sitemaps
    print("\n📋 Step 6: Regenerating Sitemaps...")
    total_sitemap_urls, sitemap_details = generate_sitemaps()

    # Step 7: Validation
    print("\n🔍 Step 7: Validating HTML files...")
    validation_results = []
    critical_errors = 0

    sample_size = min(100, len(all_files))
    sample_files = random.sample(all_files, sample_size)

    for fp in sample_files:
        result = validate_html(fp)
        validation_results.append(result)
        if not result["ok"] and result["errors"]:
            critical_errors += 1
            if critical_errors <= 5:  # Show first 5 errors
                print(f"   ⚠️  {result['file']}: {result['errors'][0]}")

    print(f"   Validated {sample_size} sample files")
    print(f"   With errors: {critical_errors}")

    # Final Report
    print("\n" + "=" * 60)
    print("║            FINAL REPORT                      ║")
    print("=" * 60)
    print(f"  📄 Total files processed:    {STATS['total_processed']}")
    print(f"  🧭 Nav updated:              {STATS['nav_updated']}")
    print(f"  📦 B2B cards enhanced:       {STATS['b2b_enhanced']}")
    print(f"  🌐 Engineering Directories:  {STATS['directory_added']}")
    print(f"  🔗 Hreflang fixed:           {STATS['hreflang_fixed']}")
    print(f"  ❌ Errors:                   {STATS['errors']}")
    print(f"  ⏭️  Skipped:                  {STATS['skipped']}")
    print(f"  ───────────────────────────────────")
    print(f"  🗺️  Total sitemap URLs:       {total_sitemap_urls}")
    print(f"  ✅ HTML validation pass:     {sample_size - critical_errors}/{sample_size}")
    print("=" * 60)

    # Save report
    report = {
        "date": DATE,
        "stats": dict(STATS),
        "sitemap_total_urls": total_sitemap_urls,
        "sitemap_details": dict(sitemap_details),
        "validation_sample": sample_size,
        "validation_errors": critical_errors,
    }
    (ROOT / "optimization-report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False)
    )
    print(f"\n📝 Report saved to optimization-report.json")


if __name__ == "__main__":
    main()
