#!/usr/bin/env python3
"""
Language Switcher Redesign + Translation Fixes
=============================================
- Removes Chinese (zh)
- Dropdown button + flags (click to show, click outside to close)
- Fixes partial translation artifacts ("結果s", mixed languages)
- Adds switcher to homepage
- Fixes tool names in "more-tools" sections per language
- Regenerates sitemaps
"""

import os, re, shutil

ROOT = os.path.dirname(__file__)
LANG_DIRS = ["de", "jp", "es", "vi"]
ALL_LANGS = ["en"] + LANG_DIRS

# ── Flag emoji mapping ──
FLAGS = {"en": "🇬🇧", "de": "🇩🇪", "jp": "🇯🇵", "es": "🇪🇸", "vi": "🇻🇳"}
LANG_NAMES = {"en": "EN", "de": "DE", "jp": "JP", "es": "ES", "vi": "VI"}

# ── Fix common translation artifacts ──
# These fix the word-replacement damage
TRANSLATION_FIXES = {
    "de": [
        (r"Ergebnis\bs\b", "Ergebnisse"),  # fix plural
        (r"Ergebnis Ergebnis", "Ergebnis"),
        (r"Rechner Rechner", "Rechner"),
        (r"Umrechner Umrechner", "Umrechner"),
        (r"Leitfaden Leitfaden", "Leitfaden"),
    ],
    "jp": [
        (r"結果s", "結果"),
        (r"計算s", "計算"),
        (r"出力s", "出力"),
        (r"入力s", "入力"),
        (r"値s", "値"),
        (r"結果 結果", "結果"),
        (r"計算機 計算機", "計算機"),
        (r"(ツール|工具|ガイド|換算|計算)\s+\1", r"\1"),
    ],
    "es": [
        (r"Resultado\bs\b", "Resultados"),
        (r"Resultado Resultado", "Resultado"),
        (r"Calculadora Calculadora", "Calculadora"),
        (r"Convertidor Convertidor", "Convertidor"),
    ],
    "vi": [
        (r"Kết quảs", "Kết quả"),
        (r"Kết quả Kết quả", "Kết quả"),
        (r"Máy tính Máy tính", "Máy tính"),
        (r"Bộ chuyển đổi Bộ chuyển đổi", "Bộ chuyển đổi"),
    ]
}

