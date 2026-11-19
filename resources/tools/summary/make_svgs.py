#!/usr/bin/env python3
"""Draw the own diagrams for the chapter summaries as SVG files in svg/.

Units are millimetres: each SVG has width = viewBox width in mm, so a font-size of 3.0
prints at 8.5 pt. Greek letters use the embedded KaTeX_Math italic font (class "m").
Geometry is computed so the physics is right (Snell's law angles, crest spacing).

Usage: python3 make_svgs.py   (writes svg/*.svg)
"""
import math, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "svg")
FS = 3.0          # 8.5 pt
SW = 0.32         # line width (mm)
STYLE = (f'<style>text{{font-family:Inter,sans-serif;font-size:{FS}px;fill:#000}}'
         f'.m{{font-family:KaTeX_Math,serif;font-style:italic}}'
         f'.r{{font-family:KaTeX_Main,serif;font-style:normal}}'
         f'.l{{stroke:#000;stroke-width:{SW};fill:none}}'
         f'.d{{stroke:#000;stroke-width:0.25;fill:none;stroke-dasharray:1 0.8}}'
         f'.g{{stroke:#777;stroke-width:0.25;fill:none}}</style>')


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}mm" height="{h}mm">'
            + STYLE + body + '</svg>')


def arrowhead(x, y, ang, size=1.6):
    """Filled arrowhead with its tip at (x, y), pointing along ang (radians, y down)."""
    a1, a2 = ang + math.radians(155), ang - math.radians(155)
    return (f'<path d="M{x:.2f} {y:.2f} L{x + size*math.cos(a1):.2f} {y + size*math.sin(a1):.2f} '
            f'L{x + size*math.cos(a2):.2f} {y + size*math.sin(a2):.2f}z" fill="#000"/>')


def line(x1, y1, x2, y2, cls="l", extra=""):
    return f'<path class="{cls}" d="M{x1:.2f} {y1:.2f} L{x2:.2f} {y2:.2f}" {extra}/>'


def ray(x1, y1, x2, y2, at=0.55, cls="l"):
    """Line with an arrowhead part way along (fraction at)."""
    ang = math.atan2(y2 - y1, x2 - x1)
    xm, ym = x1 + at*(x2 - x1), y1 + at*(y2 - y1)
    return line(x1, y1, x2, y2, cls) + arrowhead(xm, ym, ang)


def dbl(x1, y1, x2, y2):
    """Double-headed dimension arrow."""
    ang = math.atan2(y2 - y1, x2 - x1)
    return line(x1, y1, x2, y2, extra='style="stroke-width:0.25"') + arrowhead(x2, y2, ang, 1.3) + arrowhead(x1, y1, ang + math.pi, 1.3)


def text(x, y, s, anchor="start", extra=""):
    return f'<text x="{x:.2f}" y="{y:.2f}" text-anchor="{anchor}" {extra}>{s}</text>'


def arc(cx, cy, r, a1, a2):
    """Arc from angle a1 to a2 (degrees, measured clockwise from 'up' = -y)."""
    def pt(a):
        t = math.radians(a)
        return cx + r*math.sin(t), cy - r*math.cos(t)
    (x1, y1), (x2, y2) = pt(a1), pt(a2)
    large = 1 if abs(a2 - a1) > 180 else 0
    sweep = 1 if a2 > a1 else 0
    return f'<path class="l" style="stroke-width:0.22" d="M{x1:.2f} {y1:.2f} A{r} {r} 0 {large} {sweep} {x2:.2f} {y2:.2f}"/>'


