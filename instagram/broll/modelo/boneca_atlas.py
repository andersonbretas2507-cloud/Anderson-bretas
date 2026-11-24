"""Boneca em estilo atlas de anatomia (vista frontal), elevação lateral no plano frontal.
Uso: python3 boneca_atlas.py --teste | --animar
"""
import math
import pathlib
import shutil
import subprocess
import sys
import tempfile

import boneca_ombro as bo

OUT = pathlib.Path(__file__).resolve().parent
S = 0.72            # escala da figura
OX, OY = 540, 950   # incisura jugular (origem)
SHX, SHY = 178, 18  # articulação do ombro (lado direito, coordenadas locais)

MUS = 'fill="url(#m)" stroke="#6f737c" stroke-width="2.2" stroke-linejoin="round"'
MUS2 = 'fill="url(#m2)" stroke="#6f737c" stroke-width="2.2" stroke-linejoin="round"'
TEN = 'fill="url(#t)" stroke="#7d818a" stroke-width="1.6"'
FIB = 'fill="none" stroke="#9ea2ab" stroke-width="1.3" stroke-linecap="round" opacity=".9"'
DARK = 'fill="url(#tecido)" stroke="#111" stroke-width="2"'


def fibers(pairs, n, curve=0.0):
    """Linhas de fibra interpolando entre duas bordas (listas de pontos A0->A1 e B0->B1)."""
    (a0, a1), (b0, b1) = pairs
    out = []
    for i in range(1, n):
        u = i / n
        p = (a0[0] + (b0[0] - a0[0]) * u, a0[1] + (b0[1] - a0[1]) * u)
        q = (a1[0] + (b1[0] - a1[0]) * u, a1[1] + (b1[1] - a1[1]) * u)
        mx, my = (p[0] + q[0]) / 2 + curve * (q[1] - p[1]) * 0.15, (p[1] + q[1]) / 2 - curve * (q[0] - p[0]) * 0.15
        out.append(f'<path d="M{p[0]:.1f},{p[1]:.1f} Q{mx:.1f},{my:.1f} {q[0]:.1f},{q[1]:.1f}" {FIB}/>')
    return "".join(out)


def half_torso():
    """Metade direita do tronco (x>=0). Espelhada para a esquerda."""
    s = []
    # silhueta base
    s.append('<path d="M0,-70 L48,-78 C80,-55 120,-30 168,-6 C196,8 200,40 186,80 C176,110 168,150 162,200 '
             'C156,260 128,330 120,380 C124,430 160,480 172,540 L176,640 L0,640 Z" fill="url(#pele)" stroke="#6f737c" stroke-width="2.4"/>')
    # trapézio
    s.append(f'<path d="M6,-150 C20,-120 40,-95 60,-82 C95,-60 135,-35 170,-8 C140,-4 110,-2 80,2 C50,0 25,-10 4,-20 Z" {MUS}/>')
    s.append(fibers((((10, -140), (5, -25)), ((160, -10), (85, 0))), 7, 0.5))
    # esternocleidomastoideo
    s.append(f'<path d="M48,-190 C52,-150 40,-80 14,-8 L4,-14 C22,-80 30,-140 34,-190 Z" {MUS2}/>')
    # clavícula
    s.append('<path d="M6,-6 C50,-16 100,-12 168,-4 L168,6 C100,-2 50,-4 6,6 Z" fill="url(#osso)" stroke="#7d818a" stroke-width="1.6"/>')
    # peitoral maior
    s.append(f'<path d="M6,8 C60,4 120,6 170,30 C176,48 176,62 168,74 C120,120 70,150 10,150 Z" {MUS}/>')
    s.append(fibers((((10, 14), (168, 36)), ((12, 146), (166, 70))), 10, -0.3))
    # serrátil anterior (digitações)
    for i, y in enumerate((150, 185, 220)):
        s.append(f'<path d="M{168 - i * 4},{y} C150,{y + 6} 132,{y + 16} 118,{y + 30} C138,{y + 30} 156,{y + 26} {166 - i * 4},{y + 22} Z" {MUS2}/>')
    # oblíquo externo
    s.append(f'<path d="M118,170 C150,200 164,250 160,300 C150,360 140,420 160,500 C120,480 92,460 76,440 '
             f'C72,380 70,300 74,230 C90,210 104,190 118,170 Z" {MUS}/>')
    s.append(fibers((((120, 180), (78, 300)), ((158, 470), (90, 450))), 8, 0.2))
    # reto do abdome (3 segmentos + inferior)
    segs = [(170, 248), (256, 330), (338, 410), (418, 540)]
    for y0, y1 in segs:
        s.append(f'<path d="M6,{y0} L58,{y0 - 4} C70,{(y0 + y1) / 2} 70,{(y0 + y1) / 2} 60,{y1} L6,{y1} Z" {MUS}/>')
        for x in (20, 34, 48):
            s.append(f'<path d="M{x},{y0 + 6} L{x + 2},{y1 - 6}" {FIB}/>')
    # bainha / linea alba
    s.append('<path d="M0,160 L0,560" stroke="#8b8f98" stroke-width="3"/>')
    return "\n".join(s)


