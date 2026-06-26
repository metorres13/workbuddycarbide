#!/usr/bin/env python3
"""Build the complete tools listing page with all 101 tools organized by 4 categories."""

import os, re

ROOT = os.path.dirname(__file__)
TOOLS_DIR = os.path.join(ROOT, "tools")

# ── Category mapping ──
CATEGORIES = [
    {
        "name": "Cutting Parameters & Performance",
        "icon": "⚡",
        "tools": [
            "speed-feed", "chip-load", "surface-speed", "mrr-calculator",
            "horsepower-calculator", "force-calculator", "cycle-time-calculator",
            "surface-roughness-calculator", "nose-radius-compensation",
            "ramping-angle-calculator", "trochoidal-milling-calculator",
            "slot-milling-calculator", "step-milling-calculator",
            "ball-nose-effective-diameter", "helical-interpolation-calculator",
            "heat-expansion-calculator", "tool-runout-calculator",
            "feed-rate-override-calculator", "peck-drilling-calculator",
            "threading-pass-calculator", "feed-converter"
        ]
    },
    {
        "name": "Drilling, Tapping & Threads",
        "icon": "🔧",
        "tools": [
            "tap-drill-size-calculator", "tapping-feed-rate-calculator",
            "drill-point-length-calculator", "thread-depth-torque-calculator",
            "metric-imperial-thread-converter", "npt-pipe-thread-calculator",
            "percentage-of-thread-calculator", "form-tap-drill-calculator",
            "thread-lead-angle-calculator", "thread-pitch-diameter-calculator",
            "step-drill-design-calculator", "countersink-depth-calculator",
            "reaming-allowance-calculator", "gun-drill-calculator",
            "blind-hole-tapping-calculator"
        ]
    },
    {
        "name": "Materials, Grades & Heat Treat",
        "icon": "🔩",
        "tools": [
            "grade-reference", "carbide-grade-cross-ref-2",
            "metal-weight-calculator", "metal-cost-calculator",
            "hardness-converter", "machinability-rating",
            "stainless-properties", "titanium-machining-guide",
            "aluminum-alloy-table", "tool-steel-heat-treat",
            "cast-iron-machining", "coating-selector",
            "tensile-strength-converter", "plastic-machining",
            "graphite-machining", "brass-machining-parameters",
            "superalloy-tool-life", "die-steel-thermal-conductivity"
        ]
    },
    {
        "name": "Cost, Tolerances & Reference",
        "icon": "📊",
        "tools": [
            "cost-per-part-calculator", "tool-life-economics",
            "cnc-roi-calculator", "batch-cost-calculator",
            "scrap-value-calculator", "iso-fit-calculator",
            "bolt-circle-calculator", "flatness-calculator",
            "sine-bar-calculator", "coord-rotation-calculator",
            "chamfer-calculator", "taper-calculator",
            "gdt-symbols-reference", "keyway-depth-calculator",
            "dovetail-calculator", "gear-parameter-calculator",
            "gcode-reference", "mcode-reference",
            "pressure-converter", "torque-unit-converter",
            "ultimate-unit-converter", "aql-sampling-calculator",
            "pythagorean-calculator", "dia-circ-calculator",
            "tangent-point-calculator", "temp-converter",
            "round-bar-weight",
            "tube-weight-calculator", "wall-thickness-calculator",
            "weight-shipping-calculator",
            "shipping-duty-estimator", "bulk-discount-calculator",
            "production-efficiency-calculator", "inventory-turnover-calculator",
            "engineering-interest-calculator", "tool-change-time-analyzer",
            "tool-wear-cost-calculator", "machine-power-calculator",
            "coolant-concentration", "coolant-lifecycle-cost",
            "micron-inch-converter", "sfm-m-min-converter",
            "polar-rect-converter", "pomodoro-timer",
            "toolbox-organizer", "automation-vs-manual-calculator",
            "arc-r-to-ij-converter"
        ]
    }
]

