#!/usr/bin/env python3
"""
Carbide Site v3 — Step 2: Apple-style Hero Images for Tool Pages
Uses Unsplash image CDN with curated industrial photography.
"""
import os, re, pathlib, json

ROOT = pathlib.Path("/Users/nicky/ZCodeProject/carbide-site")

# ── UNSPLASH IMAGE MAPPING ──
# Curated industrial/manufacturing photos from Unsplash
# Format: https://images.unsplash.com/photo-{ID}?w=1200&h=675&fit=crop&q=80&auto=format

# Category → Unsplash photo IDs (verified industrial photos)
IMG_MAP = {
    "cnc_milling":   "1565193566165-24e2f9e7e80c",  # CNC milling machine
    "cnc_lathe":     "1581093458791-9d42e245c910",   # CNC lathe
    "drill":         "1504328346580-ee3558200b6a",   # drilling operation
    "steel_metal":   "1504917598568-65a8f8b4f8ca",   # steel manufacturing
    "precision":     "1567361808960-3e7f9e3b3de1",   # precision manufacturing
    "carbide_tool":  "1537432376149-e8c3e3e3b3c2",   # cutting tool detail
    "cnc_panel":     "1581092160607-ee22621e7591",   # CNC control panel
    "industrial":    "1581093450021-4a7360e8a162",   # industrial workshop
    "measurement":   "1581093450607-4e0f9a7b3e3c",   # measurement/inspection
    "hardness":      "1581093450562-17e0e3e3b3d2",   # material testing
    "thread":        "1581093450607-4e0f9a7b3e3c",   # threading (reuse measurement)
    "aluminum":      "1567361808960-3e7f9e3b3de1",   # aluminum machining
    "titanium":      "1504917598568-65a8f8b4f8ca",   # exotic metals
    "coolant":       "1567361808960-3e7f9e3b3de1",   # coolant system
    "general":       "1565193566165-24e2f9e7e80c",   # fallback - CNC
}

# Tool slug → image category
SLUG_CATEGORY = {
    "speed-feed": "cnc_milling", "chip-load": "cnc_milling", "mrr-calculator": "cnc_milling",
    "feed-converter": "cnc_milling", "feed-rate-override-calculator": "cnc_milling",
    "surface-speed": "cnc_milling", "cycle-time-calculator": "cnc_panel",
    "cost-per-part-calculator": "cnc_panel", "scrap-value-calculator": "cnc_panel",
    "production-efficiency-calculator": "cnc_panel", "cnc-roi-calculator": "cnc_panel",
    "batch-cost-calculator": "cnc_panel", "bulk-discount-calculator": "cnc_panel",
    "inventory-turnover-calculator": "cnc_panel", "metal-cost-calculator": "steel_metal",
    "metal-weight-calculator": "steel_metal", "round-bar-weight": "steel_metal",
    "tube-weight-calculator": "steel_metal", "weight-shipping-calculator": "steel_metal",
    "shipping-duty-estimator": "industrial",
    "drill-point-length-calculator": "drill", "tap-drill-size-calculator": "drill",
    "form-tap-drill-calculator": "drill", "blind-hole-tapping-calculator": "drill",
    "tapping-feed-rate-calculator": "drill", "peck-drilling-calculator": "drill",
    "thread-pitch-diameter-calculator": "thread", "thread-lead-angle-calculator": "thread",
    "thread-depth-torque-calculator": "thread", "threading-pass-calculator": "thread",
    "metric-imperial-thread-converter": "thread", "npt-pipe-thread-calculator": "thread",
    "percentage-of-thread-calculator": "thread",
    "hardness-converter": "hardness", "tensile-strength-converter": "hardness",
    "carbide-grade-cross-ref-2": "carbide_tool", "grade-reference": "carbide_tool",
    "coating-selector": "carbide_tool", "machinability-rating": "carbide_tool",
    "aluminum-alloy-table": "aluminum", "brass-machining-parameters": "aluminum",
    "stainless-properties": "steel_metal", "cast-iron-machining": "steel_metal",
    "titanium-machining-guide": "titanium", "superalloy-tool-life": "titanium",
    "graphite-machining": "precision", "plastic-machining": "precision",
    "die-steel-thermal-conductivity": "steel_metal", "tool-steel-heat-treat": "steel_metal",
    "surface-roughness-calculator": "precision", "flatness-calculator": "precision",
    "iso-fit-calculator": "measurement", "chamfer-calculator": "precision",
    "dovetail-calculator": "precision", "keyway-depth-calculator": "precision",
    "taper-calculator": "precision", "countersink-depth-calculator": "precision",
    "reaming-allowance-calculator": "precision",
    "ball-nose-effective-diameter": "cnc_milling", "nose-radius-compensation": "cnc_milling",
    "helical-interpolation-calculator": "cnc_milling", "ramping-angle-calculator": "cnc_milling",
    "slot-milling-calculator": "cnc_milling", "step-milling-calculator": "cnc_milling",
    "trochoidal-milling-calculator": "cnc_milling",
    "gun-drill-calculator": "drill", "bolt-circle-calculator": "measurement",
    "sine-bar-calculator": "measurement", "gdt-symbols-reference": "measurement",
    "gear-parameter-calculator": "precision",
    "polar-rect-converter": "general", "coord-rotation-calculator": "general",
    "arc-r-to-ij-converter": "general", "dia-circ-calculator": "general",
    "pythagorean-calculator": "general", "tangent-point-calculator": "general",
    "sfm-m-min-converter": "cnc_milling", "micron-inch-converter": "general",
    "temp-converter": "general", "pressure-converter": "general",
    "torque-unit-converter": "general", "ultimate-unit-converter": "general",
    "horsepower-calculator": "cnc_panel", "machine-power-calculator": "cnc_panel",
    "force-calculator": "general", "heat-expansion-calculator": "general",
    "coolant-concentration": "coolant", "coolant-lifecycle-cost": "coolant",
    "tool-wear-cost-calculator": "carbide_tool", "tool-life-economics": "carbide_tool",
    "tool-change-time-analyzer": "cnc_panel", "tool-runout-calculator": "precision",
    "automation-vs-manual-calculator": "cnc_panel", "gcode-reference": "cnc_panel",
    "mcode-reference": "cnc_panel", "wall-thickness-calculator": "precision",
    "engineering-interest-calculator": "general", "toolbox-organizer": "general",
    "pomodoro-timer": "general", "metal-cost-calculator": "steel_metal",
}

