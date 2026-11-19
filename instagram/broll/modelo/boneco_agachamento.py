"""Animação: boneca anatômica no agachamento, quadríceps em vermelho.

Reaproveita o desenho do boneco_bulgaro.py. Gera ../agachamento-quadriceps.gif e .mp4.
Uso: python3 boneco_agachamento.py  (ou --teste para um quadro só)
"""
import math
import pathlib
import shutil
import subprocess
import sys
import tempfile

import boneco_bulgaro as b

OUT = pathlib.Path(__file__).resolve().parent
ANK = (575, 1455)           # tornozelo (os dois pés no chão)
FAR_DX = -18                # perna de trás levemente deslocada
L_TH, L_SH = b.L_FT, b.L_FS
L_TORSO = math.dist(b.BASE["HIP"], b.BASE["SHO"])
BASE_ANG = math.atan2(b.BASE["SHO"][0] - b.BASE["HIP"][0], b.BASE["HIP"][1] - b.BASE["SHO"][1])
TOP_HIP, BOT_HIP = (548, 918), (402, 1192)
TOP_LEAN, BOT_LEAN = math.radians(6), math.radians(38)

P = {}


def pose(p):
    hip = (TOP_HIP[0] + (BOT_HIP[0] - TOP_HIP[0]) * p, TOP_HIP[1] + (BOT_HIP[1] - TOP_HIP[1]) * p)
    lean = TOP_LEAN + (BOT_LEAN - TOP_LEAN) * p
    sho = (hip[0] + L_TORSO * math.sin(lean), hip[1] - L_TORSO * math.cos(lean))
    knee = b.ik(hip, ANK, L_TH, L_SH, lambda k: k[0])
    far_hip, far_ank = (hip[0] + FAR_DX, hip[1]), (ANK[0] + FAR_DX, ANK[1])
    far_knee = b.ik(far_hip, far_ank, L_TH, L_SH, lambda k: k[0])
    tilt = lean - BASE_ANG
    # estado usado pelas funções do módulo do búlgaro (cabeça, coque)
    b.HIP, b.SHO, b.TILT = hip, sho, tilt
    ao = b.rot(b.sub(b.BASE["ARM_SHO"], b.BASE["SHO"]), tilt)
    arm_sho = (sho[0] + ao[0], sho[1] + ao[1])
    # braços estendidos à frente para equilibrar (sobem conforme desce)
    a = math.radians(70 - 62 * p)          # ângulo do braço abaixo da horizontal
    elb = (arm_sho[0] + 200 * math.cos(a), arm_sho[1] + 200 * math.sin(a))
    hand = (elb[0] + 165 * math.cos(a), elb[1] + 165 * math.sin(a))
    P.update(p=p, hip=hip, sho=sho, knee=knee, far_hip=far_hip, far_knee=far_knee, far_ank=far_ank,
             arm_sho=arm_sho, elb=elb, hand=hand, glow=0.15 + 0.6 * p)


QUADS = [(0.1, 0.97, 18, 8, 30), (0.04, 0.9, 54, 28, 22)]


def quads_red(thigh, glow):
    s = []
    for t0, t1, c0, c1, w in QUADS:
        d = b.belly(thigh, t0, t1, c0, c1, w)
        s.append(f'<path d="{d}" fill="#ff2a2a" opacity="{glow:.2f}" filter="url(#brilho)"/>')
        s.append(f'<path d="{d}" {b.RED}/>')
    for k in (20, 32, 48, 60):
        s.append(f'<path d="{b.line(thigh, 0.15, 0.88, k, k * 0.75, 6)}" {b.REDFIB}/>')
    return "\n".join(s)


