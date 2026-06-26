"""
Fix V7: Fix nav on ALL non-English non-tool pages (40 pages)
- Replace old 5-link nav + inline language switcher
- With new 4-link nav + flag dropdown language switcher
"""
import os, re, glob

ROOT = '/Users/nicky/ZCodeProject/carbide-site'

# Nav labels per language
NAV = {
    'de': {
        'home': '/de/',
        'products': 'Produkte',
        'tools': 'Rechner & Werkzeuge',
        'guides': 'Anleitungen',
        'about': 'Über uns',
        'quote_label': '📩 Angebot anfordern',
        'quote_href': '/de/quote.html',
    },
    'jp': {
        'home': '/jp/',
        'products': '製品',
        'tools': '計算機 & ツール',
        'guides': 'ガイド',
        'about': '会社概要',
        'quote_label': '📩 見積もり依頼',
        'quote_href': '/jp/quote.html',
    },
    'es': {
        'home': '/es/',
        'products': 'Productos',
        'tools': 'Calculadoras & Herramientas',
        'guides': 'Guías',
        'about': 'Acerca de',
        'quote_label': '📩 Solicitar cotización',
        'quote_href': '/es/quote.html',
    },
    'vi': {
        'home': '/vi/',
        'products': 'Sản phẩm',
        'tools': 'Máy Tính & Công cụ',
        'guides': 'Hướng dẫn',
        'about': 'Về chúng tôi',
        'quote_label': '📩 Yêu cầu báo giá',
        'quote_href': '/vi/quote.html',
    },
}

LANG_NAMES = {
    'en': ('🇺🇸', 'EN', 'English'),
    'de': ('🇩🇪', 'DE', 'Deutsch'),
    'jp': ('🯈', 'JP', '日本語'),
    'es': ('🇪🇸', 'ES', 'Español'),
    'vi': ('🇻🇳', 'VI', 'Tiếng Việt'),
}

LANG_FLAGS = {
    'en': '🇺🇸',
    'de': '🇩🇪',
    'jp': '🇯🇵',
    'es': '🇪🇸',
    'vi': '🇻🇳',
}


def build_nav_html(lang, page_path):
    n = NAV[lang]
    rel_path = page_path.replace(f'{lang}/', '')
    
    dd_links = []
    for lcode in ['en', 'de', 'jp', 'es', 'vi']:
        flag, lbl, nm = LANG_NAMES[lcode]
        if rel_path == 'index.html':
            href = '/' if lcode == 'en' else f'/{lcode}/'
        elif lcode == 'en':
            href = f'/{rel_path}'
        else:
            href = f'/{lcode}/{rel_path}'
        
        cls = 'current' if lcode == lang else ''
        dd_links.append(
            '<a href="%s" class="%s"><span class="flag">%s</span>'
            '<span class="lbl">%s</span><span class="nm">%s</span></a>' 
            % (href, cls, flag, lbl, nm)
        )
    
    guides_label = n.get('guides', 'Guides')
    
    return (
        '<nav id="nav-v2">\n'
        '<div class="nv-inner">\n'
        '<a class="nv-logo" href="%s"><span>◆</span> Carbide Tooling</a>\n'
        '<div class="nv-links">\n'
        '<a href="/%s/products/">%s</a>\n'
        '<a href="/%s/tools/">%s</a>\n'
        '<a href="/%s/guides/">%s</a>\n'
        '<a href="/%s/about.html">%s</a>\n'
        '</div>\n'
        '<div class="nv-right">\n'
        '<div class="nv-lang"><div class="lang-btn" onclick="toggleLangDD(event)">'
        '<span class="flag">%s</span><span>%s</span><span class="caret">▼</span></div>'
        '<div class="lang-dd" id="lang-dd">'
        '%s'
        '</div></div>\n'
        '<a class="nv-quote" href="%s">%s</a>\n'
        '</div>\n'
        '</div>\n'
        '</nav>' % (
            n['home'], lang, n['products'],             lang, n['tools'],
            lang, guides_label,
            lang, n['about'],
            LANG_FLAGS[lang], lang.upper(), ''.join(dd_links),
            n['quote_href'], n['quote_label']
        )
    )