# ---------------------------------------------------------------- 1A transverse wave
def wave(W=88, H=21, lam=22.0, A=5.5):
    y0, x0 = 11.5, 1.0
    n = 400
    pts = [f"{x0 + i*(2.5*lam)/n:.2f} {y0 - A*math.sin(2*math.pi*(i*(2.5*lam)/n)/lam):.2f}" for i in range(n + 1)]
    xe = x0 + 2.5*lam
    b = line(0, y0, xe + 1.0, y0, "d")
    b += f'<path class="l" d="M{" L".join(pts)}"/>'
    c1, c2, c3 = x0 + lam/4, x0 + 5*lam/4, x0 + 9*lam/4   # crests
    t1, t2 = x0 + 3*lam/4, x0 + 7*lam/4                    # troughs
    b += text(c1, y0 - A - 1.0, "crest", "middle")
    b += dbl(c2, y0 - A - 1.4, c3, y0 - A - 1.4) + text((c2 + c3)/2, y0 - A - 2.3, "λ", "middle", 'class="m"')
    b += dbl(t1, y0, t1, y0 + A) + text(t1 + 0.6, y0 + A/2 + 1.0, "A", "start", 'class="m"')
    b += text(t2, y0 + A + 3.6, "trough", "middle")
    b += text(xe + 2.0, y0 + 1.0, "neutral position")
    b += ray(xe + 2.0, 3.0, W - 1.0, 3.0, at=1.0) + text(xe + 2.0, 6.9, "direction of travel")
    return svg(W, H, b)


# ---------------------------------------------------------------- 1C refraction with crests
def snell():
    W, H = 40, 40
    n2, th1 = 1.50, math.radians(50)
    th2 = math.asin(math.sin(th1)/n2)
    bx, by = 19.0, 19.5                       # point where the ray meets the boundary
    b = f'<rect x="0" y="{by}" width="{W}" height="{H-by}" fill="#e6e6e6"/>'
    b += line(0, by, W, by)
    b += line(bx, 1.0, bx, H - 1.0, "d")
    # incident ray from upper left, refracted ray to lower right
    L1, L2 = 22.0, 21.0
    ix, iy = bx - L1*math.sin(th1), by - L1*math.cos(th1)
    ox, oy = bx + L2*math.sin(th2), by + L2*math.cos(th2)
    b += ray(ix, iy, bx, by, at=0.3) + ray(bx, by, ox, oy, at=0.97)
    # wave crests: perpendicular to the ray, spacing d1 in air, d1/n in glass, meeting at the boundary
    d1, half = 3.6, 1.9
    d2 = d1/n2
    for k in range(1, 5):                     # crests in air, behind the boundary point
        s = k*d1 - 0.0
        cx, cy = bx - s*math.sin(th1), by - s*math.cos(th1)
        if k == 1:
            pass
        ux, uy = math.cos(th1), -math.sin(th1)  # direction along the crest (perpendicular to ray)
        # clip crest so it stays above the boundary
        e1 = (cx - half*ux, cy - half*uy)
        e2 = (cx + half*ux, cy + half*uy)
        if e2[1] > by:                         # end crossing into glass: cut at the boundary
            t = (by - cy)/uy if uy else half
            e2 = (cx + t*ux, by)
        b += line(*e1, *e2, "g")
    for k in range(6, 10):                    # glass crests start below the angle label
        s = k*d2
        cx, cy = bx + s*math.sin(th2), by + s*math.cos(th2)
        ux, uy = math.cos(th2), -math.sin(th2)
        e1 = (cx - half*ux, cy - half*uy)
        e2 = (cx + half*ux, cy + half*uy)
        if e1[1] < by:
            t = (by - cy)/(-uy)
            e1 = (cx - t*ux, by)
        b += line(*e1, *e2, "g")
    b += arc(bx, by, 5.0, -50, 0) + text(bx - 2.9, by - 8.2, 'θ<tspan dy="0.8" style="font-size:2.4px">1</tspan>', "middle", 'class="m"')
    th2d = math.degrees(th2)
    b += arc(bx, by, 5.0, 180, 180 - th2d) + text(bx + 2.1, by + 8.6, 'θ<tspan dy="0.8" style="font-size:2.4px">2</tspan>', "middle", 'class="m"')
    b += text(bx + 1.2, 3.3, "normal")
    b += text(W - 0.5, by - 4.6, "air", "end") + text(W - 0.5, by - 1.2, "(fast)", "end")
    b += text(W - 0.5, by + 4.0, "glass", "end") + text(W - 0.5, by + 7.4, "(slow)", "end")
    return svg(W, H, b)