def build(titulo=True):
    p = P
    head = b.build().split("<rect x=\"100\" y=\"1262\"")[0]  # defs, fundo e título do búlgaro
    if titulo:
        head = head.replace(">Tronco inclinado<", ">Agachamento<").replace(">+ GLÚTEO<", ">QUADRÍCEPS<")
    s = [head]
    far_th = b.Seg(p["far_hip"], p["far_knee"], (0, -1))
    far_sh = b.Seg(p["far_knee"], p["far_ank"], (1, 0))
    s.append(b.leg(far_th, far_sh, p["far_ank"], (1, 0.02), far=True))
    s.append(f'<g style="filter:brightness(0.85)">{quads_red(far_th, p["glow"] * 0.6)}</g>')

    torso = b.Seg(p["hip"], p["sho"], (1, 0))
    s.append(f'<path d="{b.limb(torso, b.TORSO_ST)}" {b.BODY}/>')
    for args in [(0.28, 0.82, -36, -42, 20), (0.5, 0.92, -14, -30, 24), (0.08, 0.6, 10, 8, 26)]:
        s.append(f'<path d="{b.belly(torso, *args)}" {b.MUS}/>')
    s.append(f'<path d="{b.belly(torso, 0.03, 0.64, 48, 46, 13, 0.4)}" {b.MUS}/>')
    for t in (0.2, 0.33, 0.46):
        s.append(f'<path d="{b.line(torso, t, t + 0.01, 38, 62)}" {b.SEP}/>')
    s.append(f'<path d="{b.belly(torso, 0.56, 0.84, 64, 58, 36, 0.55)}" {b.MUS}/>')
    s.append(f'<path d="{b.belly(torso, 0.8, 1.08, -44, -18, 18)}" {b.MUS}/>')
    # glúteo: sinergista (rosa)
    s.append(f'<path d="{b.belly(torso, -0.2, 0.26, -62, -48, 50, 0.55)}" '
             'fill="url(#rosa)" stroke="#a7646a" stroke-width="1.6"/>')

    neck = b.Seg(p["sho"], b.rel(b.NECK_END), (1, 0))
    s.append(f'<path d="{b.limb(neck, [(-0.3, 34, 36), (0.5, 26, 28), (1.1, 26, 28)])}" {b.BODY}/>')
    hx, hy = b.rel(b.HEAD)
    ang = 22 + math.degrees(b.TILT)
    s.append(f'<ellipse cx="{hx:.1f}" cy="{hy:.1f}" rx="52" ry="62" transform="rotate({ang:.1f} {hx:.1f} {hy:.1f})" {b.BODY}/>')
    bx, by = b.rel(b.BUN)
    s.append(f'<ellipse cx="{bx:.1f}" cy="{by:.1f}" rx="30" ry="26" {b.BODY}/>')

    th = b.Seg(p["hip"], p["knee"], (0, -1))
    sh = b.Seg(p["knee"], ANK, (1, 0))
    s.append(b.leg(th, sh, ANK, (1, 0.02)))
    s.append(quads_red(th, p["glow"]))
    # canela por cima do fim do quadríceps, para o joelho ficar limpo
    s.append(f'<path d="{b.limb(sh, b.SHIN_ST[:2])}" {b.BODY}/>')

    ua = b.Seg(p["arm_sho"], p["elb"], (0, -1))
    fa = b.Seg(p["elb"], p["hand"], (0, -1))
    s.append(f'<path d="{b.limb(ua, b.UARM_ST)}" {b.BODY}/>')
    s.append(f'<path d="{b.belly(ua, -0.12, 0.5, 2, 4, 38, 0.6)}" {b.MUS}/>')
    s.append(f'<path d="{b.limb(fa, b.FARM_ST)}" {b.BODY}/>')
    hd = b.Seg(p["hand"], (p["hand"][0] + (p["hand"][0] - p["elb"][0]) * 0.25,
                           p["hand"][1] + (p["hand"][1] - p["elb"][1]) * 0.25), (0, -1))
    s.append(f'<path d="{b.limb(hd, [(-0.1, 15, 15), (0.5, 18, 18), (1.0, 12, 12)])}" {b.BODY}/>')

    # rótulo
    lx, ly = th.pt(0.45, 70)
    s.append(f'<line x1="{lx:.0f}" y1="{ly:.0f}" x2="250" y2="690" stroke="#ff4b4b" stroke-width="3"/>')
    s.append(f'<circle cx="{lx:.0f}" cy="{ly:.0f}" r="7" fill="#ff4b4b"/>')
    s.append('<text x="250" y="670" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" '
             'font-size="40" fill="#ffffff">QUADRÍCEPS</text>')
    s.append('<text x="250" y="625" text-anchor="middle" font-family="DejaVu Sans" font-size="30" '
             'fill="#ff6b6b">músculo-alvo</text>')
    s.append("</svg>")
    return "\n".join(s)


def animar(seg=2.4, fps=30):
    tmp = pathlib.Path(tempfile.mkdtemp())
    n = int(seg * fps)
    for i in range(n):
        u = i / n
        q = (1 - math.cos(2 * math.pi * u)) / 2
        pose(0.5 - 0.5 * math.cos(math.pi * q))
        f = tmp / f"f{i:03d}.svg"
        f.write_text(build(), encoding="utf-8")
        subprocess.run(["rsvg-convert", "-o", str(tmp / f"f{i:03d}.png"), str(f)], check=True)
    base = OUT.parent / "agachamento-quadriceps"
    ff = ["ffmpeg", "-y", "-loglevel", "error"]
    subprocess.run(ff + ["-stream_loop", "2", "-framerate", str(fps), "-i", str(tmp / "f%03d.png"),
                         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", "20",
                         f"{base}.mp4"], check=True)
    subprocess.run(ff + ["-framerate", str(fps), "-i", str(tmp / "f%03d.png"), "-vf",
                         "fps=15,scale=540:-1:flags=lanczos,split[a][c];[a]palettegen=max_colors=128[p];[c][p]paletteuse",
                         "-loop", "0", f"{base}.gif"], check=True)
    shutil.rmtree(tmp)


if __name__ == "__main__":
    if "--teste" in sys.argv:
        for p, nome in ((0, "cima"), (1, "baixo")):
            pose(p)
            sv = pathlib.Path(f"/tmp/agach-{nome}.svg")
            sv.write_text(build(), encoding="utf-8")
            subprocess.run(["rsvg-convert", "-o", f"/tmp/agach-{nome}.png", str(sv)], check=True)
    else:
        animar()
