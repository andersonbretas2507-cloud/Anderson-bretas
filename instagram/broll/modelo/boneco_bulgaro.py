"""Quadro de teste: boneco anatômico feminino no búlgaro, glúteo em vermelho.

Gera boneco-bulgaro-teste.svg e .png (1080x1920) nesta pasta.
"""
import math
import pathlib
import subprocess

W, H = 1080, 1920
OUT = pathlib.Path(__file__).parent


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def norm(v):
    l = math.hypot(*v)
    return (v[0] / l, v[1] / l)


class Seg:
    """Segmento A->B. 'ant' escolhe qual perpendicular é a face anterior."""

    def __init__(self, a, b, ant):
        self.a, self.b = a, b
        d = norm(sub(b, a))
        self.d = d
        n = (-d[1], d[0])
        self.n = n if (n[0] * ant[0] + n[1] * ant[1]) >= 0 else (-n[0], -n[1])
        self.L = math.hypot(*sub(b, a))

    def pt(self, t, off):
        """t ao longo (0..1, pode extrapolar); off >0 anterior, <0 posterior."""
        x = self.a[0] + self.d[0] * self.L * t + self.n[0] * off
        y = self.a[1] + self.d[1] * self.L * t + self.n[1] * off
        return (x, y)


def interp(stations, t):
    for (t0, f0, b0), (t1, f1, b1) in zip(stations, stations[1:]):
        if t0 <= t <= t1:
            u = (t - t0) / (t1 - t0)
            u = (1 - math.cos(math.pi * u)) / 2
            return f0 + (f1 - f0) * u, b0 + (b1 - b0) * u
    return stations[-1][1], stations[-1][2]


def smooth(points, closed=True):
    """Caminho suave (Catmull-Rom -> Bézier)."""
    p = points
    n = len(p)
    s = f"M{p[0][0]:.1f},{p[0][1]:.1f} "
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = p[(i - 1) % n] if closed or i > 0 else p[i]
        p1 = p[i]
        p2 = p[(i + 1) % n]
        p3 = p[(i + 2) % n] if closed or i + 2 < n else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        s += f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f} "
    return s + ("Z" if closed else "")


def limb(seg, stations, n=24):
    (a, fa, ba), (b, fb, bb) = stations[0], stations[-1]
    cap = 0.06
    stations = ([(a - cap, fa * 0.55, ba * 0.55), (a - cap * 0.5, fa * 0.88, ba * 0.88)] + stations
                + [(b + cap * 0.5, fb * 0.88, bb * 0.88), (b + cap, fb * 0.55, bb * 0.55)])
    t0, t1 = stations[0][0], stations[-1][0]
    ts = [t0 + (t1 - t0) * i / n for i in range(n + 1)]
    front = [seg.pt(t, interp(stations, t)[0]) for t in ts]
    back = [seg.pt(t, -interp(stations, t)[1]) for t in reversed(ts)]
    return smooth(front + back)


def belly(seg, t0, t1, c0, c1, w, k=0.7, n=18):
    """Ventre muscular em lente: centro c0->c1, meia-largura w, pontas finas."""
    pts1, pts2 = [], []
    for i in range(n + 1):
        u = i / n
        t = t0 + (t1 - t0) * u
        h = w * math.sin(math.pi * u) ** k + 1.5
        c = c0 + (c1 - c0) * u
        pts1.append(seg.pt(t, c + h))
        pts2.append(seg.pt(t, c - h))
    return smooth(pts1[1:-1] + [pts1[-1]] + list(reversed(pts2))[1:-1] + [pts2[0]])


def line(seg, t0, t1, off0, off1, bulge=0, n=10):
    pts = []
    for i in range(n + 1):
        u = i / n
        t = t0 + (t1 - t0) * u
        pts.append(seg.pt(t, off0 + (off1 - off0) * u + bulge * math.sin(math.pi * u)))
    return smooth(pts, closed=False)


# ---------- articulações (vista lateral, olhando para a direita) ----------
HIP = (500, 1150)
SHO = (705, 800)
F_KNEE = (775, 1185)
F_ANK = (735, 1455)
R_KNEE = (420, 1420)
R_ANK = (258, 1262)
ARM_SHO = (688, 818)
ELB = (676, 1022)
HAND = (672, 1186)

L_FT = math.dist(HIP, F_KNEE)
L_FS = math.dist(F_KNEE, F_ANK)
L_RT = math.dist(HIP, R_KNEE)
L_RS = math.dist(R_KNEE, R_ANK)
TOP_HIP = (522, 1025)
TOP_TILT = math.radians(9)  # tronco um pouco mais vertical em cima
GLOW = 0.55