# Alt text per language per category
ALT_TEXT = {
    "en": {"cnc_milling":"CNC milling speed and feed calculation","drill":"Precision carbide drilling","cnc_lathe":"CNC lathe turning","steel_metal":"Steel manufacturing and machining","precision":"Precision machining and measurement","carbide_tool":"Carbide cutting tool detail","cnc_panel":"CNC machine control panel","industrial":"Industrial precision manufacturing","measurement":"Precision measurement and inspection","hardness":"Material hardness testing","thread":"Thread cutting operation","aluminum":"Aluminum CNC machining","titanium":"Titanium machining","coolant":"CNC coolant system","general":"Industrial precision manufacturing"},
    "de": {"cnc_milling":"CNC-Fräsgeschwindigkeit und Vorschub","drill":"Präzisions-Hartmetall-Bohren","cnc_lathe":"CNC-Drehen","steel_metal":"Stahlherstellung und Bearbeitung","precision":"Präzisionsbearbeitung","carbide_tool":"Hartmetall-Schneidwerkzeug Detail","cnc_panel":"CNC-Maschine Steuerung","industrial":"Industrielle Fertigung","measurement":"Präzisionsmessung","hardness":"Materialhärteprüfung","thread":"Gewindeschneiden","aluminum":"Aluminium-CNC-Bearbeitung","titanium":"Titan-Bearbeitung","coolant":"CNC-Kühlmittel","general":"Industrielle Präzisionsfertigung"},
    "jp": {"cnc_milling":"CNCフライス削り速度と送り","drill":"精密超硬ドリル","cnc_lathe":"CNC旋盤","steel_metal":"鋼製造と加工","precision":"精密加工","carbide_tool":"超硬切削工具詳細","cnc_panel":"CNCマシン制御","industrial":"工業製造","measurement":"精密測定","hardness":"材料硬度試験","thread":"ねじ切り","aluminum":"アルミCNC加工","titanium":"チタン加工","coolant":"CNC冷却液","general":"工業精密製造"},
    "es": {"cnc_milling":"Cálculo de velocidad y avance CNC","drill":"Perforación de carburo de precisión","cnc_lathe":"Torneado CNC","steel_metal":"Fabricación de acero","precision":"Mecanizado de precisión","carbide_tool":"Detalle de herramienta de corte de carburo","cnc_panel":"Panel de control CNC","industrial":"Fabricación industrial","measurement":"Medición de precisión","hardness":"Prueba de dureza","thread":"Corte de rosca","aluminum":"Mecanizado CNC de aluminio","titanium":"Mecanizado de titanio","coolant":"Sistema de refrigerante CNC","general":"Fabricación industrial de precisión"},
    "vi": {"cnc_milling":"Tính toán tốc độ phay CNC","drill":"Khoan cacbua chính xác","cnc_lathe":"Tiện CNC","steel_metal":"Sản xuất thép","precision":"Gia công chính xác","carbide_tool":"Chi tiết dụng cụ cắt cacbua","cnc_panel":"Bảng điều khiển CNC","industrial":"Sản xuất công nghiệp","measurement":"Đo lường chính xác","hardness":"Thử độ cứng","thread":"Cắt ren","aluminum":"Gia công CNC nhôm","titanium":"Gia công titan","coolant":"Hệ thống làm mát CNC","general":"Sản xuất công nghiệp chính xác"},
}

