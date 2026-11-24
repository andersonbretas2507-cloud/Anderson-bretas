"""Teste de estilo "ilustração de exercício": figura em cinza (lápis), músculo-alvo em vermelho.
Elevação lateral, vista frontal, deltoide em vermelho. Gera PNG transparente e MP4 com fundo verde (chroma key).
Uso: python3 boneca_lapis.py --teste | --animar
"""
import math
import pathlib
import shutil
import subprocess
import sys
import tempfile

import boneca_atlas as at

OUT = pathlib.Path(__file__).resolve().parent.parent

DEFS = '''<defs>
<linearGradient id="pele" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#d9d9d9"/><stop offset=".45" stop-color="#f7f7f7"/><stop offset="1" stop-color="#9c9c9c"/></linearGradient>
<linearGradient id="m" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fafafa"/><stop offset=".55" stop-color="#d6d6d6"/><stop offset="1" stop-color="#8f8f8f"/></linearGradient>
<linearGradient id="m2" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ececec"/><stop offset="1" stop-color="#8a8a8a"/></linearGradient>
<linearGradient id="t" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#e6e6e6"/><stop offset="1" stop-color="#bdbdbd"/></linearGradient>
<linearGradient id="osso" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#eeeeee"/><stop offset="1" stop-color="#c4c4c4"/></linearGradient>
<linearGradient id="tecido" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#9a9a9a"/><stop offset=".5" stop-color="#c8c8c8"/><stop offset="1" stop-color="#6e6e6e"/></linearGradient>
<linearGradient id="metal" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#9da1a8"/><stop offset=".5" stop-color="#5d6168"/><stop offset="1" stop-color="#2e3136"/></linearGradient>
<linearGradient id="verm" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e86a5a"/><stop offset=".55" stop-color="#c8342a"/><stop offset="1" stop-color="#7e1a15"/></linearGradient>
<pattern id="hach" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(35)">
<line x1="0" y1="0" x2="0" y2="7" stroke="#5a5a5a" stroke-width="1.1" opacity=".35"/></pattern>
</defs>'''


def estilo(svg):
    svg = (svg.replace('stroke="#6f737c"', 'stroke="#4d4d4d"').replace('stroke="#7d818a"', 'stroke="#555"')
              .replace('stroke="#9ea2ab"', 'stroke="#7a7a7a"').replace('stroke="#8b8f98"', 'stroke="#666"')
              .replace('stroke="#111"', 'stroke="#555"').replace('stroke="#222"', 'stroke="#555"'))
    return svg


def cabeça():
    # cabeça com rabo de cavalo (perfil frontal), sem traços de rosto
    return ('<path d="M-34,-150 C-36,-120 -30,-90 -26,-70 L26,-70 C30,-90 36,-120 34,-150 Z" fill="url(#pele)" stroke="#4d4d4d" stroke-width="2.2"/>'
            '<ellipse cx="0" cy="-232" rx="70" ry="90" fill="url(#pele)" stroke="#4d4d4d" stroke-width="2.4"/>'
            '<path d="M-72,-240 C-74,-330 74,-330 72,-240 C60,-292 -60,-292 -72,-240 Z" fill="#7a7a7a" stroke="#4d4d4d" stroke-width="2"/>'
            '<path d="M40,-300 C110,-300 120,-220 96,-150 C110,-210 90,-270 44,-280 Z" fill="#8a8a8a" stroke="#4d4d4d" stroke-width="2"/>'
            '<path d="M-72,-228 C-82,-224 -82,-200 -70,-196 M72,-228 C82,-224 82,-200 70,-196" stroke="#4d4d4d" stroke-width="2.2" fill="url(#pele)"/>'
            # sombra lateral do rosto
            '<path d="M30,-300 C80,-270 80,-190 40,-150 C60,-200 60,-260 30,-300 Z" fill="url(#hach)"/>')


def frame(ang, fundo=None):
    arm = at.braço()
    i = arm.rfind('<path d="M-6,-46')
    delt = arm[i:]
    delt_red = (delt.replace('fill="url(#m)"', 'fill="url(#verm)"', 1)
                    .replace('stroke="#6f737c" stroke-width="2"', 'stroke="#7e1a15" stroke-width="2"'))
    delt_red = delt_red.replace('stroke="#9ea2ab"', 'stroke="#f2a49a"')
    arm = arm[:i]
    sombra_braço = '<path d="M14,-10 C40,80 44,200 36,300 C32,380 28,440 20,500 L22,500 C30,420 36,360 40,300 C48,170 52,80 44,-10 Z" fill="url(#hach)"/>'
    s = ['<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">', DEFS]
    if fundo:
        s.append(f'<rect width="1080" height="1920" fill="{fundo}"/>')
    s.append(f'<g transform="translate(540,900) scale({at.S})">')
    for t in (f'translate({at.SHX},{at.SHY}) rotate({-ang:.2f})', f'scale(-1,1) translate({at.SHX},{at.SHY}) rotate({-ang:.2f})'):
        s.append(f'<g transform="{t}">{arm}{sombra_braço}</g>')
    s.append(at.torso())
    # sombreado de lápis no lado direito do tronco e das coxas
    s.append('<path d="M120,200 C150,260 160,330 125,390 C130,440 165,490 176,560 L176,640 L150,640 C140,520 110,440 110,380 '
             'C120,320 130,260 120,200 Z" fill="url(#hach)"/>')
    s.append('<path d="M150,700 C180,780 175,880 140,990 L118,990 C140,880 150,780 140,700 Z" fill="url(#hach)"/>')
    s.append(cabeça())
    for t in (f'translate({at.SHX},{at.SHY}) rotate({-ang:.2f})', f'scale(-1,1) translate({at.SHX},{at.SHY}) rotate({-ang:.2f})'):
        s.append(f'<g transform="{t}">{delt_red}</g>')
    s.append('</g></svg>')
    return estilo("\n".join(s))


def render(svg, png):
    p = pathlib.Path(png).with_suffix(".svg")
    p.write_text(svg, encoding="utf-8")
    subprocess.run(["rsvg-convert", "-o", str(png), str(p)], check=True)
    p.unlink()


def ang_t(t, per=2.4):
    k = (1 - math.cos(2 * math.pi * (t % per) / per)) / 2
    return 10 + 78 * k


if __name__ == "__main__":
    if "--animar" in sys.argv:
        tmp = pathlib.Path(tempfile.mkdtemp())
        fps, n = 30, 72
        for i in range(n):
            render(frame(ang_t(i / fps), "#00b140"), tmp / f"{i:03d}.png")
        base = OUT / "elevacao-lateral-ilustracao"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-stream_loop", "2", "-framerate", str(fps), "-i", str(tmp / "%03d.png"),
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p", f"{base}-fundo-verde.mp4"],
                       check=True)
        shutil.rmtree(tmp)
        render(frame(88), f"{base}.png")
    else:
        render(frame(12, "#222"), "/tmp/lp_a.png")
        render(frame(88, "#222"), "/tmp/lp_b.png")