def ik(a, c, l1, l2, side):
    """Joelho entre quadril a e tornozelo c; side escolhe a solução."""
    d = min(math.dist(a, c), l1 + l2 - 0.5)
    ux, uy = (c[0] - a[0]) / math.dist(a, c), (c[1] - a[1]) / math.dist(a, c)
    x = (l1 * l1 - l2 * l2 + d * d) / (2 * d)
    h = math.sqrt(max(l1 * l1 - x * x, 0))
    px, py = a[0] + ux * x, a[1] + uy * x
    k1 = (px - uy * h, py + ux * h)
    k2 = (px + uy * h, py - ux * h)
    return max((k1, k2), key=side)


def rot(v, ang):
    c, s_ = math.cos(ang), math.sin(ang)
    return (v[0] * c - v[1] * s_, v[0] * s_ + v[1] * c)


BASE = dict(HIP=HIP, SHO=SHO, F_KNEE=F_KNEE, R_KNEE=R_KNEE, ARM_SHO=ARM_SHO, ELB=ELB, HAND=HAND)
HEAD = (55, -102)
BUN = (7, -140)
NECK_END = (33, -52)
TILT = 0.0


def set_pose(p):
    """p = 1 no fundo do búlgaro, 0 em cima."""
    global HIP, SHO, F_KNEE, R_KNEE, ARM_SHO, ELB, HAND, TILT, GLOW
    global torso, f_thigh, f_shin, r_thigh, r_shin, uarm, farm
    b = BASE
    HIP = (TOP_HIP[0] + (b["HIP"][0] - TOP_HIP[0]) * p, TOP_HIP[1] + (b["HIP"][1] - TOP_HIP[1]) * p)
    TILT = -TOP_TILT * (1 - p)
    tv = rot(sub(b["SHO"], b["HIP"]), TILT)
    SHO = (HIP[0] + tv[0], HIP[1] + tv[1])
    F_KNEE = ik(HIP, F_ANK, L_FT, L_FS, lambda k: k[0])
    R_KNEE = ik(HIP, R_ANK, L_RT, L_RS, lambda k: k[1])
    ao = rot(sub(b["ARM_SHO"], b["SHO"]), TILT)
    ARM_SHO = (SHO[0] + ao[0], SHO[1] + ao[1])
    ELB = (ARM_SHO[0] + b["ELB"][0] - b["ARM_SHO"][0], ARM_SHO[1] + b["ELB"][1] - b["ARM_SHO"][1])
    HAND = (ELB[0] + b["HAND"][0] - b["ELB"][0], ELB[1] + b["HAND"][1] - b["ELB"][1])
    GLOW = 0.15 + 0.6 * p
    torso = Seg(HIP, SHO, (1, 0))
    f_thigh = Seg(HIP, F_KNEE, (0, -1))
    f_shin = Seg(F_KNEE, F_ANK, (1, 0))
    r_thigh = Seg(HIP, R_KNEE, (1, 0.3))
    r_shin = Seg(R_KNEE, R_ANK, (0.3, 1))
    uarm = Seg(ARM_SHO, ELB, (1, 0))
    farm = Seg(ELB, HAND, (1, 0))


def rel(off):
    v = rot(off, TILT)
    return (SHO[0] + v[0], SHO[1] + v[1])


set_pose(1)

TORSO_ST = [(-0.12, 60, 74), (0.05, 76, 84), (0.3, 58, 54), (0.5, 66, 60),
            (0.66, 96, 68), (0.78, 84, 72), (0.92, 64, 66), (1.04, 44, 50)]
THIGH_ST = [(-0.05, 70, 70), (0.15, 80, 78), (0.5, 66, 58), (0.88, 46, 40), (1.06, 38, 36)]
SHIN_ST = [(-0.05, 34, 38), (0.25, 30, 54), (0.6, 22, 30), (1.0, 16, 18), (1.04, 15, 17)]
UARM_ST = [(-0.08, 38, 40), (0.15, 42, 40), (0.55, 30, 32), (1.0, 23, 24), (1.06, 22, 22)]
FARM_ST = [(-0.05, 24, 24), (0.3, 27, 24), (1.0, 14, 14), (1.05, 14, 14)]