# ---------------------------------------------------------------- 1C partial reflection, critical angle, TIR
def tir(W=88, H=25.5):
    n1 = 1.50                                  # glass into air
    thc = math.degrees(math.asin(1/n1))        # 41.8 degrees
    by, Lin = 8.0, 11.0
    b = f'<rect x="0" y="{by}" width="{W}" height="{H-by}" fill="#e6e6e6"/>' + line(0, by, W, by)
    b += text(1.0, 4.5, "air") + text(1.0, by + 3.6, "glass")
    panels = [(21.0, 25.0, ("θ &lt; θc", "refracts out")), (50.0, thc, ("θ = θc", "skims along")), (77.0, 62.0, ("θ &gt; θc", "all reflects"))]
    for px, th, (l1, l2) in panels:
        t = math.radians(th)
        sx, sy = px - Lin*math.sin(t), by + Lin*math.cos(t)
        rx, ry = px + Lin*math.sin(t), by + Lin*math.cos(t)
        b += line(px, by - 6.5, px, by + 10.5, "d")
        b += ray(sx, sy, px, by, at=0.5)
        if th > thc + 0.5:                                  # total internal reflection
            b += ray(px, by, rx, ry, at=0.6)
        else:                                               # weak (partial) reflection, dashed
            b += line(px, by, rx, ry, "d") + arrowhead(px + 0.6*(rx-px), by + 0.6*(ry-by), math.atan2(ry-by, rx-px), 1.3)
        if th < thc - 0.5:                                  # refracted ray, Snell's law
            t2 = math.asin(n1*math.sin(t))
            L2 = 6.5
            b += ray(px, by, px + L2*math.sin(t2), by - L2*math.cos(t2), at=0.8)
        elif abs(th - thc) <= 0.5:                          # refracted ray at 90 degrees: along the surface
            b += ray(px, by - 0.25, px + 11.0, by - 0.25, at=0.85)
        a, s = l1.split(" ", 1)[0], l1.split(" ", 1)[1]
        rel, sym = s.split(" ")
        b += (f'<text x="{px:.2f}" y="{H - 4.4:.2f}" text-anchor="middle"><tspan class="m">θ</tspan> {rel} '
              f'<tspan class="m">θ</tspan><tspan class="m" dy="0.7" style="font-size:2.4px">c</tspan></text>')
        b += text(px, H - 0.8, l2, "middle")
    return svg(W, H, b)


# ---------------------------------------------------------------- 1C optical fibre
def fibre():
    W, H = 88, 15
    top, bot, ct, cb = 1.0, 13.0, 4.0, 10.0
    b = f'<rect x="0" y="{top}" width="58" height="{bot-top}" fill="#e6e6e6" stroke="#000" stroke-width="{SW}"/>'
    b += f'<rect x="0" y="{ct}" width="58" height="{cb-ct}" fill="#fff"/>' + line(0, ct, 58, ct) + line(0, cb, 58, cb)
    xs = [0, 9, 23, 37, 51, 58]
    ys = [7.0, cb, ct, cb, ct, ct + (cb - ct)*0.5]
    for i in range(len(xs) - 1):
        b += ray(xs[i], ys[i], xs[i+1], ys[i+1], at=0.55)
    b += text(60, 3.4, 'cladding: smaller <tspan class="m">n</tspan>')
    b += text(60, 8.0, 'core: bigger <tspan class="m">n</tspan>')
    b += text(60, 12.6, "cladding")
    return svg(W, H, b)


