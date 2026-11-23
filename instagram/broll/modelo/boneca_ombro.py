"""Boneca anatômica de frente fazendo elevação lateral no plano frontal.
Tendão do supraespinal fica vermelho e "espremido" quando o braço passa de ~60°.
Uso: python3 boneca_ombro.py --teste | --animar
"""
import math
import pathlib
import shutil
import subprocess
import sys
import tempfile

import boneco_bulgaro as b

OUT = pathlib.Path(__file__).resolve().parent
CX = 400
NECK = (CX, 735)
PELV = (CX, 1300)
SH_R, SH_L = (CX + 128, 775), (CX - 128, 775)
L_UA, L_FA = 200, 155
FONT = 'font-family="DejaVu Sans" font-weight="bold"'

TORSO_ST = [(-0.06, 150, 150), (0.08, 168, 168), (0.42, 118, 118), (0.62, 132, 132),
            (0.86, 140, 140), (1.0, 112, 112), (1.04, 60, 60)]
UARM = [(-0.1, 44, 44), (0.2, 46, 44), (0.6, 33, 33), (1.0, 25, 25), (1.06, 24, 24)]
FARM = [(-0.05, 25, 25), (0.3, 28, 26), (1.0, 15, 15), (1.05, 15, 15)]


def arm(sh, ang, s, out):
    """ang: abdução em graus (0 = braço ao lado do corpo). s = +1 direita, -1 esquerda."""
    a = math.radians(ang)
    el = (sh[0] + s * L_UA * math.sin(a), sh[1] + L_UA * math.cos(a))
    a2 = math.radians(ang - 6)
    hd = (el[0] + s * L_FA * math.sin(a2), el[1] + L_FA * math.cos(a2))
    ua = b.Seg(sh, el, (0, -1))
    fa = b.Seg(el, hd, (0, -1))
    out.append(f'<path d="{b.limb(ua, UARM)}" {b.BODY}/>')
    out.append(f'<path d="{b.belly(ua, 0.35, 0.95, 0, 0, 16)}" {b.MUS}/>')            # bíceps/braquial
    out.append(f'<path d="{b.limb(fa, FARM)}" {b.BODY}/>')
    out.append(f'<path d="{b.belly(fa, 0.0, 0.6, 0, 0, 14)}" {b.MUS}/>')
    # deltoide cobrindo a cabeça do úmero
    out.append(f'<path d="{b.belly(ua, -0.22, 0.5, 0, 0, 46, 0.6)}" {b.MUS}/>')
    for k in (-24, -8, 8, 24):
        out.append(f'<path d="{b.line(ua, -0.1, 0.42, k, k * 0.4)}" {b.FIB}/>')
    # halter
    out.append(f'<rect x="{hd[0] - 52}" y="{hd[1] - 9}" width="104" height="18" rx="6" fill="#5d6168" '
               f'transform="rotate({-s * (90 - ang):.1f} {hd[0]:.1f} {hd[1]:.1f})"/>')
    for d in (-44, 44):
        px = hd[0] + d * math.cos(math.radians(-s * (90 - ang)))
        py = hd[1] + d * math.sin(math.radians(-s * (90 - ang)))
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="28" fill="url(#metal)" stroke="#202226" stroke-width="2"/>')
    return el


