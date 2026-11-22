"""Gera o carrossel de resultado da Marina Leal (6 slides 1080x1350).

Uso: python3 gerar.py /caminho/para/fotos-por-data
"""
import pathlib
import subprocess
import sys

from PIL import Image

FOTOS = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/home/claude/ingrid/orig")
OUT = pathlib.Path(__file__).resolve().parent
TMP = OUT / "_tmp"
TMP.mkdir(exist_ok=True)
LOGO = OUT.parent.parent / "landing/img/logo.png"

GOLD = "#e0b13f"
ORANGE = "#f08a24"
HANDLE = "@andersonbretaspersonal"

# Medidas do corpo em cada foto, na escala de 800 px de altura: (topo da cabeça, pés, centro x)
CORPO = {
    "IMG_5245": (113, 613, 192), "IMG_5596": (161, 644, 213), "IMG_6055": (113, 650, 178),
    "IMG_6375": (105, 640, 222), "IMG_6987": (101, 558, 221),
    "IMG_5247": (113, 586, 219), "IMG_5598": (113, 613, 216), "IMG_6059": (113, 650, 214), "IMG_6989": (101, 558, 220),
    "IMG_5246": (123, 667, 229), "IMG_6988": (117, 728, 250),
}
def recorte(nome, aspecto=0.44, sem_rosto=0.15):
    """Recorta do pescoço para baixo (rosto oculto), corpo no mesmo tamanho em todas as datas."""
    im = Image.open(FOTOS / f"{nome}.jpg")
    k = im.height / 800
    topo, pes, cx = (v * k for v in CORPO[nome])
    pescoco = topo + (pes - topo) * sem_rosto
    h = (pes - pescoco) * 1.05
    w = h * aspecto
    y0 = pescoco
    box = [cx - w / 2, y0, cx + w / 2, y0 + h]
    out = im.crop(tuple(int(v) for v in box)).resize((500, int(500 / aspecto)), Image.LANCZOS)
    p = TMP / f"{nome}.jpg"
    out.save(p, quality=93)
    return p


def recorte_livre(nome, box, larg=700):
    im = Image.open(FOTOS / f"{nome}.jpg")
    out = im.crop(box)
    out = out.resize((larg, int(larg * out.height / out.width)), Image.LANCZOS)
    p = TMP / f"{nome}.jpg"
    out.save(p, quality=93)
    return p, out.width / out.height