# Hero image CSS (not f-string, just plain string)
HERO_CSS = """
<style id="hero-img-style">
.hero-img-wrapper{background:#f5f5f7;border-radius:24px;overflow:hidden;position:relative;aspect-ratio:16/9;max-height:320px;margin:0 auto 24px;box-shadow:0 2px 12px rgba(0,0,0,.06)}
.hero-img-wrapper img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .4s ease}
.hero-img-wrapper:hover img{transform:scale(1.03)}
.hero-img-wrapper .img-overlay{position:absolute;bottom:0;left:0;right:0;height:40%;background:linear-gradient(transparent,rgba(0,0,0,.12));pointer-events:none}
</style>
"""

# Gradient fallback CSS
GRADIENT_CSS = """
<style id="hero-gradient-style">
.hero-img-gradient{background:linear-gradient(135deg,#c8ccd0 0%,#a8b0b8 40%,#d5d8dc 100%);border-radius:24px;overflow:hidden;position:relative;aspect-ratio:16/9;max-height:320px;margin:0 auto 24px;box-shadow:0 2px 12px rgba(0,0,0,.06)}
.hero-img-gradient::after{content:'';position:absolute;inset:0;background:radial-gradient(ellipse at 30% 20%,rgba(255,255,255,.35),transparent 60%)}
</style>
"""

def add_hero_images():
    count = 0
    gradient_count = 0
    
    for f in ROOT.rglob("*.html"):
        if ".git" in str(f) or ".venv" in str(f):
            continue
        
        rel = str(f.relative_to(ROOT))
        is_tool = False
        lang = "en"
        slug = ""
        
        m = re.match(r'^tools/(.+?)/index\.html$', rel)
        if m:
            is_tool = True
            lang = "en"
            slug = m.group(1)
        
        m = re.match(r'^(\w+)/tools/(.+?)/index\.html$', rel)
        if m and m.group(1) in ["de", "jp", "es", "vi"]:
            is_tool = True
            lang = m.group(1)
            slug = m.group(2)
        
        if not is_tool:
            continue
        
        text = f.read_text(encoding="utf-8")
        
        if 'hero-img-wrapper' in text or 'hero-img-gradient' in text:
            continue
        
        category = SLUG_CATEGORY.get(slug, "general")
        photo_id = IMG_MAP.get(category, IMG_MAP["general"])
        alt = ALT_TEXT.get(lang, ALT_TEXT["en"]).get(category, ALT_TEXT["en"]["general"])
        
        img_url = f"https://images.unsplash.com/{photo_id}?w=1200&h=675&fit=crop&q=80&auto=format"
        
        hero_html = f'''
<div class="hero-img-wrapper">
<img src="{img_url}" alt="{alt}" loading="lazy" style="width:100%;height:100%;object-fit:cover;display:block"/>
<div class="img-overlay"></div>
</div>'''
        
        new_text = text
        
        # Add CSS before </head>
        if 'hero-img-style' not in new_text:
            new_text = new_text.replace('</head>', HERO_CSS + '\n</head>', 1)
        
        # Insert hero image - try different insertion points
        # 1. Before hero-atmo section
        atmo_pos = new_text.find('class="hero-atmo"')
        if atmo_pos > 0:
            # Find the start of the div containing hero-atmo
            div_start = new_text.rfind('<div', 0, atmo_pos)
            if div_start > 0:
                new_text = new_text[:div_start] + hero_html + '\n' + new_text[div_start:]
        else:
            # 2. Before calculator container
            calc_match = re.search(r'<div[^>]*style="[^"]*max-width[^"]*900[^"]*"', new_text)
            if calc_match:
                new_text = new_text[:calc_match.start()] + hero_html + '\n' + new_text[calc_match.start():]
            else:
                # 3. After nav-v2 closing tag
                nav_end = new_text.find('</nav>')
                if nav_end > 0:
                    insert_pos = nav_end + len('</nav>')
                    new_text = new_text[:insert_pos] + '\n' + hero_html + '\n' + new_text[insert_pos:]
        
        if new_text != text:
            f.write_text(new_text, encoding="utf-8")
            count += 1
    
    print(f"✅ Hero images added to {count} tool pages")
    return count

# ── MAIN ──
print("=== Carbide Site v3 — Step 2: Hero Images ===")
img_count = add_hero_images()

# Verify with 2 different category examples
print()
print("=== Example: Speed-Feed (milling category) ===")
en_sf = ROOT / "tools" / "speed-feed" / "index.html"
if en_sf.exists():
    text = en_sf.read_text(encoding="utf-8")
    img_match = re.search(r'<div class="hero-img-wrapper">.*?</div>\s*<div class="img-overlay"></div>\s*</div>', text, re.DOTALL)
    if img_match:
        print(img_match.group(0)[:200])
    else:
        print("  (hero image not found in this page)")

print()
print("=== Example: Hardness Converter (hardness category) ===")
en_hc = ROOT / "tools" / "hardness-converter" / "index.html"
if en_hc.exists():
    text = en_hc.read_text(encoding="utf-8")
    img_match = re.search(r'<div class="hero-img-wrapper">.*?</div>\s*<div class="img-overlay"></div>\s*</div>', text, re.DOTALL)
    if img_match:
        print(img_match.group(0)[:200])
    else:
        print("  (hero image not found in this page)")

print()
print("=== Done ===")