def doll(ang):
    s = []
    torso = b.Seg(PELV, NECK, (1, 0))
    s.append(f'<path d="{b.limb(torso, TORSO_ST)}" {b.BODY}/>')
    # quadril/pernas (cortadas na coxa)
    for dx in (-62, 62):
        th = b.Seg((CX + dx, 1270), (CX + dx * 1.1, 1470), (1, 0))
        s.append(f'<path d="{b.limb(th, [(0, 72, 72), (0.6, 62, 62), (1.0, 52, 52)])}" {b.BODY}/>')
        s.append(f'<path d="{b.belly(th, 0.1, 1.0, 0, 0, 40)}" {b.MUS}/>')
    s.append(f'<path d="M{CX - 165},1255 Q{CX},1330 {CX + 165},1255 L{CX + 150},1300 Q{CX},1360 {CX - 150},1300 Z" '
             'fill="#3a3c42" stroke="#202226" stroke-width="2"/>')
    # abdômen
    s.append(f'<rect x="{CX - 46}" y="1000" width="92" height="230" rx="40" fill="url(#musc)" stroke="#8b909b" stroke-width="1.6"/>')
    s.append(f'<line x1="{CX}" y1="1005" x2="{CX}" y2="1225" stroke="#9aa0aa" stroke-width="2"/>')
    for y in (1060, 1115, 1170):
        s.append(f'<line x1="{CX - 44}" y1="{y}" x2="{CX + 44}" y2="{y}" stroke="#9aa0aa" stroke-width="2"/>')
    for sgn in (-1, 1):  # oblíquos
        s.append(f'<path d="M{CX + sgn * 50},1000 Q{CX + sgn * 120},1080 {CX + sgn * 110},1240 L{CX + sgn * 52},1225 Z" '
                 'fill="url(#musc)" stroke="#8b909b" stroke-width="1.4"/>')
    # peitoral e top
    for sgn in (-1, 1):
        s.append(f'<path d="M{CX},800 Q{CX + sgn * 80},790 {CX + sgn * 125},805 Q{CX + sgn * 120},900 {CX + sgn * 60},950 '
                 f'Q{CX + sgn * 20},950 {CX},930 Z" fill="url(#musc)" stroke="#8b909b" stroke-width="1.6"/>')
    s.append(f'<path d="M{CX - 120},860 Q{CX - 60},990 {CX},935 Q{CX + 60},990 {CX + 120},860 L{CX + 115},905 '
             f'Q{CX + 60},1000 {CX},960 Q{CX - 60},1000 {CX - 115},905 Z" fill="#3a3c42" stroke="#202226" stroke-width="2"/>')
    # trapézio
    s.append(f'<path d="M{CX - 40},705 Q{CX - 90},760 {CX - 128},770 L{CX + 128},770 Q{CX + 90},760 {CX + 40},705 Z" '
             'fill="url(#musc)" stroke="#8b909b" stroke-width="1.6"/>')
    # pescoço e cabeça
    s.append(f'<rect x="{CX - 34}" y="640" width="68" height="110" rx="26" {b.BODY}/>')
    s.append(f'<ellipse cx="{CX}" cy="590" rx="62" ry="78" {b.BODY}/>')
    s.append(f'<ellipse cx="{CX}" cy="508" rx="36" ry="26" {b.BODY}/>')  # coque
    # braços
    el_r = arm(SH_R, ang, 1, s)
    arm(SH_L, ang, -1, s)
    # ombro: alerta vermelho no complexo do ombro quando aperta
    aperto = max(0.0, min(1.0, (ang - 55) / 30))
    if aperto > 0:
        for sh in (SH_R, SH_L):
            s.append(f'<circle cx="{sh[0]}" cy="{sh[1] - 10}" r="70" fill="#ff2a2a" opacity="{0.55 * aperto:.2f}" filter="url(#brilho)"/>')
            s.append(f'<circle cx="{sh[0]}" cy="{sh[1] - 10}" r="34" fill="url(#verm)" opacity="{0.9 * aperto:.2f}"/>')
    return s, aperto


