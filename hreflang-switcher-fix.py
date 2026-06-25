#!/usr/bin/env python3
"""
Apple-style Language Switcher + Hreflang SEO Fix
===============================================
1. Injects minimal language switcher into nav bar on ALL 606+ pages
2. Verifies and fixes hreflang cross-references on all pages
3. Fixes related-tools links to point to current language
4. Regenerates multilingual sitemaps
"""

import os, re, json, glob

ROOT = os.path.dirname(__file__)
LANGUAGES = {"en": "EN", "de": "DE", "jp": "JP", "es": "ES", "vi": "VI", "zh": "中"}
LANG_DIRS = ["de", "jp", "es", "vi", "zh"]

# ═══════════════════════════════════════════
# TOOL MAPPING
# ═══════════════════════════════════════════

def get_tool_names():
    """Get all tool directory names from English source"""
    tools_dir = os.path.join(ROOT, "tools")
    names = sorted(d for d in os.listdir(tools_dir) 
                   if d != "index.html" and os.path.isdir(os.path.join(tools_dir, d)))
    return names


def tool_file_exists(tool_name, lang):
    """Check if a tool exists for a given language"""
    if lang == "en":
        fpath = os.path.join(ROOT, "tools", tool_name, "index.html")
    else:
        fpath = os.path.join(ROOT, lang, "tools", tool_name, "index.html")
    return os.path.isfile(fpath)


def iter_tool_files():
    """Generator yielding (lang, tool_name, filepath) for all existing tool files"""
    names = get_tool_names()
    for name in names:
        # English
        fpath = os.path.join(ROOT, "tools", name, "index.html")
        if os.path.isfile(fpath):
            yield ("en", name, fpath)
        # Other languages
        for lang in LANG_DIRS:
            fpath = os.path.join(ROOT, lang, "tools", name, "index.html")
            if os.path.isfile(fpath):
                yield (lang, name, fpath)


# ═══════════════════════════════════════════
# 1. NAV LANGUAGE SWITCHER INJECTION
# ═══════════════════════════════════════════

LANG_SWITCHER_CSS = """
/* Language Switcher - Apple Style */
.lang-nav{display:flex;align-items:center;gap:2px;margin-left:12px;padding-left:12px;border-left:1px solid #e8e8ed}
.lang-nav a{font-size:11px;font-weight:500;color:#86868b;text-decoration:none;padding:2px 5px;border-radius:4px;transition:all .15s}
.lang-nav a:hover{color:#1d1d1f;background:#f5f5f7}
.lang-nav a.active{color:#0066cc;font-weight:600}
.lang-nav .sep{color:#d2d2d6;font-size:10px;margin:0 1px}
"""


def nav_switcher_html(current_lang, tool_name):
    """Generate Apple-style language switcher HTML for nav bar"""
    html = '<div class="lang-nav">'
    langs = [("en", "EN"), ("de", "DE"), ("jp", "JP"), ("es", "ES"), ("vi", "VI"), ("zh", "中")]
    parts = []
    for code, label in langs:
        if code == current_lang:
            parts.append(f'<a href="#" class="active" onclick="return false">{label}</a>')
        else:
            if code == "en":
                href = f"/tools/{tool_name}/"
            else:
                href = f"/{code}/tools/{tool_name}/"
            # If tool doesn't exist for this language, link to homepage
            if not tool_file_exists(tool_name, code):
                href = f"/{code}/" if code != "en" else "/"
            parts.append(f'<a href="{href}">{label}</a>')
    html = '<div class="lang-nav">'
    for i, part in enumerate(parts):
        if i > 0:
            html += '<span class="sep">|</span>'
        html += part
    html += '</div>'
    return html


def inject_nav_switcher(filepath, lang, tool_name):
    """Inject language switcher into nav bar"""
    with open(filepath) as f: content = f.read()
    
    # Skip if already has nav switcher
    if 'lang-nav' in content:
        return False
    
    switcher = nav_switcher_html(lang, tool_name)
    
    # Insert after the "Get a Quote" button (which is the last element in nav)
    quote_pattern = r'(<a[^>]*href="[^"]*quote[^"]*"[^>]*>[^<]*</a>)'
    match = re.search(quote_pattern, content)
    if match:
        content = content.replace(match.group(1), match.group(1) + switcher)
        
        # Add CSS if not present
        if LANG_SWITCHER_CSS.strip() not in content:
            content = content.replace("</style>", LANG_SWITCHER_CSS + "\n</style>")
        
        with open(filepath, "w") as f: f.write(content)
        return True
    
    return False