# ── Friendly names and descriptions ──
TOOL_INFO = {
    "speed-feed": ("Speed & Feed Calculator", "Calculate optimal RPM, IPM, and chip load for carbide end mills across 10 material groups."),
    "chip-load": ("Chip Load Calculator", "Calculate feed per tooth (IPT/fz) and verify chip load against recommended ranges."),
    "surface-speed": ("Surface Speed (SFM)", "Calculate SFM, RPM, or cutting speed for turning and milling operations."),
    "mrr-calculator": ("MRR Calculator", "Calculate material removal rate in cm³/min and in³/min for any machining operation."),
    "horsepower-calculator": ("Horsepower Calculator", "Calculate required spindle power and torque for milling and turning."),
    "force-calculator": ("Milling Force Calculator", "Calculate cutting forces, torque, and resultant loads on the tool."),
    "cycle-time-calculator": ("Cycle Time Calculator", "Estimate turning cycle time for OD, facing, boring, and parting operations."),
    "surface-roughness-calculator": ("Surface Roughness Calculator", "Calculate theoretical Ra and Rz surface finish from feed and nose radius."),
    "nose-radius-compensation": ("Nose Radius Compensation", "Calculate X/Z compensation for CNC lathe G41/G42 tool nose radius."),
    "ramping-angle-calculator": ("Ramping Angle Calculator", "Calculate max ramping angle and Z feed rate for helical milling."),
    "trochoidal-milling-calculator": ("Trochoidal Milling Calculator", "Calculate HSM peel milling parameters for trochoidal toolpaths."),
    "slot-milling-calculator": ("Slot Milling Calculator", "Calculate safe speeds and feeds for full-width slotting and keyway cutting."),
    "step-milling-calculator": ("Step Milling Calculator", "Calculate optimal stepover and depth of cut for multi-pass milling."),
    "ball-nose-effective-diameter": ("Ball Nose Effective Diameter", "Calculate effective cutting diameter of ball nose end mills at depth of cut."),
    "helical-interpolation-calculator": ("Helical Interpolation Calculator", "Calculate helical milling parameters for circular interpolated holes."),
    "heat-expansion-calculator": ("Heat Expansion Calculator", "Calculate thermal expansion of metals for precision machining compensation."),
    "tool-runout-calculator": ("Tool Runout Calculator", "Calculate TIR effects on surface finish, tool life, and hole accuracy."),
    "feed-rate-override-calculator": ("Feed Rate Override Calculator", "Calculate adjusted feed rates when using override on your CNC control."),
    "peck-drilling-calculator": ("Peck Drilling Calculator", "Calculate safe peck depths and retract heights for deep hole drilling."),
    "threading-pass-calculator": ("Threading Pass Calculator", "Calculate number of passes and DOC for CNC threading cycles."),
    "feed-converter": ("Feed Converter", "Convert between feed per rev, feed per tooth, and feed per minute."),

    "tap-drill-size-calculator": ("Tap Drill Size Calculator", "Find the correct tap drill size for metric, UNC, and UNF threads at any engagement."),
    "tapping-feed-rate-calculator": ("Tapping Feed Rate Calculator", "Calculate tapping feed rate (F) from RPM and thread pitch for rigid tapping."),
    "drill-point-length-calculator": ("Drill Point Length Calculator", "Calculate drill point length for 118°, 135°, and custom point angles."),
    "thread-depth-torque-calculator": ("Thread Depth & Torque Calculator", "Calculate minimum thread engagement and torque-to-tension relationships."),
    "metric-imperial-thread-converter": ("Metric/Imperial Thread Converter", "Convert between metric pitch and imperial TPI thread specifications."),
    "npt-pipe-thread-calculator": ("NPT Pipe Thread Calculator", "Calculate NPT thread dimensions including taper, pitch diameter, and length."),
    "percentage-of-thread-calculator": ("Thread Percentage Calculator", "Calculate tap drill size for any thread engagement percentage."),
    "form-tap-drill-calculator": ("Form Tap Drill Calculator", "Calculate drill sizes for thread forming (roll tapping) in various materials."),
    "thread-lead-angle-calculator": ("Thread Lead Angle Calculator", "Calculate lead angle (helix angle) for single and multi-start threads."),
    "thread-pitch-diameter-calculator": ("Thread Pitch Diameter Calculator", "Calculate pitch diameter measurement using the three-wire method."),
    "step-drill-design-calculator": ("Step Drill Design Calculator", "Design step drill geometry including diameters, lengths, and transition angles."),
    "countersink-depth-calculator": ("Countersink Depth Calculator", "Calculate countersink and counterbore depth for standard fasteners."),
    "reaming-allowance-calculator": ("Reaming Allowance Calculator", "Calculate pre-reaming drill size and reaming stock allowance by material."),
    "gun-drill-calculator": ("Gun Drill Calculator", "Calculate gun drilling parameters: speeds, feeds, and coolant pressure."),
    "blind-hole-tapping-calculator": ("Blind Hole Tapping Calculator", "Calculate tap drill depth and min full thread for blind hole tapping."),

    "grade-reference": ("Carbide Grade Cross Reference", "Compare insert grades across Sandvik, Kennametal, Iscar, and more."),
    "carbide-grade-cross-ref-2": ("Carbide Grade Selector", "Cross-reference ISO P/M/K/S/H carbide grades by application and material."),
    "metal-weight-calculator": ("Metal Weight Calculator", "Calculate weight of carbide, steel, aluminum, and brass round stock."),
    "metal-cost-calculator": ("Metal Cost Calculator", "Calculate material cost per part including scrap recovery and nesting efficiency."),
    "hardness-converter": ("Hardness Converter", "Convert between HRC, HRB, HB, HV, and tensile strength for all metals."),
    "machinability-rating": ("Machinability Rating", "Compare machinability ratings of AISI steels and adjust speeds accordingly."),
    "stainless-properties": ("Stainless Steel Properties", "Compare 304 vs 316 stainless steel for machining and corrosion resistance."),
    "titanium-machining-guide": ("Titanium Machining Guide", "Complete speeds, feeds, and tooling guide for Ti-6Al-4V and other titanium alloys."),
    "aluminum-alloy-table": ("Aluminum Alloy Table", "Compare 6061 vs 7075 aluminum for machinability, strength, and applications."),
    "tool-steel-heat-treat": ("Tool Steel Heat Treat", "Calculate dimensional change and optimal heattreating specs for A2, D2, O1, S7."),
    "cast-iron-machining": ("Cast Iron Machining", "Speeds and feeds for gray iron, ductile iron, and compacted graphite iron."),
    "coating-selector": ("Coating Selector", "Match carbide coating (TiN, TiAlN, AlTiN, DLC, CVD) to your application."),
    "tensile-strength-converter": ("Tensile Strength Converter", "Convert between PSI, MPa, and tensile strength from hardness values."),
    "plastic-machining": ("Plastic Machining Guide", "Machining parameters for Delrin, Nylon, PTFE, Acrylic, and other engineering plastics."),
    "graphite-machining": ("Graphite Machining Calculator", "Speeds, feeds, and tooling for EDM graphite electrode machining."),
    "brass-machining-parameters": ("Brass Machining Parameters", "Optimal speeds and feeds for free-machining brass and copper alloys."),
    "superalloy-tool-life": ("Superalloy Tool Life", "Estimate tool life when machining Inconel, Hastelloy, Waspaloy, and Rene 41."),
    "die-steel-thermal-conductivity": ("Die Steel Thermal Conductivity", "Thermal conductivity data for H13, P20, D2, and S7 die and mold steels."),

    "cost-per-part-calculator": ("Cost Per Part Calculator", "Calculate total manufacturing cost per part including material, labor, and overhead."),
    "tool-life-economics": ("Tool Life Economics", "Calculate optimal tool change frequency balancing tool cost and productivity."),
    "cnc-roi-calculator": ("CNC ROI Calculator", "Calculate return on investment for CNC machine purchases and automation projects."),
    "batch-cost-calculator": ("Batch Cost Calculator", "Calculate total batch manufacturing cost with setup amortization and quantity discounts."),
    "scrap-value-calculator": ("Scrap Value Calculator", "Calculate scrap metal recovery value for steel, aluminum, brass, and carbide."),
    "iso-fit-calculator": ("ISO Fit Calculator", "Calculate shaft and hole tolerances for ISO fit classes H7/g6, H7/h6, and more."),
    "bolt-circle-calculator": ("Bolt Circle Calculator", "Calculate XY coordinates for bolt circles with N holes at any radius."),
    "flatness-calculator": ("Flatness Calculator", "Calculate flatness tolerance based on part size and GD&T requirements."),
    "sine-bar-calculator": ("Sine Bar Calculator", "Calculate gage block stack height for sine bar angle setup."),
    "coord-rotation-calculator": ("Coordinate Rotation Calculator", "Rotate XY coordinates by any angle around any origin point."),
    "chamfer-calculator": ("Chamfer Calculator", "Calculate chamfer width, depth, and angle from any two known values."),
    "taper-calculator": ("Taper Calculator", "Calculate taper per inch, taper per foot, and included angle for tapered surfaces."),
    "gdt-symbols-reference": ("GD&T Symbols Reference", "Complete reference guide for GD&T symbols, datums, and feature control frames."),
    "keyway-depth-calculator": ("Keyway Depth Calculator", "Calculate keyway and keyseat depth for standard inch and metric keys."),
    "dovetail-calculator": ("Dovetail Calculator", "Calculate dovetail dimensions, cutter width, and measurement over pins."),
    "gear-parameter-calculator": ("Gear Parameter Calculator", "Calculate spur gear module, pitch diameter, and tooth dimensions."),
    "gcode-reference": ("G-Code Reference", "Quick reference for common G-code commands and cycles for CNC mills and lathes."),
    "mcode-reference": ("M-Code Reference", "Quick reference for M-code auxiliary commands for CNC machine control."),
    "pressure-converter": ("Pressure Converter", "Convert between PSI, bar, MPa, kPa, and kg/cm² pressure units."),
    "torque-unit-converter": ("Torque Unit Converter", "Convert between N·m, ft·lb, in·lb, and kg·m torque units."),
    "ultimate-unit-converter": ("Ultimate Unit Converter", "Multi-category unit converter covering length, weight, volume, and temperature."),
    "aql-sampling-calculator": ("AQL Sampling Calculator", "Calculate AQL sampling plans per ANSI/ASQ Z1.4 standard for lot inspection."),
    "pythagorean-calculator": ("Pythagorean Calculator", "Calculate right triangle sides, angles, area, and hypotenuse for setup."),
    "dia-circ-calculator": ("Diameter & Circumference", "Calculate diameter, circumference, radius, and area of circles."),
    "tangent-point-calculator": ("Tangent Point Calculator", "Calculate tangent points on circles for toolpath geometry."),
    "temp-converter": ("Temperature Converter", "Convert between Celsius, Fahrenheit, and Kelvin for machining coolant temps."),
    "round-bar-weight": ("Round Bar Weight Calculator", "Calculate weight of round steel, aluminum, and brass bars per foot and meter."),
    "tube-weight-calculator": ("Tube Weight Calculator", "Calculate hollow bar and pipe weight for schedule 40/80 pipe sizes."),
    "wall-thickness-calculator": ("Wall Thickness Calculator", "Calculate minimum wall thickness for tubular parts under machining loads."),
    "weight-shipping-calculator": ("Weight & Shipping Calculator", "Calculate total shipping weight for tooling orders and crating estimates."),
    "shipping-duty-estimator": ("Shipping Duty Estimator", "Estimate import duties and taxes for international carbide tooling shipments."),
    "bulk-discount-calculator": ("Bulk Discount Calculator", "Calculate tiered pricing discounts for volume tool purchases."),
    "production-efficiency-calculator": ("Production Efficiency Calculator", "Calculate OEE, utilization, and throughput for manufacturing cells."),
    "inventory-turnover-calculator": ("Inventory Turnover Calculator", "Calculate inventory turnover ratio and days of inventory for tool crib."),
    "engineering-interest-calculator": ("Engineering Interest Calculator", "Calculate compound interest for capital equipment investment analysis."),
    "tool-change-time-analyzer": ("Tool Change Time Analyzer", "Analyze tool change time impact on overall cycle time and productivity."),
    "tool-wear-cost-calculator": ("Tool Wear Cost Calculator", "Calculate per-edge tooling cost including regrind and coating expenses."),
    "machine-power-calculator": ("Machine Power Calculator", "Calculate machine spindle power requirements based on cutting parameters."),
    "coolant-concentration": ("Coolant Concentration Calculator", "Calculate coolant mix ratio using refractometer Brix readings."),
    "coolant-lifecycle-cost": ("Coolant Lifecycle Cost Calculator", "Calculate total annual coolant cost including concentrate, disposal, and labor."),
    "micron-inch-converter": ("Micron to Inch Converter", "Convert between microns, inches, and millimeters for surface finish specs."),
    "sfm-m-min-converter": ("SFM to m/min Converter", "Convert surface speed between SFM and meters per minute for global standards."),
    "polar-rect-converter": ("Polar to Rectangular Converter", "Convert between polar and rectangular coordinates for CNC programming."),
    "pomodoro-timer": ("Pomodoro Timer", "25-minute productivity timer for focused machining programming sessions."),
    "toolbox-organizer": ("Toolbox Organizer", "Organize and categorize your cutting tool inventory by operation and material."),
    "automation-vs-manual-calculator": ("Automation vs Manual Calculator", "Compare automated vs manual machining costs for build vs buy decisions."),
    "arc-r-to-ij-converter": ("Arc R to IJ Converter", "Convert between R- and IJK-format circular interpolation for G-code."),
    "chip-load": ("Chip Load Calculator", "Calculate feed per tooth (IPT/fz) and verify chip load against recommended ranges."),
}


