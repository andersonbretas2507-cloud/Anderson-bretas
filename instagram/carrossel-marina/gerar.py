"""Gera o carrossel de resultado da Marina Leal (6 slides 1080x1350).

Uso: python3 gerar.py /caminho/para/fotos-por-data
"""
import pathlib
import subprocess
import sys

from PIL import Image

FOTOS = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/home/claude/marina/por-data")
OUT = pathlib.Path(__file__).resolve().parent
TMP = OUT / "_tmp"
TMP.mkdir(exist_ok=True)
LOGO = OUT.parent.parent / "landing/img/logo.png"

GOLD = "#e0b13f"
ORANGE = "#f08a24"
HANDLE = "@andersonbretaspersonal"

# Medidas do corpo em cada foto, na escala de 800 px de altura: (topo da cabeça, pés, centro x)
CORPO = {
    "2025-05_costas": (200, 695, 275),
    "2025-11_costas": (182, 745, 280),
    "2026-09_costas": (210, 635, 220),
}


def recorte(nome, aspecto=0.44, folga=1.16):
    """Recorta a foto deixando o corpo do mesmo tamanho em todas as datas."""
    im = Image.open(FOTOS / f"{nome}.jpg")
    k = im.height / 800
    topo, pes, cx = (v * k for v in CORPO[nome])
    h = (pes - topo) * folga
    w = h * aspecto
    cy = (topo + pes) / 2 + (pes - topo) * 0.01
    box = [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]
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
    c_mai = recorte("2025-05_costas")
    c_nov = recorte("2025-11_costas")
    c_set = recorte("2026-09_costas")
    frente, _ = recorte_livre("2025-05_frente", (330, 330, 870, 1460), 600)
    casual, ar = recorte_livre("2026-09_antes-depois-casual", (0, 0, 900, 1330), 800)

    # 1. Capa
    s = (t(540, 165, "RESULTADO", 92, anchor="middle", peso=900)
         + t(540, 265, "NÃO É LINEAR.", 92, GOLD, anchor="middle", peso=900)
         + t(540, 325, "Marina · 16 meses de treino", 30, "#cfcfcf", 500, "middle"))
    w, h, y = 300, 682, 380
    for i, (img, r) in enumerate([(c_mai, "MAI 2025"), (c_nov, "NOV 2025"), (c_set, "SET 2026")]):
        s += card(img, 60 + i * (w + 30), y, w, h, r)
    s += t(540, 1150, "Arrasta e vê o meio do caminho →", 30, "#ffffff", 600, "middle")
    salvar("1-capa", base(1, s))

    # 2. O começo
    s = (card(frente, 60, 120, 470, 1060, "MAI 2025")
         + t(580, 190, "O COMEÇO", 26, ORANGE, 800)
         + t(580, 262, "MAI 2025", 64, peso=900)
         + t(580, 330, "Marina, 1,76 m", 32, "#ffffff", 600)
         + t(580, 420, "O treino:", 28, GOLD, 700))
    itens = ["Treino individualizado", "A · B · C", "Base: agachamento,", "leg press, terra sumô", "e elevação pélvica",
             "Cardio? Já vinha das", "outras atividades dela"]
    yy = 470
    for i, it in enumerate(itens):
        bullet = i in (0, 2, 5)
        if bullet:
            s += f'<circle cx="590" cy="{yy - 9}" r="6" fill="{ORANGE}"/>'
        s += t(610, yy, it, 28, "#e8e8e8", 500)
        yy += 44 if i not in (1, 4) else 66
    salvar("2-comeco", base(2, s))

    # 3. Nov 2025: parece que piorou?
    s = (t(60, 130, "6 MESES DEPOIS", 26, ORANGE, 800)
         + t(60, 205, "PARECE QUE PIOROU?", 64, peso=900))
    s += card(c_mai, 110, 260, 410, 860, "MAI 2025") + card(c_nov, 560, 260, 410, 860, "NOV 2025")
    s += (t(540, 1180, "Roupa, luz e fase do corpo mudam a foto.", 30, "#e8e8e8", 500, "middle")
          + t(540, 1228, "É aqui que a maioria desiste.", 32, GOLD, 800, "middle"))
    salvar("3-nov-2025", base(3, s))

    # 4. Set 2026: ela continuou
    s = (t(60, 130, "MAIS 10 MESES", 26, ORANGE, 800)
         + t(60, 205, "ELA CONTINUOU.", 64, peso=900))
    s += card(c_nov, 110, 260, 410, 860, "NOV 2025") + card(c_set, 560, 260, 410, 860, "SET 2026", GOLD)
    s += (t(540, 1180, "Mesmo método: carga subindo ciclo a ciclo,", 30, "#e8e8e8", 500, "middle")
          + t(540, 1228, "de 15 até 8 repetições a cada 10 semanas.", 30, GOLD, 700, "middle"))
    salvar("4-set-2026", base(4, s))

    # 5. Os números
    s = (t(60, 130, "AVALIAÇÃO INICIAL → SET 2026", 26, ORANGE, 800)
         + t(60, 205, "OS NÚMEROS", 64, peso=900))
    ch = 860
    cw = int(ch * ar)
    s += card(casual, 60, 260, cw, ch)
    for lx, lab in ((60 + cw * 0.25, "ANTES"), (60 + cw * 0.75, "DEPOIS")):
        s += (f'<rect x="{lx - 70}" y="{260 + ch - 70}" width="140" height="46" rx="23" fill="{ORANGE}"/>'
              + t(lx, 260 + ch - 38, lab, 22, "#111", 800, "middle"))
    x0 = 60 + cw + 40
    dados = [("−7,3 kg", "de peso"), ("−6,6 kg", "de gordura"), ("−10 cm", "de cintura"),
             ("−9,5 cm", "de abdômen"), ("30,9 → 30,3 kg", "músculo mantido")]
    yy = 330
    for v, lab in dados:
        tam = 58 if len(v) < 10 else 40
        s += t(x0, yy, v, tam, GOLD, 900) + t(x0, yy + 42, lab, 28, "#e8e8e8", 500)
        yy += 160
    s += t(540, 1210, "Perdeu gordura sem perder músculo.", 34, "#ffffff", 800, "middle")
    salvar("5-numeros", base(5, s))

    # 6. CTA
    s = (t(540, 260, "O MEIO DO CAMINHO", 70, anchor="middle", peso=900)
         + t(540, 350, "NÃO É O FIM.", 70, GOLD, anchor="middle", peso=900)
         + f'<rect x="490" y="400" width="100" height="6" rx="3" fill="{ORANGE}"/>')
    yy = 500
    for it in ["Treino individualizado", "Reavaliação a cada fase", "Constância acima de pressa"]:
        s += f'<circle cx="352" cy="{yy - 9}" r="7" fill="{ORANGE}"/>' + t(375, yy, it, 34, "#e8e8e8", 500)
        yy += 62
    import shutil
    shutil.copy(LOGO, TMP / "logo.png")
    s += ('<clipPath id="lg"><circle cx="540" cy="790" r="75"/></clipPath>'
          f'<image x="465" y="715" width="150" height="150" clip-path="url(#lg)" xlink:href="{TMP / "logo.png"}"/>')
    s += (t(540, 940, "Comenta EU se você já pensou", 34, "#ffffff", 600, "middle")
          + t(540, 985, "em desistir no meio.", 34, "#ffffff", 600, "middle")
          + t(540, 1090, "Quer o seu? Link na bio.", 44, GOLD, 900, "middle"))
    salvar("6-cta", base(6, s))


if __name__ == "__main__":
    main()
