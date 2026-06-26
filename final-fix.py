#!/usr/bin/env python3
"""Final fixes: restore hreflang, add atmosphere to English tools"""
import re
from pathlib import Path

ROOT = Path("/Users/nicky/ZCodeProject/carbide-site")
SITE = "https://carbide-tooling.com"

LANG_MAP = {
    "en": "en", "de": "de", "jp": "ja", "es": "es", "vi": "vi",
}
LANG_ORDER = ["en", "de", "jp", "es", "vi"]

HERO_ATMO_CSS = """<style id="hero-atmo-style">
.hero-atmo{position:relative;width:100%;height:200px;overflow:hidden;background:linear-gradient(180deg,#f5f5f7 0%,#e8e8ed 40%,#d2d2d7 100%);margin-bottom:-60px;z-index:0}
.hero-atmo::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 80% 60% at 20% 50%,rgba(0,102,204,.06) 0%,transparent 50%),radial-gradient(ellipse 60% 80% at 80% 40%,rgba(0,0,0,.04) 0%,transparent 50%),linear-gradient(180deg,rgba(255,255,255,0) 0%,rgba(255,255,255,.95) 90%,#fff 100%)}
.hero-atmo::after{content:'';position:absolute;bottom:0;left:0;right:0;height:80px;background:linear-gradient(0deg,#fff 0%,transparent 100%)}
.img-container{width:100%;aspect-ratio:1;background:#fff;border-radius:20px;border:1px solid #d2d2d7;overflow:hidden;display:flex;align-items:center;justify-content:center;position:relative}
.img-container img{width:100%;height:100%;object-fit:cover}
.img-placeholder{width:100%;height:100%;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#f0f0f3 0%,#e8e8ed 50%,#f0f0f3 100%);color:#c0c0c6;font-size:48px}
.img-placeholder::after{content:'◆';font-size:48px;opacity:.3}
</style>"""

HERO_ATMO_HTML = '<div class="hero-atmo" aria-hidden="true"></div>'


def detect_lang(filepath):
    rel = str(filepath.relative_to(ROOT))
    for lc in ["de", "jp", "es", "vi", "zh"]:
        if rel.startswith(lc + "/") or rel.startswith(lc + "\\"):
            return lc
    return "en"


def build_hreflang_block(filepath, lang_code):
    rel = filepath.relative_to(ROOT)
    parts = list(rel.parts)

    if parts[0] in ["de", "jp", "es", "vi", "zh"]:
        path_parts = list(parts[1:])
    else:
        path_parts = list(parts)

    base = "/".join(path_parts)
    if base.endswith("/index.html"):
        base = base[:-len("index.html")]
    elif base == "index.html":
        base = ""

    tags = []
    # x-default
    en_url = f"{SITE}/{base}" if base else f"{SITE}/"
    tags.append(f'<link href="{en_url}" hreflang="x-default" rel="alternate"/>')
    
    for lc in LANG_ORDER:
        hl = LANG_MAP[lc]
        if lc == "en":
            href = en_url
        else:
            href = f"{SITE}/{lc}/{base}" if base else f"{SITE}/{lc}/"
        # Remove double slashes
        href = href.replace("//", "/").replace("https:/", "https://")
        tags.append(f'<link href="{href}" hreflang="{hl}" rel="alternate"/>')
    
    return "\n".join(tags)


def fix_file(filepath):
    content = filepath.read_text(encoding="utf-8")
    modified = False
    lang = detect_lang(filepath)

    # 1. Fix hreflang - remove ALL existing and inject fresh ones
    old_count = len(re.findall(r'<link[^>]*hreflang="[^"]*"[^>]*rel="alternate"[^>]*>', content))
    if old_count < 5:
        # Remove all existing hreflang links
        content = re.sub(r'<link[^>]*hreflang="[^"]*"[^>]*rel="alternate"[^>]*>\s*', '', content)
        # Inject fresh ones before </head>
        new_tags = build_hreflang_block(filepath, lang)
        content = content.replace('</head>', f'\n{new_tags}\n</head>', 1)
        modified = True

    # 2. Add atmosphere to English tool pages
    rel_str = str(filepath.relative_to(ROOT))
    is_en_tool = (lang == "en" and
                  rel_str.startswith("tools/") and
                  "/" in rel_str[len("tools/"):] and  # has subdirectory after tools/
                  filepath.name == "index.html")
    
    if is_en_tool and 'hero-atmo' not in content:
        # Add CSS in head if not present
        if 'hero-atmo-style' not in content:
            content = content.replace('</head>', f'{HERO_ATMO_CSS}\n</head>', 1)
        # Add HTML after body
        content = re.sub(r'(<body[^>]*>)', r'\1\n' + HERO_ATMO_HTML, content, count=1)
        modified = True

    if modified:
        filepath.write_text(content, encoding="utf-8")
        return True
    return False


def main():
    fixed = 0
    for f in ROOT.rglob("*.html"):
        if ".git" in str(f) or ".venv" in str(f) or "__pycache__" in str(f):
            continue
        if fix_file(f):
            fixed += 1
    print(f"Fixed {fixed} files")

if __name__ == "__main__":
    main()