def build_page():
    """Generate the complete HTML page"""
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>All 101 Free CNC Machining Tools — Carbide Tooling</title>
<meta name="description" content="101 free CNC machining calculators and reference tools across 4 categories: cutting parameters, drilling & threading, materials reference, and cost analysis."/>
<link rel="canonical" href="https://carbide-tooling.com/tools/"/>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,400;14..32,500;14..32,600;14..32,700;14..32,800;14..32,900&display=swap" rel="stylesheet"/>
<link rel="stylesheet" href="/css/tool-style.css"/>
<meta name="theme-color" content="#0066cc"/>
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%230066cc'/%3E%3Ctext x='16' y='22' text-anchor='middle' font-size='18' font-weight='800' fill='%23fff'%3E◆%3C/text%3E%3C/svg%3E"/>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter',-apple-system,sans-serif;background:#fff;color:#1d1d1f;line-height:1.6}
nav{position:sticky;top:0;z-index:100;background:rgba(255,255,255,.96);backdrop-filter:saturate(180%) blur(24px);border-bottom:1px solid rgba(0,0,0,.06);height:44px}
.nav-inner{display:flex;align-items:center;justify-content:space-between;height:44px;max-width:1060px;margin:0 auto;padding:0 24px;font-size:12px}
.nav-left{display:flex;align-items:center;gap:32px}
.logo{font-size:14px;font-weight:700;text-decoration:none;color:#1d1d1f;display:flex;align-items:center;gap:6px}
.logo span{font-weight:800;color:#0066cc}
.nav-links>a{color:#1d1d1f;text-decoration:none;padding:0 18px;transition:color .2s;height:44px;display:flex;align-items:center;font-weight:500;font-size:12px}
.nav-links>a:hover{color:#0066cc}
.hero{text-align:center;padding:48px 0 32px}
.hero .badge{display:inline-flex;background:#f5f5f7;padding:4px 14px;border-radius:20px;font-size:11px;font-weight:600;color:#86868b;margin-bottom:12px}
.hero h1{font-size:32px;font-weight:800;letter-spacing:-.6px;margin-bottom:6px}
.hero h1 .accent{color:#0066cc}
.hero p{font-size:14px;color:#86868b;max-width:500px;margin:0 auto;line-height:1.7}
.container{max-width:960px;margin:0 auto;padding:0 20px}
.category{margin-bottom:40px}
.category h2{font-size:20px;font-weight:700;margin-bottom:4px;display:flex;align-items:center;gap:8px}
.category .cat-count{font-size:12px;color:#86868b;font-weight:400;margin-bottom:14px}
.tool-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.tool-card{display:flex;align-items:center;gap:10px;padding:10px 14px;background:#f5f5f7;border-radius:12px;text-decoration:none;color:#1d1d1f;transition:all .15s;min-height:48px}
.tool-card:hover{background:#e8f0fe;transform:translateY(-1px)}
.tool-card .tc-icon{font-size:16px;flex-shrink:0;width:28px;text-align:center}
.tool-card .tc-name{font-size:12px;font-weight:500;line-height:1.3}
.tool-card .tc-desc{font-size:10px;color:#86868b;line-height:1.3;margin-top:1px}
footer{background:#f5f5f7;border-top:1px solid #e8e8ed;padding:32px 0;text-align:center;font-size:12px;color:#86868b}
footer a{color:#0066cc;text-decoration:none}
@media(max-width:768px){
  .hero h1{font-size:24px}
  .tool-grid{grid-template-columns:1fr 1fr}
  .tool-card{padding:8px 12px}
}
@media(max-width:480px){
  .tool-grid{grid-template-columns:1fr}
}
</style>
</head>
<body>
<nav>
<div class="nav-inner">
  <div class="nav-left">
    <a href="https://carbide-tooling.com/" class="logo"><span>◆</span> Carbide Tooling</a>
    <div class="nav-links">
      <a href="https://carbide-tooling.com/products/">Products</a>
      <a href="https://carbide-tooling.com/guides/">Guides</a>
      <a href="https://carbide-tooling.com/about.html">About</a>
    </div>
  </div>
  <a href="https://carbide-tooling.com/quote.html" style="display:inline-flex;background:#0066cc;color:#fff;padding:6px 16px;border-radius:20px;font-size:11px;font-weight:600;text-decoration:none">📩 Get a Quote</a>
</div>
</nav>

<section class="hero">
  <div class="badge">🧰 101 Tools</div>
  <h1>CNC Machining <span class="accent">Toolset</span></h1>
  <p>Professional calculators for speeds & feeds, drilling & threading, materials reference, and cost analysis.</p>
</section>

<div class="container">
'''
    
    total = 0
    for cat in CATEGORIES:
        html += f'''<div class="category">
  <h2>{cat["icon"]} {cat["name"]}</h2>
  <div class="cat-count">{len(cat["tools"])} tools</div>
  <div class="tool-grid">
'''
        for tool_dir in cat["tools"]:
            info = TOOL_INFO.get(tool_dir)
            if info:
                name, desc = info
            else:
                name = tool_dir.replace("-", " ").title()
                desc = "Free CNC machining calculator tool."
            
            # Pick an icon
            icons = ["⚙️", "📐", "🔄", "🔧", "🔩", "📊", "🔬", "⏱️", "💪", "🔌", "⚡", "🌀", "🔧"]
            icon = icons[abs(hash(tool_dir)) % len(icons)]
            
            html += f'    <a href="/tools/{tool_dir}/" class="tool-card"><span class="tc-icon">{icon}</span><div><div class="tc-name">{name}</div><div class="tc-desc">{desc}</div></div></a>\n'
            total += 1
        
        html += '  </div>\n</div>\n'
    
    html += f'''
</div>

<footer>
  <p style="margin-bottom:4px"><a href="https://carbide-tooling.com/">CarbideTooling.com</a></p>
  <p style="font-size:11px">Copyright &copy; 2026 Carbide Tooling &mdash; {total} free engineering tools</p>
</footer>
</body>
</html>'''
    
    fpath = os.path.join(ROOT, "tools", "index.html")
    with open(fpath, "w") as f:
        f.write(html)
    print(f"✅ Generated tools listing with {total} tools")


if __name__ == "__main__":
    build_page()