def coxa():
    s = ['<path d="M8,600 C60,590 150,600 178,620 C190,720 170,860 140,990 L36,990 C30,880 20,760 8,660 Z" '
         'fill="url(#pele)" stroke="#6f737c" stroke-width="2.4"/>']
    s.append(f'<path d="M150,640 C186,720 180,860 140,980 L118,970 C140,860 140,740 128,650 Z" {MUS2}/>')   # vasto lateral
    s.append(f'<path d="M126,640 C140,760 132,880 108,975 L70,975 C66,880 80,760 92,640 Z" {MUS}/>')       # reto femoral
    s.append(fibers((((100, 650), (76, 965)), ((124, 650), (104, 965))), 5))
    s.append(f'<path d="M70,900 C56,930 50,960 56,985 L92,985 C86,950 84,920 80,890 Z" {MUS}/>')          # vasto medial
    s.append(f'<path d="M150,630 C120,720 70,840 40,975 L30,975 C56,840 104,720 138,624 Z" {MUS2}/>')     # sartório
    s.append(f'<path d="M12,640 C40,700 46,780 40,880 L20,880 C18,800 14,720 10,660 Z" {MUS2}/>')         # adutores
    s.append(f'<path d="M50,990 C60,1010 110,1010 124,990 Z" {TEN}/>')
    return "\n".join(s)


def torso():
    h = half_torso() + coxa()
    return (f'<g>{h}</g><g transform="scale(-1,1)">{h}</g>'
            # top esportivo
            '<path d="M-150,50 C-100,40 -40,60 0,90 C40,60 100,40 150,50 C160,90 150,130 140,150 '
            'C100,160 40,165 0,160 C-40,165 -100,160 -140,150 C-150,130 -160,90 -150,50 Z" ' + DARK + '/>'
            '<path d="M-140,52 C-120,10 -110,-2 -96,-6 M140,52 C120,10 110,-2 96,-6" stroke="#222" stroke-width="10" fill="none"/>'
            # short
            '<path d="M-176,540 C-90,520 90,520 176,540 L182,690 C120,700 40,690 8,720 L0,730 L-8,720 C-40,690 -120,700 -182,690 Z" ' + DARK + '/>')