# ── Tool name translations for more-tools section ──
TOOL_NAMES = {
    "de": {
        "speed-feed": "Schnittgeschwindigkeit & Vorschub",
        "chip-load": "Spanbelastung",
        "surface-speed": "Schnittgeschwindigkeit (SFM)",
        "mrr-calculator": "Zerspanungsvolumen (MRR)",
        "horsepower-calculator": "Spindelleistung",
        "force-calculator": "Zerspankraft",
        "cycle-time-calculator": "Zykluszeit",
        "surface-roughness-calculator": "Oberflächenrauheit",
        "nose-radius-compensation": "Eckenradius-Kompensation",
        "ramping-angle-calculator": "Rampenwinkel",
        "trochoidal-milling-calculator": "Trochoidalfräsen",
        "slot-milling-calculator": "Nutenfräsen",
        "step-milling-calculator": "Stufenfräsen",
        "ball-nose-effective-diameter": "Wirksamer Kugelfräserdurchmesser",
        "helical-interpolation-calculator": "Helixinterpolation",
        "heat-expansion-calculator": "Wärmeausdehnung",
        "tool-runout-calculator": "Rundlauf",
        "feed-rate-override-calculator": "Vorschub-Override",
        "tap-drill-size-calculator": "Gewindebohrer-Kernloch",
        "tapping-feed-rate-calculator": "Gewindebohr-Vorschub",
        "drill-point-length-calculator": "Bohrerspitzenlänge",
        "thread-depth-torque-calculator": "Gewindetiefe & Drehmoment",
        "metric-imperial-thread-converter": "Metrisch/Zoll-Gewinde",
        "npt-pipe-thread-calculator": "NPT-Rohrgewinde",
        "percentage-of-thread-calculator": "Gewindeeingriffsgrad",
        "form-tap-drill-calculator": "Gewindeform-Kernloch",
        "thread-lead-angle-calculator": "Gewindesteigungswinkel",
        "thread-pitch-diameter-calculator": "Gewinde-Flankendurchmesser",
        "step-drill-design-calculator": "Stufenbohrer-Design",
        "countersink-depth-calculator": "Senktiefe",
        "reaming-allowance-calculator": "Reibaufmaß",
        "gun-drill-calculator": "Tiefbohren",
        "blind-hole-tapping-calculator": "Sackloch-Gewindebohren",
        "grade-reference": "Sorten-Referenz",
        "carbide-grade-cross-ref-2": "Hartmetallsorten-Vergleich",
        "metal-weight-calculator": "Hartmetall-Gewicht",
        "metal-cost-calculator": "Metallkosten",
        "hardness-converter": "Härteumrechner",
        "machinability-rating": "Zerspanbarkeitsbewertung",
        "stainless-properties": "Edelstahl-Eigenschaften",
        "titanium-machining-guide": "Titan-Bearbeitungsleitfaden",
        "aluminum-alloy-table": "Aluminiumlegierungs-Tabelle",
        "tool-steel-heat-treat": "Werkzeugstahl-Wärmebehandlung",
        "cast-iron-machining": "Gusseisen-Bearbeitung",
        "coating-selector": "Beschichtungsauswahl",
        "tensile-strength-converter": "Zugfestigkeitsumrechner",
        "plastic-machining": "Kunststoff-Bearbeitung",
        "graphite-machining": "Graphit-Bearbeitung",
        "brass-machining-parameters": "Messing-Bearbeitung",
        "superalloy-tool-life": "Superlegierungs-Standzeit",
        "cost-per-part-calculator": "Stückkosten",
        "tool-life-economics": "Standzeit-Wirtschaftlichkeit",
        "cnc-roi-calculator": "CNC-ROI",
        "batch-cost-calculator": "Chargenkosten",
        "scrap-value-calculator": "Abfallwert",
        "iso-fit-calculator": "ISO-Passungen",
        "bolt-circle-calculator": "Lochkreise",
        "flatness-calculator": "Ebenheit",
        "sine-bar-calculator": "Sinusschiene",
        "coord-rotation-calculator": "Koordinatendrehung",
        "chamfer-calculator": "Fasenberechnung",
        "taper-calculator": "Konusberechnung",
        "gdt-symbols-reference": "GD&T-Symbole",
        "keyway-depth-calculator": "Nuttiefe",
        "dovetail-calculator": "Schwalbenschwanz",
        "gear-parameter-calculator": "Zahnradparameter",
        "gcode-reference": "G-Code-Referenz",
        "mcode-reference": "M-Code-Referenz",
        "pressure-converter": "Druckumrechner",
        "torque-unit-converter": "Drehmomentumrechner",
        "ultimate-unit-converter": "Universal-Umrechner",
        "aql-sampling-calculator": "AQL-Stichprobenprüfung",
        "feed-converter": "Vorschub-Umrechner",
        "temp-converter": "Temperaturumrechner",
        "pythagorean-calculator": "Pythagoras-Rechner",
        "dia-circ-calculator": "Durchmesser/Umfang",
        "pomodoro-timer": "Pomodoro-Timer",
        "toolbox-organizer": "Werkzeugkasten-Organizer",
        "tool-wear-cost-calculator": "Werkzeugverschleißkosten",
        "tool-change-time-analyzer": "Werkzeugwechselzeit-Analyse",
        "inventory-turnover-calculator": "Lagerumschlag",
        "production-efficiency-calculator": "Produktionseffizienz",
        "engineering-interest-calculator": "Zinsrechner (Ing.)",
        "bulk-discount-calculator": "Mengenrabatt",
        "shipping-duty-estimator": "Versandkosten-Schätzer",
        "weight-shipping-calculator": "Gewicht & Versand",
        "microm-inch-converter": "Mikrometer/Zoll-Umrechner",
        "sfm-m-min-converter": "SFM/m/min-Umrechner",
        "tube-weight-calculator": "Rohrgewicht",
        "round-bar-weight": "Rundstahlgewicht",
        "wall-thickness-calculator": "Wanddicke",
        "metal-weight-calculator": "Metallgewicht",
    },
    "jp": {
        "speed-feed": "切削速度と送り",
        "chip-load": "チップ負荷",
        "surface-speed": "表面速度（SFM）",
        "mrr-calculator": "材料除去率（MRR）",
        "horsepower-calculator": "主軸出力",
        "force-calculator": "切削力",
        "cycle-time-calculator": "サイクルタイム",
        "surface-roughness-calculator": "表面粗さ",
        "nose-radius-compensation": "ノーズR補正",
        "ramping-angle-calculator": "ランプ角",
        "trochoidal-milling-calculator": "トロコイド加工",
        "slot-milling-calculator": "溝加工",
        "step-milling-calculator": "段階加工",
        "ball-nose-effective-diameter": "ボールエンドミル有効径",
        "helical-interpolation-calculator": "ヘリカル補間",
        "heat-expansion-calculator": "熱膨張",
        "tool-runout-calculator": "工具振れ",
        "feed-rate-override-calculator": "送りオーバーライド",
        "tap-drill-size-calculator": "タップ下穴径",
        "tapping-feed-rate-calculator": "タッピング送り",
        "drill-point-length-calculator": "ドリル先端長さ",
        "thread-depth-torque-calculator": "ねじ深さとトルク",
        "metric-imperial-thread-converter": "メートル/インチねじ換算",
        "npt-pipe-thread-calculator": "NPT管用ねじ",
        "percentage-of-thread-calculator": "ねじ山の率",
        "form-tap-drill-calculator": "転造タップ下穴",
        "thread-lead-angle-calculator": "ねじリード角",
        "thread-pitch-diameter-calculator": "ねじ有効径",
        "step-drill-design-calculator": "段付きドリル設計",
        "countersink-depth-calculator": "皿ざぐり深さ",
        "reaming-allowance-calculator": "リーマ代",
        "gun-drill-calculator": "ガンドリル",
        "blind-hole-tapping-calculator": "止り穴タッピング",
        "grade-reference": "グレード一覧",
        "carbide-grade-cross-ref-2": "超硬グレード比較",
        "hardness-converter": "硬さ換算",
        "stainless-properties": "ステンレス特性",
        "titanium-machining-guide": "チタン加工ガイド",
        "cost-per-part-calculator": "部品単価計算",
        "feed-converter": "送り換算",
        "temp-converter": "温度換算"
    },
    "es": {
        "speed-feed": "Velocidad y avance",
        "chip-load": "Carga de viruta",
        "hardness-converter": "Convertidor de dureza",
        "feed-converter": "Convertidor de avance",
        "temp-converter": "Convertidor de temperatura",
        "tap-drill-size-calculator": "Calculadora de broca para roscar",
        "titanium-machining-guide": "Guía de mecanizado de titanio",
        "surface-speed": "Velocidad superficial (SFM)",
        "mrr-calculator": "Calculadora MRR",
        "horsepower-calculator": "Potencia del husillo",
    },
    "vi": {
        "speed-feed": "Tốc độ & lượng chạy dao",
        "chip-load": "Tải phoi",
        "hardness-converter": "Chuyển đổi độ cứng",
        "feed-converter": "Chuyển đổi lượng chạy dao",
        "temp-converter": "Chuyển đổi nhiệt độ",
        "tap-drill-size-calculator": "Kích thước mũi khoan ren",
    }
}