BODY = 'fill="url(#pele)" stroke="#7d828d" stroke-width="2.2"'
MUS = 'fill="url(#musc)" stroke="#8b909b" stroke-width="1.6"'
SEP = 'fill="none" stroke="#9aa0aa" stroke-width="1.8" stroke-linecap="round" opacity=".85"'
FIB = 'fill="none" stroke="#c7cad1" stroke-width="1.1" stroke-linecap="round" opacity=".9"'
RED = 'fill="url(#verm)" stroke="#7a0d12" stroke-width="2"'
REDFIB = 'fill="none" stroke="#ff8a8a" stroke-width="1.3" opacity=".55" stroke-linecap="round"'


def leg(thigh, shin, ankle, toe_dir, far=False):
    g = []
    op = ' style="filter:brightness(0.9)"' if far else ''
    g.append(f'<g{op}>')
    g.append(f'<path d="{limb(thigh, THIGH_ST)}" {BODY}/>')
    # quadríceps (vasto lateral + reto femoral)
    g.append(f'<path d="{belly(thigh, 0.1, 0.97, 18, 8, 30)}" {MUS}/>')
    g.append(f'<path d="{belly(thigh, 0.04, 0.9, 54, 28, 22)}" {MUS}/>')
    # isquiotibiais (sinergistas: rosa suave)
    hs = MUS if far else 'fill="url(#rosa)" stroke="#a7646a" stroke-width="1.6"'
    g.append(f'<path d="{belly(thigh, 0.12, 1.0, -32, -16, 28)}" {hs}/>')
    g.append(f'<path d="{line(thigh, 0.05, 0.98, 2, -2)}" {SEP}/>')
    for k in (-14, -26, -38):
        g.append(f'<path d="{line(thigh, 0.3, 0.88, k, k * 0.7, -4)}" '
                 + (FIB if far else 'fill="none" stroke="#e7b3b6" stroke-width="1.1" opacity=".8"') + '/>')
    for k in (20, 32, 48, 60):
        g.append(f'<path d="{line(thigh, 0.15, 0.88, k, k * 0.75, 6)}" {FIB}/>')
    # perna
    g.append(f'<path d="{limb(shin, SHIN_ST)}" {BODY}/>')
    g.append(f'<path d="{belly(shin, 0.0, 0.62, -24, -12, 24, 0.6)}" {MUS}/>')  # gastrocnêmio
    g.append(f'<path d="{belly(shin, 0.06, 0.82, 14, 8, 12)}" {MUS}/>')  # tibial anterior
    g.append(f'<path d="{line(shin, 0.55, 0.98, -14, -10)}" {SEP}/>')
    # pé
    ax, ay = ankle
    dx, dy = toe_dir
    nx, ny = -dy, dx
    pts = [(ax - dx * 34 - nx * 6, ay - dy * 34 - ny * 6),
           (ax - dx * 30 + nx * 22, ay - dy * 30 + ny * 22),
           (ax + dx * 40 + nx * 26, ay + dy * 40 + ny * 26),
           (ax + dx * 108 + nx * 24, ay + dy * 108 + ny * 24),
           (ax + dx * 116 + nx * 10, ay + dy * 116 + ny * 10),
           (ax + dx * 70 - nx * 8, ay + dy * 70 - ny * 8),
           (ax + dx * 10 - nx * 20, ay + dy * 10 - ny * 20)]
    g.append(f'<path d="{smooth(pts)}" {BODY}/>')
    g.append('</g>')
    return "\n".join(g)