# ---------------------------------------------------------------- 2A heating curve for water (time not to scale)
def heating(W=88, H=28):
    """Steady heating. Slopes follow c: ice (about 2100 J/(kg K)) and steam (about 2000) warm about
    twice as fast as water (4190), so their lines are steeper. Plateaus at 0 and 100 degC,
    boiling longer than melting (L_vap is about 7 times L_fusion); time is not to scale."""
    ox, oy = 9.0, 23.5
    k = 0.15                                   # mm per degC
    Y = lambda tc: oy - (tc + 30) * k
    xs = [0, 2.4, 12.4, 27.4, 63.4, 66.4]      # ice 30 deg in 2.4 mm; water 100 deg in 15 mm; steam 20 deg in 3 mm
    ts = [-30, 0, 0, 100, 100, 120]
    pts = [(ox + x, Y(t)) for x, t in zip(xs, ts)]
    b = ray(ox, oy, ox, 1.0, at=1.0) + ray(ox, oy, W - 1.0, oy, at=1.0)
    b += line(ox, Y(0), pts[2][0], Y(0), "d") + line(ox, Y(100), pts[4][0], Y(100), "d")
    b += f'<path class="l" style="stroke-width:0.45" d="M' + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + '"/>'
    b += text(ox - 1.0, Y(0) + 1.0, "0", "end") + text(ox - 1.0, Y(100) + 1.0, "100", "end")
    b += text(ox + 1.5, 2.6, "temperature (°C)")
    b += text(W - 1.0, oy + 3.6, "time, heating steadily (not to scale)", "end")
    b += text((pts[1][0] + pts[2][0]) / 2, Y(0) - 1.2, "melting", "middle")
    b += text((pts[3][0] + pts[4][0]) / 2, Y(100) - 1.2, "boiling", "middle")
    b += text(pts[1][0] + 0.8, Y(-27), "ice")
    b += text(pts[2][0] + 5.5, Y(50) + 1.0, "water", "end")
    b += text(pts[5][0] + 0.6, Y(120) + 2.6, "steam", "start") if False else text(pts[5][0] + 0.8, Y(108), "steam")
    b += text(pts[3][0] + 4.0, Y(62), 'flat parts: <tspan class="m">Q</tspan> = <tspan class="m">mL</tspan>')
    b += text(pts[3][0] + 4.0, Y(62) + 4.0, 'sloping parts: <tspan class="m">Q</tspan> = <tspan class="m">mc</tspan>Δ<tspan class="m">T</tspan>')
    return svg(W, H, b)


# ---------------------------------------------------------------- 2B Earth's energy budget (simplified, NASA values)
def budget(W=88, H=23):
    gy = 17.0
    b = f'<rect x="0" y="{gy}" width="{W}" height="{H-gy}" fill="#e6e6e6"/>' + line(0, gy, W, gy)
    b += text(W - 1.0, gy + 4.0, "Earth (surface and air)", "end")
    b += f'<circle cx="4.5" cy="4.5" r="3" class="l"/>'
    hx = 24.0                                  # where sunlight arrives
    b += ray(7.0, 6.5, hx, gy, at=0.6) + text(4.0, 13.5, "340 in")
    b += ray(hx, gy, hx + 13.0, 3.0, at=0.7) + text(hx + 11.5, 9.5, "100") + text(hx + 11.5, 12.9, "reflected")
    b += text(hx, gy + 4.0, "240 absorbed", "middle")
    x = 62.0
    path = f"M{x} {gy} q1.8 -2.5 0 -5 q-1.8 -2.5 0 -5 q1.4 -2 0 -4"
    b += f'<path class="l" d="{path}"/>' + arrowhead(x, 2.0, -math.pi/2)
    b += text(x + 3.0, 7.5, "240 out as") + text(x + 3.0, 10.9, "infrared")
    b += text(W - 1.0, 2.6, "W/m²", "end")
    return svg(W, H, b)


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, fn in [("wave", wave), ("snell", snell), ("tir", tir), ("fibre", fibre),
                     ("heating", heating), ("budget", budget)]:
        open(os.path.join(OUT, name + ".svg"), "w").write(fn())
        print("wrote svg/" + name + ".svg")


if __name__ == "__main__":
    main()