def get_tool_names():
    tools_dir = os.path.join(ROOT, "tools")
    return sorted(d for d in os.listdir(tools_dir) if d != "index.html" and os.path.isdir(os.path.join(tools_dir, d)))


def run_fixes():
    """Apply all fixes"""
    names = get_tool_names()
    total_fixed = 0
    
    # ══════════════════════════════════════════════════════
    # 1. Remove zh from all existing hreflang on all pages
    # ══════════════════════════════════════════════════════
    print("🗑️  Removing Chinese (zh) from all pages...")
    zh_count = 0
    for lang in ALL_LANGS:
        td = os.path.join(ROOT, "tools") if lang == "en" else os.path.join(ROOT, lang, "tools")
        for name in os.listdir(td):
            if name == "index.html": continue
            fpath = os.path.join(td, name, "index.html")
            if not os.path.isfile(fpath): continue
            with open(fpath) as f: content = f.read()
            if "hreflang=\"zh\"" in content or "/zh/" in content or "中" in content:
                # Remove zh hreflang lines
                content = re.sub(r'\s*<link rel="alternate" hreflang="zh" href="[^"]*"/>\n?', '', content)
                # Remove 中 from language switcher
                content = re.sub(r'\s*<span class="sep">\|</span><a[^>]*>中</a>', '', content)
                content = re.sub(r'\s*<a[^>]*>中</a>', '', content)
                with open(fpath, "w") as f: f.write(content)
                zh_count += 1
    print(f"   Removed zh from {zh_count} files")
    
    # ══════════════════════════════════════════════════════
    # 2. Replace old inline switcher with dropdown button + flags
    # ══════════════════════════════════════════════════════
    print("\n🔽 Replacing language switcher with dropdown + flags...")
    
    dropdown_css = """
/* Language Switcher - Dropdown with Flags */
.lang-btn{display:inline-flex;align-items:center;gap:4px;background:none;border:1px solid #e8e8ed;border-radius:8px;padding:3px 8px;cursor:pointer;font-size:13px;line-height:1;transition:all .15s;margin-left:8px}
.lang-btn:hover{background:#f5f5f7;border-color:#d2d2d6}
.lang-btn .arrow{font-size:8px;color:#86868b;margin-left:2px}
.lang-dropdown{position:relative;display:inline-flex;align-items:center}
.lang-menu{display:none;position:absolute;top:100%;right:0;margin-top:4px;background:#fff;border:1px solid #e8e8ed;border-radius:10px;box-shadow:0 8px 24px rgba(0,0,0,.1);padding:4px;z-index:200;min-width:100px}
.lang-menu.show{display:block}
.lang-menu a{display:flex;align-items:center;gap:6px;padding:6px 12px;border-radius:6px;text-decoration:none;font-size:12px;color:#1d1d1f;transition:background .1s;white-space:nowrap}
.lang-menu a:hover{background:#f5f5f7}
.lang-menu a.active{color:#0066cc;font-weight:600;background:#f0f7ff}
.lang-menu a .flag{font-size:16px}"""
    
    # Add dropdown JS
    dropdown_js = """
<script>
function toggleLang(e){e.stopPropagation();var m=document.getElementById('lang-menu');if(m)m.classList.toggle('show')}
document.addEventListener('click',function(){var m=document.getElementById('lang-menu');if(m)m.classList.remove('show')});
</script>"""
    
    sw_count = 0
    for lang in ALL_LANGS:
        td = os.path.join(ROOT, "tools") if lang == "en" else os.path.join(ROOT, lang, "tools")
        for name in os.listdir(td):
            if name == "index.html": continue
            fpath = os.path.join(td, name, "index.html")
            if not os.path.isfile(fpath): continue
            
            with open(fpath) as f: content = f.read()
            orig = content
            
            # Remove old lang-nav switcher
            content = re.sub(r'\s*<div class="lang-nav">.*?</div>', '', content, flags=re.DOTALL)
            
            # Remove old lang-switcher from footer
            content = re.sub(r'\s*<div class="lang-switcher">.*?</div>', '', content, flags=re.DOTALL)
            
            # Build dropdown HTML
            current_flag = FLAGS.get(lang, "🇬🇧")
            dd = f'\n<div class="lang-dropdown">\n<button class="lang-btn" onclick="toggleLang(event)"><span id="cf">{current_flag}</span><span class="arrow">▼</span></button>\n<div class="lang-menu" id="lang-menu">\n'
            for lc in ["en", "de", "jp", "es", "vi"]:
                active = ' class="active"' if lc == lang else ""
                flag = FLAGS[lc]
                lname = LANG_NAMES[lc]
                if lc == "en":
                    href = f"/tools/{name}/"
                else:
                    href = f"/{lc}/tools/{name}/"
                dd += f'<a href="{href}"{active}><span class="flag">{flag}</span> {lname}</a>\n'
            dd += '</div>\n</div>'
            
            # Insert after "Get a Quote" button
            content = re.sub(r'(</a>)\s*</div>\s*</nav>', r'\1' + dd + r'</div></nav>', content)
            
            # Add CSS if not present
            if dropdown_css.strip() not in content:
                content = content.replace("</style>", dropdown_css + "\n</style>")
            
            # Add JS if not present (before </body>)
            if 'toggleLang' not in content:
                content = content.replace("</body>", dropdown_js + "\n</body>")
            
            if content != orig:
                with open(fpath, "w") as f: f.write(content)
                sw_count += 1
    print(f"   Updated switcher on {sw_count} files")
    
    # ══════════════════════════════════════════════════════
    # 3. Fix translation artifacts
    # ══════════════════════════════════════════════════════
    print("\n🔧 Fixing translation artifacts...")
    fix_count = 0
    for lang in LANG_DIRS:
        fixes = TRANSLATION_FIXES.get(lang, [])
        if not fixes: continue
        td = os.path.join(ROOT, lang, "tools")
        for name in os.listdir(td):
            if name == "index.html": continue
            fpath = os.path.join(td, name, "index.html")
            if not os.path.isfile(fpath): continue
            with open(fpath) as f: content = f.read()
            orig = content
            for pattern, replacement in fixes:
                content = re.sub(pattern, replacement, content)
            if content != orig:
                with open(fpath, "w") as f: f.write(content)
                fix_count += 1
    print(f"   Fixed {fix_count} files")
    
    # ══════════════════════════════════════════════════════
    # 4. Fix tool names in more-tools sections per language
    # ══════════════════════════════════════════════════════
    print("\n📝 Fixing tool names in more-tools sections...")
    tn_count = 0
    for lang in LANG_DIRS:
        tnames = TOOL_NAMES.get(lang, {})
        if not tnames: continue
        td = os.path.join(ROOT, lang, "tools")
        for name in os.listdir(td):
            if name == "index.html": continue
            fpath = os.path.join(td, name, "index.html")
            if not os.path.isfile(fpath): continue
            with open(fpath) as f: content = f.read()
            orig = content
            # Fix tool names in links: <a href="/{lang}/tools/X/">English Name</a>
            for tool_key, localized_name in tnames.items():
                # Match links to this tool in same language
                old_link = f'href="/{lang}/tools/{tool_key}/">'
                # Find the enclosing <a> tag and replace the display text
                pattern = rf'(<a href="/{lang}/tools/{tool_key}/">)([^<]+)(</a>)'
                content = re.sub(pattern, rf'\1{localized_name}\3', content)
            if content != orig:
                with open(fpath, "w") as f: f.write(content)
                tn_count += 1
    print(f"   Fixed tool names in {tn_count} files")
    
    # ══════════════════════════════════════════════════════
    # 5. Add switcher to homepage
    # ══════════════════════════════════════════════════════
    print("\n🏠 Adding language switcher to homepage...")
    hp_path = os.path.join(ROOT, "index.html")
    if os.path.isfile(hp_path):
        with open(hp_path) as f: content = f.read()
        
        # Add CSS
        if dropdown_css.strip() not in content:
            content = content.replace("</style>", dropdown_css + "\n</style>")
        
        # Add JS
        if 'toggleLang' not in content:
            content = content.replace("</body>", dropdown_js + "\n</body>")
        
        # Add dropdown in nav, after "Get a Quote"
        dd_home = '\n<div class="lang-dropdown">\n<button class="lang-btn" onclick="toggleLang(event)"><span id="cf">🇬🇧</span><span class="arrow">▼</span></button>\n<div class="lang-menu" id="lang-menu">\n'
        for lc in ["en", "de", "jp", "es", "vi"]:
            flag = FLAGS[lc]
            lname = LANG_NAMES[lc]
            active = ' class="active"' if lc == "en" else ""
            href = "/" if lc == "en" else f"/{lc}/"
            dd_home += f'<a href="{href}"{active}><span class="flag">{flag}</span> {lname}</a>\n'
        dd_home += '</div>\n</div>'
        
        content = re.sub(r'(📩 Get a Quote</a>)\s*</div>\s*</nav>', r'\1' + dd_home + r'</div></nav>', content)
        
        with open(hp_path, "w") as f: f.write(content)
        print("   Homepage updated")
    
    # ══════════════════════════════════════════════════════
    # 6. Regenerate sitemaps
    # ══════════════════════════════════════════════════════
    print("\n🗺️  Regenerating sitemaps...")
    generate_sitemaps(names)
    
    print(f"\n✅ Done! Total files modified in this run: ~{sw_count + fix_count + tn_count}")