def base(n, corpo):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1080" height="1350">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#16120a"/><stop offset=".55" stop-color="#0b0b0b"/><stop offset="1" stop-color="#070707"/></linearGradient>
</defs>
<rect width="1080" height="1350" fill="url(#bg)"/>
{corpo}
<text x="60" y="1300" font-family="Inter" font-size="22" fill="#8a8a8a">{HANDLE}</text>
<text x="1020" y="1300" text-anchor="end" font-family="Inter" font-size="22" fill="#8a8a8a">{n}/6</text>
</svg>'''


_clip = [0]


def card(img, x, y, w, h, rotulo=None, cor=ORANGE):
    _clip[0] += 1
    c = f"c{_clip[0]}"
    s = (f'<clipPath id="{c}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="26"/></clipPath>'
         f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice" '
         f'clip-path="url(#{c})" xlink:href="{img}"/>'
         f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="26" fill="none" stroke="#ffffff" stroke-opacity=".12" stroke-width="2"/>')
    if rotulo:
        pw = 170
        s += (f'<rect x="{x + w / 2 - pw / 2}" y="{y + h - 70}" width="{pw}" height="46" rx="23" fill="{cor}"/>'
              f'<text x="{x + w / 2}" y="{y + h - 38}" text-anchor="middle" font-family="Inter" font-weight="800" '
              f'font-size="22" fill="#111">{rotulo}</text>')
    return s


def t(x, y, txt, size, cor="#fff", peso=800, anchor="start", fam="Inter"):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{fam}" font-weight="{peso}" '
            f'font-size="{size}" fill="{cor}">{txt}</text>')


def salvar(nome, svg):
    p = TMP / f"{nome}.svg"
    p.write_text(svg, encoding="utf-8")
    subprocess.run(["rsvg-convert", "-o", str(TMP / f"{nome}.png"), str(p)], check=True)
    Image.open(TMP / f"{nome}.png").convert("RGB").save(OUT / f"{nome}.jpg", quality=94)


def main():
    F = {k: recorte(k) for k in CORPO}
    R = [("IMG_5245", "JUL"), ("IMG_5596", "AGO"), ("IMG_6055", "SET"), ("IMG_6375", "2 NOV"), ("IMG_6987", "22 NOV")]

    # 1. Capa
    s = (t(540, 165, "4 MESES E MEIO.", 88, anchor="middle", peso=900)
         + t(540, 262, "MESMA MULHER.", 88, GOLD, anchor="middle", peso=900)
         + t(540, 322, "Ingrid · jul → nov 2026", 30, "#cfcfcf", 500, "middle"))
    s += card(F["IMG_5245"], 70, 380, 455, 760, "JUL 2026") + card(F["IMG_6987"], 555, 380, 455, 760, "NOV 2026", GOLD)
    s += t(540, 1215, "Arrasta e vê mês a mês →", 30, "#fff", 600, "middle")
    salvar("1-capa", base(1, s))

    # 2. Linha do tempo (frente)
    s = t(60, 130, "MÊS A MÊS", 26, ORANGE, 800) + t(60, 205, "A LINHA DO TEMPO", 64, peso=900)
    w, h = 182, 400
    for i, (k, r) in enumerate(R):
        x = 60 + i * (w + 12)
        s += card(F[k], x, 300, w, h)
        s += t(x + w / 2, 750, r, 30, GOLD if i == 4 else "#fff", 800, "middle")
    s += (t(540, 900, "Sem mudança de um dia para o outro.", 34, "#e8e8e8", 500, "middle")
          + t(540, 955, "Mudança de mês em mês.", 38, GOLD, 800, "middle"))
    salvar("2-linha-do-tempo", base(2, s))

    # 3. Costas
    s = t(60, 130, "DE COSTAS", 26, ORANGE, 800) + t(60, 205, "GLÚTEO E POSTERIOR", 64, peso=900)
    s += card(F["IMG_5247"], 110, 260, 410, 860, "JUL 2026") + card(F["IMG_6989"], 560, 260, 410, 860, "NOV 2026", GOLD)
    s += t(540, 1210, "Mais volume onde o treino mirou.", 34, "#e8e8e8", 600, "middle")
    salvar("3-costas", base(3, s))

    # 4. Perfil
    s = t(60, 130, "DE PERFIL", 26, ORANGE, 800) + t(60, 205, "POSTURA E CINTURA", 64, peso=900)
    s += card(F["IMG_5246"], 110, 260, 410, 860, "JUL 2026") + card(F["IMG_6988"], 560, 260, 410, 860, "NOV 2026", GOLD)
    s += t(540, 1210, "Abdômen mais firme, glúteo mais projetado.", 32, "#e8e8e8", 600, "middle")
    salvar("4-perfil", base(4, s))

    # 5. O método
    s = (t(540, 300, "O QUE FEZ", 76, anchor="middle", peso=900)
         + t(540, 390, "A DIFERENÇA", 76, GOLD, anchor="middle", peso=900))
    yy = 540
    for it in ["Treino individualizado", "Progressão de carga a cada ciclo", "Reavaliação todo mês",
               "Ajuste do programa pelos números", "Constância, mês após mês"]:
        s += f'<circle cx="250" cy="{yy - 10}" r="8" fill="{ORANGE}"/>' + t(280, yy, it, 38, "#e8e8e8", 500)
        yy += 80
    s += t(540, 1060, "Sem fórmula mágica. Com método.", 40, GOLD, 800, "middle")
    salvar("5-metodo", base(5, s))

    # 6. CTA
    import shutil
    shutil.copy(LOGO, TMP / "logo.png")
    s = (t(540, 300, "4 MESES E MEIO", 70, anchor="middle", peso=900)
         + t(540, 390, "JÁ DÃO PARA VER.", 70, GOLD, anchor="middle", peso=900)
         + '<clipPath id="lg"><circle cx="540" cy="600" r="75"/></clipPath>'
         + f'<image x="465" y="525" width="150" height="150" clip-path="url(#lg)" xlink:href="{TMP / "logo.png"}"/>'
         + t(540, 800, "Qual mês você achou que mais mudou?", 34, "#fff", 600, "middle")
         + t(540, 850, "Comenta aqui 👇".replace(" 👇", ""), 34, "#fff", 600, "middle")
         + t(540, 980, "Quer o seu? Link na bio.", 44, GOLD, 900, "middle"))
    salvar("6-cta", base(6, s))


if __name__ == "__main__":
    main()