def braço():
    """Braço direito em coordenadas locais: ombro na origem, pendendo para +y."""
    s = []
    s.append('<path d="M-40,-10 C-48,80 -44,170 -36,300 C-34,360 -30,420 -22,500 L22,500 C30,420 36,360 40,300 '
             'C48,170 52,80 44,-10 Z" fill="url(#pele)" stroke="#6f737c" stroke-width="2.4"/>')
    # tríceps (lateral) e bíceps (anterior)
    s.append(f'<path d="M14,100 C40,140 44,220 34,300 L16,300 C22,220 18,150 6,110 Z" {MUS2}/>')
    s.append(f'<path d="M-30,120 C-44,170 -40,250 -20,300 L4,300 C10,240 6,170 -6,120 Z" {MUS}/>')
    s.append(fibers((((-26, 130), (-16, 296)), ((-4, 126), (2, 296))), 5))
    # tendão do bíceps / cotovelo
    s.append(f'<path d="M-12,296 L-6,330 L4,330 L2,296 Z" {TEN}/>')
    # antebraço: braquiorradial, flexores, extensores
    s.append(f'<path d="M-34,320 C-40,360 -34,420 -18,480 L-6,478 C-14,420 -16,360 -10,320 Z" {MUS}/>')
    s.append(f'<path d="M-8,322 C2,380 6,430 4,480 L16,480 C22,430 24,380 30,322 Z" {MUS2}/>')
    s.append(fibers((((-30, 330), (-14, 476)), ((-12, 326), (-8, 476))), 3))
    # mão
    s.append('<path d="M-22,498 C-26,530 -20,560 0,566 C20,560 26,530 22,498 Z" fill="url(#pele)" stroke="#6f737c" stroke-width="2"/>')
    # halter
    s.append('<rect x="-60" y="530" width="120" height="16" rx="6" fill="#55595f"/>'
             '<rect x="-74" y="508" width="22" height="60" rx="6" fill="url(#metal)" stroke="#222"/>'
             '<rect x="52" y="508" width="22" height="60" rx="6" fill="url(#metal)" stroke="#222"/>')
    # deltoide (3 porções) por cima da articulação
    s.append(f'<path d="M-6,-46 C40,-44 66,-10 60,40 C54,90 30,130 6,168 C-14,130 -46,80 -52,30 C-56,-10 -36,-40 -6,-46 Z" {MUS}/>')
    s.append('<path d="M-22,-36 C-22,40 -10,110 4,164 M26,-40 C30,40 22,110 8,164" stroke="#6f737c" stroke-width="2" fill="none"/>')
    s.append(fibers((((-46, 10), (4, 160)), ((54, 10), (8, 160))), 11))
    return "\n".join(s)


def cabeça():
    return ('<path d="M-34,-150 C-36,-120 -30,-90 -26,-70 L26,-70 C30,-90 36,-120 34,-150 Z" fill="url(#pele)" stroke="#6f737c" stroke-width="2.2"/>'
            '<ellipse cx="0" cy="-232" rx="72" ry="92" fill="url(#pele)" stroke="#6f737c" stroke-width="2.4"/>'
            '<path d="M-74,-250 C-70,-320 70,-320 74,-250 C60,-290 -60,-290 -74,-250 Z" fill="#3d3f45"/>'
            '<ellipse cx="0" cy="-330" rx="40" ry="30" fill="#3d3f45"/>'
            '<path d="M-72,-228 C-82,-224 -82,-200 -70,-196 M72,-228 C82,-224 82,-200 70,-196" stroke="#6f737c" stroke-width="2.2" fill="url(#pele)"/>')


DEFS = '''<defs>
<radialGradient id="fundo" cx="50%" cy="55%" r="75%"><stop offset="0" stop-color="#1c1d21"/><stop offset="1" stop-color="#050506"/></radialGradient>
<linearGradient id="pele" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f6f6f8"/><stop offset="1" stop-color="#c3c6cd"/></linearGradient>
<radialGradient id="m" cx="35%" cy="30%" r="80%"><stop offset="0" stop-color="#ffffff"/><stop offset=".6" stop-color="#dfe1e6"/><stop offset="1" stop-color="#a9adb6"/></radialGradient>
<radialGradient id="m2" cx="40%" cy="35%" r="80%"><stop offset="0" stop-color="#f1f2f5"/><stop offset="1" stop-color="#a2a6af"/></radialGradient>
<linearGradient id="t" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#e9e3cf"/><stop offset="1" stop-color="#c9c2aa"/></linearGradient>
<linearGradient id="osso" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f1ede0"/><stop offset="1" stop-color="#c9c2aa"/></linearGradient>
<linearGradient id="osso2" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#c9ccd3"/><stop offset="1" stop-color="#8d919a"/></linearGradient>
<linearGradient id="tecido" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a3c42"/><stop offset="1" stop-color="#1c1d21"/></linearGradient>
<linearGradient id="metal" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#9da1a8"/><stop offset=".5" stop-color="#5d6168"/><stop offset="1" stop-color="#2e3136"/></linearGradient>
<radialGradient id="verm" cx="40%" cy="35%" r="75%"><stop offset="0" stop-color="#ff6b6b"/><stop offset=".55" stop-color="#e3262d"/><stop offset="1" stop-color="#8e1117"/></radialGradient>
<filter id="brilho" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="16"/></filter>
</defs>'''