def generate_sitemaps(names):
    """Generate per-language sitemaps - NO Chinese"""
    langs = [("en","en"), ("de","de"), ("jp","ja"), ("es","es"), ("vi","vi")]
    
    for lang_code, hf_code in langs:
        urls = []
        if lang_code == "en":
            prefix = "https://carbide-tooling.com"
            urls.append((f"{prefix}/", "1.0"))
            urls.append((f"{prefix}/tools/", "0.9"))
            urls.append((f"{prefix}/about.html", "0.5"))
            urls.append((f"{prefix}/quote.html", "0.6"))
            for pf in sorted(os.listdir(os.path.join(ROOT, "products"))):
                if pf.endswith(".html"):
                    urls.append((f"{prefix}/products/{pf}", "0.6"))
            for gf in sorted(os.listdir(os.path.join(ROOT, "guides"))):
                if gf.endswith(".html"):
                    urls.append((f"{prefix}/guides/{gf}", "0.6"))
            for name in names:
                urls.append((f"{prefix}/tools/{name}/", "0.8"))
        else:
            prefix = f"https://carbide-tooling.com/{lang_code}"
            urls.append((f"{prefix}/", "0.9"))
            urls.append((f"{prefix}/tools/", "0.8"))
            for name in names:
                if os.path.isfile(os.path.join(ROOT, lang_code, "tools", name, "index.html")):
                    urls.append((f"{prefix}/tools/{name}/", "0.8"))
        
        alt_langs = [("en","en","https://carbide-tooling.com"), ("de","de","https://carbide-tooling.com/de"), ("jp","ja","https://carbide-tooling.com/jp"), ("es","es","https://carbide-tooling.com/es"), ("vi","vi","https://carbide-tooling.com/vi")]
        
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        for url, prio in urls:
            xml += f"  <url>\n    <loc>{url}</loc>\n    <priority>{prio}</priority>\n"
            for alc, ahf, apref in alt_langs:
                # Determine alternate URL
                if alc == lang_code:
                    alt_url = url
                elif alc == "en":
                    alt_url = re.sub(r'^https://carbide-tooling\.com/[a-z]{2}/', 'https://carbide-tooling.com/', url)
                else:
                    if lang_code == "en":
                        alt_url = url.replace("https://carbide-tooling.com/", f"https://carbide-tooling.com/{alc}/")
                    else:
                        alt_url = url.replace(f"https://carbide-tooling.com/{lang_code}/", f"https://carbide-tooling.com/{alc}/")
                xml += f'    <xhtml:link rel="alternate" hreflang="{ahf}" href="{alt_url}"/>\n'
            xml += "  </url>\n"
        xml += '</urlset>\n'
        
        fname = f"sitemap-{lang_code}.xml" if lang_code != "en" else "sitemap.xml"
        with open(os.path.join(ROOT, fname), "w") as f:
            f.write(xml)
        print(f"   ✓ {fname} ({len(urls)} URLs)")
    
    # Sitemap index (no zh)
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for lang_code, _, _ in alt_langs:
        fname = f"sitemap-{lang_code}.xml" if lang_code != "en" else "sitemap.xml"
        xml += f'  <sitemap>\n    <loc>https://carbide-tooling.com/{fname}</loc>\n  </sitemap>\n'
    xml += '</sitemapindex>\n'
    with open(os.path.join(ROOT, "sitemap-index.xml"), "w") as f:
        f.write(xml)
    print("   ✓ sitemap-index.xml")


if __name__ == "__main__":
    run_fixes()