def build():
    s = []
    s.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    s.append('''<defs>
  <radialGradient id="fundo" cx="50%" cy="58%" r="70%">
    <stop offset="0" stop-color="#1b1c20"/><stop offset="1" stop-color="#050506"/></radialGradient>
  <linearGradient id="pele" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#f7f7f9"/><stop offset=".55" stop-color="#d9dbe0"/>
    <stop offset="1" stop-color="#a9adb6"/></linearGradient>
  <radialGradient id="musc" cx="38%" cy="32%" r="75%">
    <stop offset="0" stop-color="#ffffff"/><stop offset=".6" stop-color="#e2e4e8"/>
    <stop offset="1" stop-color="#b6bac3"/></radialGradient>
  <radialGradient id="verm" cx="40%" cy="35%" r="75%">
    <stop offset="0" stop-color="#ff6b6b"/><stop offset=".55" stop-color="#e3262d"/>
    <stop offset="1" stop-color="#8e1117"/></radialGradient>
  <radialGradient id="rosa" cx="40%" cy="35%" r="75%">
    <stop offset="0" stop-color="#fbe3e4"/><stop offset=".6" stop-color="#eebfc2"/>
    <stop offset="1" stop-color="#c98d92"/></radialGradient>
  <linearGradient id="metal" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#9da1a8"/><stop offset=".5" stop-color="#5d6168"/>
    <stop offset="1" stop-color="#2e3136"/></linearGradient>
  <linearGradient id="estofado" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#3a3c42"/><stop offset="1" stop-color="#16171a"/></linearGradient>
  <filter id="brilho" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="16"/></filter>
  <filter id="sombra" x="-20%" y="-20%" width="140%" height="140%">
    <feGaussianBlur stdDeviation="10"/></filter>
</defs>''')
    s.append(f'<rect width="{W}" height="{H}" fill="url(#fundo)"/>')

    # título
    s.append('<text x="540" y="250" text-anchor="middle" font-family="DejaVu Sans" '
             'font-weight="bold" font-size="64" fill="#ffffff">Tronco inclinado</text>')
    s.append('<text x="540" y="340" text-anchor="middle" font-family="DejaVu Sans" '
             'font-weight="bold" font-size="72" fill="#d4a93a">+ GLÚTEO</text>')

    # chão e sombra
    s.append('<ellipse cx="520" cy="1505" rx="380" ry="26" fill="#000" opacity=".7" filter="url(#sombra)"/>')
    s.append('<line x1="80" y1="1500" x2="1000" y2="1500" stroke="#2c2e33" stroke-width="3"/>')

    # banco
    s.append('<rect x="100" y="1262" width="290" height="44" rx="18" fill="url(#estofado)" stroke="#55585f" stroke-width="2"/>')
    s.append('<rect x="140" y="1306" width="22" height="194" fill="url(#metal)"/>')
    s.append('<rect x="330" y="1306" width="22" height="194" fill="url(#metal)"/>')
    s.append('<rect x="118" y="1488" width="66" height="12" rx="4" fill="#5d6168"/>')
    s.append('<rect x="308" y="1488" width="66" height="12" rx="4" fill="#5d6168"/>')

    # perna de trás (longe da câmera)
    s.append(leg(r_thigh, r_shin, R_ANK, (-1, 0.12), far=True))

    # tronco
    s.append(f'<path d="{limb(torso, TORSO_ST)}" {BODY}/>')
    # eretores / dorsal
    s.append(f'<path d="{belly(torso, 0.28, 0.82, -36, -42, 20)}" {MUS}/>')
    s.append(f'<path d="{belly(torso, 0.5, 0.92, -14, -30, 24)}" {MUS}/>')
    # oblíquo externo
    s.append(f'<path d="{belly(torso, 0.08, 0.6, 10, 8, 26)}" {MUS}/>')
    # reto abdominal (borda anterior + interseções)
    s.append(f'<path d="{belly(torso, 0.03, 0.64, 48, 46, 13, 0.4)}" {MUS}/>')
    for t in (0.2, 0.33, 0.46):
        s.append(f'<path d="{line(torso, t, t + 0.01, 38, 62)}" {SEP}/>')
    # peito / mama
    s.append(f'<path d="{belly(torso, 0.56, 0.84, 64, 58, 36, 0.55)}" {MUS}/>')
    # trapézio
    s.append(f'<path d="{belly(torso, 0.8, 1.08, -44, -18, 18)}" {MUS}/>')
    for k in (-24, -36, -48):
        s.append(f'<path d="{line(torso, 0.48, 0.86, k, k - 6, -4)}" {FIB}/>')

    # glúteo máximo (alvo) com brilho
    glute = belly(torso, -0.2, 0.26, -62, -48, 50, 0.55)
    s.append(f'<path d="{glute}" fill="#ff2a2a" opacity="{GLOW:.2f}" filter="url(#brilho)"/>')
    s.append(f'<path d="{glute}" {RED}/>')
    for k in (-38, -52, -66, -80):
        s.append(f'<path d="{line(torso, -0.13, 0.19, k, k + 10, -10)}" {REDFIB}/>')
    # glúteo médio (apoio, rosa)
    s.append(f'<path d="{belly(torso, 0.14, 0.34, -32, -36, 18)}" '
             f'fill="url(#rosa)" stroke="#a7646a" stroke-width="1.6"/>')

    # pescoço e cabeça (manequim, sem rosto)
    neck = Seg(SHO, rel(NECK_END), (1, 0))
    s.append(f'<path d="{limb(neck, [(-0.3, 34, 36), (0.5, 26, 28), (1.1, 26, 28)])}" {BODY}/>')
    s.append(f'<path d="{belly(neck, -0.1, 1.0, 8, 4, 8)}" {MUS}/>')  # esternocleidomastoideo
    hx_, hy_ = rel(HEAD)
    ang = 22 + math.degrees(TILT)
    s.append(f'<ellipse cx="{hx_:.1f}" cy="{hy_:.1f}" rx="52" ry="62" transform="rotate({ang:.1f} {hx_:.1f} {hy_:.1f})" '
             'fill="url(#pele)" stroke="#7d828d" stroke-width="2.2"/>')
    # coque e rabo de cavalo (identifica figura feminina)
    bx_, by_ = rel(BUN)
    s.append(f'<ellipse cx="{bx_:.1f}" cy="{by_:.1f}" rx="30" ry="26" fill="url(#pele)" stroke="#7d828d" stroke-width="2"/>')

    # perna da frente
    s.append(leg(f_thigh, f_shin, F_ANK, (1, 0.02)))

    # braço
    s.append(f'<path d="{limb(uarm, UARM_ST)}" {BODY}/>')
    s.append(f'<path d="{belly(uarm, -0.12, 0.5, 2, 4, 38, 0.6)}" {MUS}/>')  # deltoide
    s.append(f'<path d="{belly(uarm, 0.35, 0.97, 14, 10, 14)}" {MUS}/>')  # bíceps
    s.append(f'<path d="{belly(uarm, 0.3, 0.97, -16, -10, 15)}" {MUS}/>')  # tríceps
    s.append(f'<path d="{limb(farm, FARM_ST)}" {BODY}/>')
    s.append(f'<path d="{belly(farm, 0.0, 0.65, 8, 4, 14)}" {MUS}/>')
    # halter (visto de lado)
    hx, hy = HAND[0], HAND[1] + 18
    s.append(f'<circle cx="{hx}" cy="{hy}" r="52" fill="url(#metal)" stroke="#202226" stroke-width="3"/>')
    s.append(f'<circle cx="{hx}" cy="{hy}" r="34" fill="none" stroke="#2a2c31" stroke-width="3"/>')
    s.append(f'<circle cx="{hx}" cy="{hy}" r="9" fill="#202226"/>')
    # mão
    hand = Seg(HAND, (HAND[0] + 2, HAND[1] + 40), (1, 0))
    s.append(f'<path d="{limb(hand, [(-0.1, 15, 15), (0.5, 20, 18), (1.0, 14, 12)])}" {BODY}/>')

    # rótulo do músculo-alvo
    lx, ly = torso.pt(0.02, -95)
    s.append(f'<line x1="{lx:.0f}" y1="{ly:.0f}" x2="345" y2="965" stroke="#ff4b4b" stroke-width="3"/>')
    s.append(f'<circle cx="{lx:.0f}" cy="{ly:.0f}" r="7" fill="#ff4b4b"/>')
    s.append('<text x="250" y="985" text-anchor="middle" font-family="DejaVu Sans" '
             'font-weight="bold" font-size="40" fill="#ffffff">GLÚTEO</text>')
    s.append('<text x="250" y="940" text-anchor="middle" font-family="DejaVu Sans" '
             'font-size="30" fill="#ff6b6b">músculo-alvo</text>')

    s.append('</svg>')
    return "\n".join(s)