def frame(ang, titulo=True):
    aperto = max(0.0, min(1.0, (ang - 55) / 30))
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">', DEFS,
         '<rect width="1080" height="1920" fill="url(#fundo)"/>']
    if titulo:
        s.append(f'<text x="540" y="140" {bo.FONT} font-size="86" fill="#ffffff" text-anchor="middle">SEU OMBRO DÓI?</text>')
    s.append(f'<g transform="translate({OX},{OY}) scale({S})">')
    arm = braço()
    s.append(f'<g transform="translate({SHX},{SHY}) rotate({-ang:.2f})">{arm}</g>')
    s.append(f'<g transform="scale(-1,1) translate({SHX},{SHY}) rotate({-ang:.2f})">{arm}</g>')
    s.append(torso())
    s.append(cabeça())
    # deltoides por cima do tronco (redesenha só o deltoide)
    delt = arm[arm.rfind('<path d="M-6,-46'):]
    s.append(f'<g transform="translate({SHX},{SHY}) rotate({-ang:.2f})">{delt}</g>')
    s.append(f'<g transform="scale(-1,1) translate({SHX},{SHY}) rotate({-ang:.2f})">{delt}</g>')
    if aperto > 0:
        for sx in (1, -1):
            s.append(f'<circle cx="{sx * (SHX - 10)}" cy="{SHY - 30}" r="80" fill="#ff2a2a" opacity="{0.55 * aperto:.2f}" filter="url(#brilho)"/>')
            s.append(f'<path d="M{sx * 120},{SHY - 52} C{sx * 150},{SHY - 66} {sx * 190},{SHY - 56} {sx * 214},{SHY - 30}" '
                     f'stroke="url(#verm)" stroke-width="{22 - 8 * aperto:.1f}" stroke-linecap="round" fill="none" opacity="{aperto:.2f}"/>')
    s.append('</g>')
    # zoom do ombro (reaproveitado)
    zoom = bo.inset(ang, aperto)
    zoom = [z for z in zoom if 'stroke-dasharray' not in z]
    s += zoom
    s.append(f'<line x1="{OX + S * SHX:.0f}" y1="{OY + S * (SHY - 50):.0f}" x2="640" y2="600" stroke="#e0b13f" stroke-width="3" stroke-dasharray="10 8"/>')
    s.append(f'<text x="540" y="1770" {bo.FONT} font-size="44" fill="#ffffff" text-anchor="middle">Braço totalmente na lateral:</text>')
    s.append(f'<text x="540" y="1835" {bo.FONT} font-size="44" fill="#e0b13f" text-anchor="middle">o úmero sobe e espreme o tendão</text>')
    s.append('</svg>')
    return "\n".join(s)


def animar(dur=4.0, fps=30, out=OUT.parent / "ombro-tendao-espremido-atlas.mp4"):
    tmp = pathlib.Path(tempfile.mkdtemp())
    for i in range(int(dur * fps)):
        f = tmp / f"{i:04d}.svg"
        f.write_text(frame(bo.ang_t(i / fps, dur)), encoding="utf-8")
        subprocess.run(["rsvg-convert", "-o", str(tmp / f"{i:04d}.png"), str(f)], check=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(fps), "-i", str(tmp / "%04d.png"),
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", str(out)], check=True)
    shutil.rmtree(tmp)


if __name__ == "__main__":
    if "--animar" in sys.argv:
        animar()
    else:
        for a, n in ((10, "a"), (88, "b")):
            p = pathlib.Path(f"/tmp/at_{n}.svg")
            p.write_text(frame(a), encoding="utf-8")
            subprocess.run(["rsvg-convert", "-o", f"/tmp/at_{n}.png", str(p)], check=True)