NEW_LANG_CSS = (".lang-btn{display:flex;align-items:center;gap:4px;padding:4px 10px;border-radius:20px;"
                "background:#f5f5f7;border:1px solid #e8e8ed;font-size:12px;font-weight:600;color:#1d1d1f;"
                "cursor:pointer;transition:all .2s;position:relative;user-select:none;letter-spacing:.3px}"
".lang-btn:hover{background:#e8e8ed;border-color:#d2d2d7}"
".lang-btn .flag{font-size:14px;line-height:1}"
".lang-btn .caret{font-size:8px;opacity:.5;margin-left:2px}"
".lang-dd{display:none;position:absolute;top:calc(100% + 6px);right:0;background:#fff;border:1px solid #e8e8ed;"
"border-radius:12px;box-shadow:0 8px 30px rgba(0,0,0,.12);padding:6px;z-index:300;min-width:140px}"
".lang-dd.open{display:block;animation:ddIn .15s ease}"
"@keyframes ddIn{from{opacity:0;transform:translateY(-4px)}to{opacity:1;transform:translateY(0)}}"
".lang-dd a{display:flex;align-items:center;gap:8px;padding:8px 12px;border-radius:8px;text-decoration:none;font-size:13px;color:#1d1d1f;"
"transition:background .15s;white-space:nowrap;font-weight:500}"
".lang-dd a:hover{background:#f5f5f7}"
".lang-dd a.current{color:#0066cc;font-weight:700;background:#f0f7ff}"
".lang-dd a .flag{font-size:18px;line-height:1}"
".lang-dd a .lbl{font-weight:600;letter-spacing:.3px}"
".lang-dd a .nm{font-weight:400;color:#86868b;font-size:11px;margin-left:auto}")

JS_TOGGLE = "<script>\nfunction toggleLangDD(e){e.stopPropagation();var d=document.getElementById('lang-dd');d.classList.toggle('open')}" \
            "\ndocument.addEventListener('click',function(){var d=document.getElementById('lang-dd');if(d)d.classList.remove('open')})\n</script>"

fixed = 0
for lang in ['de', 'jp', 'es', 'vi']:
    base = os.path.join(ROOT, lang)
    
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d != 'tools']
        
        for fname in sorted(files):
            if not fname.endswith('.html'):
                continue
            
            fp = os.path.join(root, fname)
            rel_path = os.path.relpath(fp, ROOT)
            
            with open(fp, 'r') as f:
                html = f.read()
            
            original = html
            
            # 1. Replace old nav block
            old_nav_pattern = r'<nav id="nav-v2">.*?</nav>'
            new_nav = build_nav_html(lang, rel_path)
            html = re.sub(old_nav_pattern, new_nav, html, flags=re.DOTALL)
            
            # 2. Replace old nv-lang CSS block (from nv-lang to @media)
            # Match everything from "nav#nav-v2 .nv-lang{" up to but not including "@media"
            css_match = re.search(
                r'(nav#nav-v2 \.nv-lang\{.*?)(@media\(max-width)',
                html,
                re.DOTALL
            )
            if css_match:
                html = html[:css_match.start(1)] + NEW_LANG_CSS + '\n' + css_match.group(2) + html[css_match.end(2):]
            
            # 3. Fix mobile nav-links
            html = re.sub(
                r'nav#nav-v2 \.nv-links\{display:none\}',
                'nav#nav-v2 .nv-links{display:flex;align-items:center;gap:0;flex-wrap:wrap;order:2;width:100%;justify-content:center}',
                html,
                count=1
            )
            
            # 4. Ensure position:relative on nv-lang
            html = re.sub(
                r'(nav#nav-v2 \.nv-lang)\{',
                r'\1{position:relative;display:flex;align-items:center;',
                html,
                count=1
            )
            
            # 5. Ensure toggleLangDD JS
            if 'toggleLangDD' not in html:
                html = JS_TOGGLE + '</body>' if '</body>' in html else html
            
            # Clean extra blank lines
            html = re.sub(r'\n{3,}', '\n\n', html)
            
            if html != original:
                with open(fp, 'w') as f:
                    f.write(html)
                print("  OK %s" % rel_path)
                fixed += 1

print("\nFixed: %d pages" % fixed)