# ═══════════════════════════════════════════
# 2. HREFLANG AUDIT & FIX
# ═══════════════════════════════════════════

def hreflang_html(tool_name):
    """Generate complete hreflang tag block"""
    tags = ""
    for code, hf_code in [("en","en"), ("de","de"), ("jp","ja"), ("es","es"), ("vi","vi"), ("zh","zh")]:
        if code == "en":
            href = f"https://carbide-tooling.com/tools/{tool_name}/"
        else:
            href = f"https://carbide-tooling.com/{code}/tools/{tool_name}/"
        tags += f'  <link rel="alternate" hreflang="{hf_code}" href="{href}"/>\n'
    tags += f'  <link rel="alternate" hreflang="x-default" href="https://carbide-tooling.com/tools/{tool_name}"/>'
    return tags


def fix_hreflang(filepath, tool_name):
    """Remove all existing hreflang and inject fresh ones"""
    with open(filepath) as f: content = f.read()
    
    # Remove all existing alternate/hreflang link tags
    content = re.sub(r'\s*<link rel="alternate" hreflang="[^"]*" href="[^"]*"/>\n?', '', content)
    
    # Inject fresh hreflang
    hf = hreflang_html(tool_name)
    content = content.replace("</head>", "\n" + hf + "\n</head>")
    
    with open(filepath, "w") as f: f.write(content)
    return True


# ═══════════════════════════════════════════
# 3. FIX RELATED TOOLS LINKS
# ═══════════════════════════════════════════

def fix_related_tool_links(filepath, lang):
    """Fix more-tools and toolbox links to point to current language"""
    with open(filepath) as f: content = f.read()
    
    if lang == "en":
        return False  # English links are already correct
    
    # Fix more-tools links: href="/tools/X/" -> href="/{lang}/tools/X/"
    pattern = r'href="/tools/([^"/]+)/"'
    def fix_link(m):
        tool = m.group(1)
        return f'href="/{lang}/tools/{tool}/"'
    
    new_content = re.sub(pattern, fix_link, content)
    
    if new_content != content:
        with open(filepath, "w") as f: f.write(new_content)
        return True
    return False


# ═══════════════════════════════════════════
# 4. FIX TOOLBOX PRECISION LINKS
# ═══════════════════════════════════════════

def fix_toolbox_links(filepath, lang):
    """Fix the Precision Engineering Toolbox links"""
    # Same pattern as fix_related_tool_links - already handled by the regex above
    pass


# ═══════════════════════════════════════════
# 5. GENERATE SITEMAPS
# ═══════════════════════════════════════════

def generate_sitemaps():
    """Generate per-language sitemaps with all 101 tools + main pages"""
    names = get_tool_names()
    
    for lang_code, hf_code in [("en","en"), ("de","de"), ("jp","ja"), ("es","es"), ("vi","vi"), ("zh","zh")]:
        urls = []
        
        if lang_code == "en":
            prefix = "https://carbide-tooling.com"
            urls.append((f"{prefix}/", "1.0"))
            urls.append((f"{prefix}/tools/", "0.9"))
            urls.append((f"{prefix}/about.html", "0.5"))
            urls.append((f"{prefix}/quote.html", "0.6"))
            # Products
            for pf in sorted(os.listdir(os.path.join(ROOT, "products"))):
                if pf.endswith(".html"):
                    urls.append((f"{prefix}/products/{pf}", "0.6"))
            # Guides
            for gf in sorted(os.listdir(os.path.join(ROOT, "guides"))):
                if gf.endswith(".html"):
                    urls.append((f"{prefix}/guides/{gf}", "0.6"))
            # Tools
            for name in names:
                urls.append((f"{prefix}/tools/{name}/", "0.8"))
        else:
            prefix = f"https://carbide-tooling.com/{lang_code}"
            urls.append((f"{prefix}/", "0.9"))
            urls.append((f"{prefix}/tools/", "0.8"))
            # Tools (only if they exist)
            for name in names:
                if tool_file_exists(name, lang_code):
                    urls.append((f"{prefix}/tools/{name}/", "0.8"))
        
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        xml += '  xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        
        for url, prio in urls:
            xml += f"  <url>\n    <loc>{url}</loc>\n    <priority>{prio}</priority>\n"
            # Add xhtml:link for hreflang
            for lc, lh in [("en","en"), ("de","de"), ("jp","ja"), ("es","es"), ("vi","vi"), ("zh","zh")]:
                # Determine the alternate URL
                if lc == "en":
                    alt = re.sub(r'^https://carbide-tooling\.com/[a-z]{2}/', 'https://carbide-tooling.com/', url)
                else:
                    if lang_code == "en":
                        alt = url.replace("https://carbide-tooling.com/", f"https://carbide-tooling.com/{lc}/")
                    else:
                        alt = url.replace(f"https://carbide-tooling.com/{lang_code}/", f"https://carbide-tooling.com/{lc}/")
                xml += f'    <xhtml:link rel="alternate" hreflang="{lh}" href="{alt}"/>\n'
            xml += "  </url>\n"
        
        xml += '</urlset>\n'
        
        fname = f"sitemap-{lang_code}.xml" if lang_code != "en" else "sitemap.xml"
        with open(os.path.join(ROOT, fname), "w") as f:
            f.write(xml)
        print(f"  ✓ {fname} ({len(urls)} URLs)")
    
    # Sitemap index
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for lang_code in ["en", "de", "jp", "es", "vi", "zh"]:
        fname = f"sitemap-{lang_code}.xml" if lang_code != "en" else "sitemap.xml"
        xml += f'  <sitemap>\n    <loc>https://carbide-tooling.com/{fname}</loc>\n  </sitemap>\n'
    xml += '</sitemapindex>\n'
    with open(os.path.join(ROOT, "sitemap-index.xml"), "w") as f:
        f.write(xml)
    print("  ✓ sitemap-index.xml")