def animar(seg=2.4, fps=30):
    import shutil, tempfile
    tmp = pathlib.Path(tempfile.mkdtemp())
    n = int(seg * fps)
    for i in range(n):
        u = i / n
        p = (1 - math.cos(2 * math.pi * u)) / 2  # sobe e desce
        p = 0.5 - 0.5 * math.cos(math.pi * p)
        set_pose(p)
        f = tmp / f"f{i:03d}.svg"
        f.write_text(build(), encoding="utf-8")
        subprocess.run(["rsvg-convert", "-o", str(tmp / f"f{i:03d}.png"), str(f)], check=True)
    base = OUT.parent / "bulgaro-gluteo"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-stream_loop", "2", "-framerate", str(fps),
                    "-i", str(tmp / "f%03d.png"), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-preset", "veryfast", "-crf", "20", f"{base}.mp4"], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", str(tmp / "f%03d.png"),
                    "-vf", "fps=15,scale=540:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128[p];[b][p]paletteuse",
                    "-loop", "0", f"{base}.gif"], check=True)
    shutil.rmtree(tmp)


if __name__ == "__main__":
    import sys
    if "--animar" in sys.argv:
        animar()
        raise SystemExit
    svg = OUT / "boneco-bulgaro-teste.svg"
    svg.write_text(build(), encoding="utf-8")
    subprocess.run(["rsvg-convert", "-o", str(OUT / "boneco-bulgaro-teste.png"), str(svg)], check=True)
    print("ok")