def inset(ang, aperto):
    """Zoom do ombro direito: acrômio, cabeça do úmero e tendão do supraespinal."""
    cx, cy, R = 540, 440, 175
    s = [f'<clipPath id="zc"><circle cx="{cx}" cy="{cy}" r="{R}"/></clipPath>',
         f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="#141416"/>', '<g clip-path="url(#zc)">']
    hx, hy = cx - 40, cy + 40 - 48 * min(1, ang / 90)       # cabeça do úmero sobe
    a = math.radians(ang)
    ex, ey = hx + 420 * math.sin(a), hy + 420 * math.cos(a)
    s.append(f'<path d="M{cx - 220},{cy - 40} L{cx - 110},{cy - 60} L{cx - 95},{cy + 160} L{cx - 220},{cy + 230} Z" '
             'fill="url(#osso2)"/>')  # escápula/glenoide
    nx, ny = math.cos(a), -math.sin(a)
    s.append(f'<path d="M{hx + nx * 34},{hy + ny * 34} L{ex + nx * 26},{ey + ny * 26} L{ex - nx * 26},{ey - ny * 26} '
             f'L{hx - nx * 34},{hy - ny * 34} Z" fill="url(#osso)"/>')
    s.append(f'<circle cx="{hx}" cy="{hy}" r="62" fill="url(#osso)" stroke="#8b909b" stroke-width="2"/>')
    # tendão sobre a cabeça do úmero
    cor = f'rgb({int(240 - 8 * aperto)},{int(138 - 100 * aperto)},{int(36 - 6 * aperto)})'
    larg = 22 - 10 * aperto
    s.append(f'<path d="M{hx - 70},{hy - 30} A72,72 0 0 1 {hx + 70},{hy - 26}" fill="none" stroke="{cor}" '
             f'stroke-width="{larg:.1f}" stroke-linecap="round"/>')
    if aperto > 0.5:
        s.append(f'<ellipse cx="{hx}" cy="{hy - 72}" rx="80" ry="34" fill="#ff2a2a" opacity="{0.6 * aperto:.2f}" filter="url(#brilho)"/>')
    # acrômio por cima
    s.append(f'<path d="M{cx - 200},{cy - 140} L{cx + 120},{cy - 150} L{cx + 160},{cy - 118} L{cx + 40},{cy - 94} '
             f'L{cx - 180},{cy - 96} Z" fill="url(#osso2)"/>')
    s.append('</g>')
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="#e0b13f" stroke-width="5"/>')
    s.append(f'<text x="{cx - 60}" y="{cy - 165}" {FONT} font-size="26" fill="#cfcfcf" text-anchor="middle">acrômio</text>')
    s.append(f'<text x="{cx - 20}" y="{cy + 140}" {FONT} font-size="26" fill="#cfcfcf" text-anchor="middle">úmero</text>')
    lab = "TENDÃO ESPREMIDO!" if aperto > 0.5 else "tendão"
    s.append(f'<text x="{cx}" y="{cy - R - 45}" {FONT} font-size="{40 if aperto > 0.5 else 30}" '
             f'fill="{"#ff4b4b" if aperto > 0.5 else "#f08a24"}" text-anchor="middle">{lab}</text>')
    # linha ligando o ombro da boneca ao zoom
    s.append(f'<line x1="{SH_R[0] + 140}" y1="{SH_R[1] + 140}" x2="{cx + R * 0.6:.0f}" y2="{cy + R * 0.8:.0f}" '
             'stroke="#e0b13f" stroke-width="3" stroke-dasharray="10 8"/>')
    return s


def frame(ang, titulo=True):
    base = b.build().split('<rect width="1080" height="1920" fill="url(#fundo)"/>')[0]
    defs_extra = ('<defs><linearGradient id="osso" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f4f4f6"/>'
                  '<stop offset="1" stop-color="#b9bcc4"/></linearGradient>'
                  '<linearGradient id="osso2" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#c9ccd3"/>'
                  '<stop offset="1" stop-color="#8d919a"/></linearGradient></defs>')
    s = [base, defs_extra, '<rect width="1080" height="1920" fill="url(#fundo)"/>']
    if titulo:
        s.append(f'<text x="540" y="140" {FONT} font-size="86" fill="#ffffff" text-anchor="middle">SEU OMBRO DÓI?</text>')
    d, aperto = doll(ang)
    s.append('<g transform="translate(140,170)">')
    s += d
    s.append('</g>')
    s += inset(ang, aperto)
    s.append(f'<text x="540" y="1770" {FONT} font-size="44" fill="#ffffff" text-anchor="middle">Braço totalmente na lateral:</text>')
    s.append(f'<text x="540" y="1835" {FONT} font-size="44" fill="#e0b13f" text-anchor="middle">o úmero sobe e espreme o tendão</text>')
    s.append('</svg>')
    return "\n".join(s)


def ang_t(t, dur):
    u = (t % 2.0) / 2.0
    k = (1 - math.cos(2 * math.pi * u)) / 2
    return 8 + 84 * k


def animar(dur=4.0, fps=30, out=OUT.parent / "ombro-tendao-espremido.mp4"):
    tmp = pathlib.Path(tempfile.mkdtemp())
    for i in range(int(dur * fps)):
        f = tmp / f"{i:04d}.svg"
        f.write_text(frame(ang_t(i / fps, dur)), encoding="utf-8")
        subprocess.run(["rsvg-convert", "-o", str(tmp / f"{i:04d}.png"), str(f)], check=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(fps), "-i", str(tmp / "%04d.png"),
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", str(out)], check=True)
    shutil.rmtree(tmp)


if __name__ == "__main__":
    if "--animar" in sys.argv:
        animar()
    else:
        for a, n in ((10, "a"), (90, "b")):
            p = pathlib.Path(f"/tmp/om_{n}.svg")
            p.write_text(frame(a), encoding="utf-8")
            subprocess.run(["rsvg-convert", "-o", f"/tmp/om_{n}.png", str(p)], check=True)