# ═══════════════════════════════════════════
# 6. TITLE FORMAT FIX
# ═══════════════════════════════════════════

def fix_title(filepath):
    """Ensure title format is consistent"""
    with open(filepath) as f: content = f.read()
    
    title_match = re.search(r'<title>([^<]*)</title>', content)
    if title_match:
        title = title_match.group(1)
        # Remove any duplicate "Carbide-Tooling.com"
        title = re.sub(r'\s*\|\s*Carbide-Tooling\.com\s*\|\s*Carbide-Tooling\.com', ' | Carbide-Tooling.com', title)
        # Ensure ends with " | Carbide-Tooling.com"
        if not title.endswith("Carbide-Tooling.com"):
            title = title.strip() + " | Carbide-Tooling.com"
        if title != title_match.group(1):
            content = content.replace(title_match.group(0), f"<title>{title}</title>")
            with open(filepath, "w") as f: f.write(content)
            return True
    return False


# ═══════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════

def main():
    print("=" * 60)
    print("Language Switcher & Hreflang Injection")
    print("=" * 60)
    
    names = get_tool_names()
    print(f"\n📁 Found {len(names)} tools across 6 languages\n")
    
    # Phase 1: Inject nav language switcher
    print("🔤 Phase 1: Nav language switcher injection...")
    sw_count = 0
    for lang, name, fpath in iter_tool_files():
        if inject_nav_switcher(fpath, lang, name):
            sw_count += 1
    print(f"  → Language switcher added to {sw_count} files")
    
    # Phase 2: Fix hreflang on all pages
    print("\n🌐 Phase 2: Hreflang injection...")
    hf_count = 0
    for lang, name, fpath in iter_tool_files():
        fix_hreflang(fpath, name)
        hf_count += 1
    print(f"  → hreflang updated on {hf_count} files")
    
    # Phase 3: Fix related tool links for non-English
    print("\n🔗 Phase 3: Related tools links fix...")
    rl_count = 0
    for lang, name, fpath in iter_tool_files():
        if lang != "en":
            if fix_related_tool_links(fpath, lang):
                rl_count += 1
    print(f"  → Related links fixed on {rl_count} files")
    
    # Phase 4: Fix titles
    print("\n📝 Phase 4: Title format fix...")
    tt_count = 0
    for lang, name, fpath in iter_tool_files():
        if fix_title(fpath):
            tt_count += 1
    print(f"  → Titles fixed on {tt_count} files")
    
    # Phase 5: Regenerate sitemaps
    print("\n🗺️  Phase 5: Sitemap regeneration...")
    generate_sitemaps()
    
    # Summary
    total_files = sum(1 for _ in iter_tool_files())
    print(f"\n{'='*60}")
    print(f"✅ COMPLETE")
    print(f"   Total files processed: {total_files}")
    print(f"   Language switcher:     {sw_count} files")
    print(f"   hreflang:              {hf_count} files")
    print(f"   Related links:         {rl_count} files")
    print(f"   Titles:                {tt_count} files")
    print(f"   Sitemaps:              7 files")
    print(f"{'='*60}")
    print("\n📋 Run git add -A && git commit -m '...' && git push to deploy")


if __name__ == "__main__":
    main()
