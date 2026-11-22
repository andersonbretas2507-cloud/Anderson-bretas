"""Reel: elevação lateral no plano escapular (Ingrid). Gera /home/claude/lateral/elevacao-lateral.mp4"""
import math
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC = "/mnt/user-data/uploads/IMG_6973.mov"
W = Path("/home/claude/lateral/work")
W.mkdir(exist_ok=True)
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf"
GOLD, ORANGE, RED, GREEN = (224, 177, 63), (240, 138, 36), (232, 50, 30), (62, 207, 106)
BONE, BONE_D = (232, 233, 237), (150, 154, 164)
FPS = 30
TONE = ("zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,"
        "zscale=t=bt709:m=bt709:r=tv,format=yuv420p")
LOOK = "eq=contrast=1.07:saturation=1.06:gamma=0.98,unsharp=5:5:0.5,vignette=PI/7"


def font(size, bold=True):
    return ImageFont.truetype(FB if bold else FR, size)


def ease(u):
    u = max(0.0, min(1.0, u))
    return 0.5 - 0.5 * math.cos(math.pi * u)


def fundo():
    im = Image.new("RGB", (1080, 1920), (10, 10, 10))
    d = ImageDraw.Draw(im)
    for y in range(1920):
        k = 1 - abs(y - 900) / 1100
        c = int(10 + 14 * max(0, k))
        d.line([(0, y), (1080, y)], fill=(c + 6, c + 3, c - 2 if c > 2 else 0))
    return im


BG = None


def titulo(d, tag, cor_tag, linha1, linha2=None, y=300):
    f1, f2 = font(44), font(78)
    w = d.textlength(tag, font=f1)
    d.rounded_rectangle([540 - w / 2 - 26, y - 40, 540 + w / 2 + 26, y + 34], 18, fill=cor_tag)
    d.text((540, y - 3), tag, font=f1, fill=(15, 15, 15), anchor="mm")
    d.text((540, y + 110), linha1, font=f2, fill="white", anchor="mm")
    if linha2:
        d.text((540, y + 200), linha2, font=f2, fill="white", anchor="mm")


def rodape(d, linhas, y=1450, cor=(225, 225, 225)):
    f = font(46, bold=False)
    for i, l in enumerate(linhas):
        d.text((540, y + i * 62), l, font=f, fill=cor, anchor="mm")


def selo(d, x, y, ok):
    cor = GREEN if ok else RED
    d.ellipse([x - 42, y - 42, x + 42, y + 42], fill=cor)
    if ok:
        d.line([(x - 20, y + 2), (x - 5, y + 18), (x + 22, y - 16)], fill="white", width=11)
    else:
        d.line([(x - 18, y - 18), (x + 18, y + 18)], fill="white", width=11)
        d.line([(x - 18, y + 18), (x + 18, y - 18)], fill="white", width=11)


# ---------------- Animação 1: impacto subacromial ----------------
def ombro(t, dur):
    im = BG.copy()
    d = ImageDraw.Draw(im)
    titulo(d, "ERRO 1", RED, "BRAÇO TOTALMENTE", "NA LATERAL DO TRONCO")
    u = ease(t / (dur * 0.7))
    th = math.radians(8 + 80 * u)               # abdução do braço
    cx, cy = 520, 880 - 55 * u                  # cabeça do úmero sobe quando o braço abre no plano frontal
    r = 92
    # escápula / glenoide
    d.polygon([(300, 760), (420, 740), (445, 820), (430, 1000), (330, 1160), (280, 1000)], fill=BONE_D)
    # diáfise do úmero
    L = 400
    ex, ey = cx + L * math.sin(th), cy + L * math.cos(th)
    nx, ny = math.cos(th), -math.sin(th)
    w = 44
    d.polygon([(cx + nx * w, cy + ny * w), (ex + nx * (w - 8), ey + ny * (w - 8)),
               (ex - nx * (w - 8), ey - ny * (w - 8)), (cx - nx * w, cy - ny * w)], fill=BONE)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=BONE, outline=BONE_D, width=3)
    # tendão (supraespinal) passando sobre a cabeça do úmero
    gap = (cy - r) - 718                         # espaço entre cabeça do úmero e acrômio
    aperto = max(0.0, min(1.0, (40 - gap) / 40))
    cor_t = tuple(int(ORANGE[i] + (RED[i] - ORANGE[i]) * aperto) for i in range(3))
    if aperto > 0.6:
        glow = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse([cx - 150, cy - r - 70, cx + 150, cy - r + 40],
                                     fill=(255, 40, 30, int(150 * aperto)))
        im.paste(glow.filter(ImageFilter.GaussianBlur(25)), (0, 0), glow.filter(ImageFilter.GaussianBlur(25)))
        d = ImageDraw.Draw(im)
    d.arc([cx - r - 16, cy - r - 16, cx + r + 16, cy + r + 16], 200, 345, fill=cor_t, width=24)
    # acrômio (por cima)
    d.polygon([(360, 650), (720, 640), (790, 668), (770, 712), (600, 718), (420, 716), (380, 700)], fill=BONE_D)
    d.text((800, 600), "acrômio", font=font(36, False), fill=(200, 200, 200), anchor="lm")
    d.text((300, 1220), "escápula", font=font(36, False), fill=(200, 200, 200), anchor="mm")
    d.text((cx + 10, cy + 10), "úmero", font=font(36, False), fill=(60, 60, 60), anchor="mm")
    d.text((cx - 260, cy - r - 30), "tendões", font=font(36, False), fill=cor_t, anchor="rm")
    if aperto > 0.6:
        d.text((cx + 120, cy + r + 50), "ESPREMIDOS!", font=font(50), fill=RED, anchor="lm")
    rodape(d, ["O úmero sobe e “espreme” os tendões", "no espaço subacromial: risco de impacto"], y=1500)
    return im


# ---------------- Animação 2: cotovelo ----------------
def boneco(d, x0, ok, u):
    """Vista de frente, braço direito em elevação lateral."""
    d.ellipse([x0 - 45, 760, x0 + 45, 850], fill=BONE)                       # cabeça
    d.rounded_rectangle([x0 - 80, 870, x0 + 80, 1140], 30, fill=BONE)        # tronco
    d.rounded_rectangle([x0 - 70, 1140, x0 - 15, 1360], 20, fill=BONE)       # pernas
    d.rounded_rectangle([x0 + 15, 1140, x0 + 70, 1360], 20, fill=BONE)
    for s in (-1, 1):
        sx, sy = x0 + s * 85, 900
        a = math.radians(5 + 80 * u)                                         # abdução
        ex, ey = sx + s * 100 * math.sin(a), sy + 100 * math.cos(a)
        flex = math.radians(80 if not ok else 15)                            # flexão do cotovelo
        b = a - flex                                                         # antebraço cai em relação ao braço
        hx, hy = ex + s * 90 * math.sin(b), ey + 90 * math.cos(b)
        d.line([(sx, sy), (ex, ey)], fill=BONE, width=34)
        d.line([(ex, ey), (hx, hy)], fill=BONE, width=28)
        d.ellipse([ex - 17, ey - 17, ex + 17, ey + 17], fill=BONE)
        d.rounded_rectangle([hx - 30, hy - 14, hx + 30, hy + 14], 8, fill=(80, 84, 92))
        if not ok:
            d.ellipse([ex - 26, ey - 26, ex + 26, ey + 26], outline=RED, width=6)


def cotovelo(t, dur):
    im = BG.copy()
    d = ImageDraw.Draw(im)
    titulo(d, "ERRO 2", RED, "COTOVELO FLEXIONADO", "DEMAIS")
    u = ease((t % 1.6) / 0.8) if (t % 1.6) < 0.8 else 1 - ease(((t % 1.6) - 0.8) / 0.8)
    boneco(d, 280, False, u)
    boneco(d, 800, True, u)
    selo(d, 290, 1450, False)
    selo(d, 790, 1450, True)
    d.text((290, 1530), "cotovelo a 90°", font=font(38, False), fill="white", anchor="mm")
    d.text((790, 1530), "levemente flexionado", font=font(38, False), fill="white", anchor="mm")
    rodape(d, ["A alavanca encurta, o deltoide trabalha menos", "e o ombro tende a girar para dentro"], y=1640)
    return im


# ---------------- Animação 3: plano escapular (vista de cima) ----------------
def plano(t, dur):
    im = BG.copy()
    d = ImageDraw.Draw(im)
    titulo(d, "O CERTO", GREEN, "PLANO ESCAPULAR")
    cx, cy = 540, 1000
    d.text((540, 600), "vista de cima ↓", font=font(36, False), fill=(170, 170, 170), anchor="mm")
    # linha do plano frontal
    for x in range(110, 980, 36):
        d.line([(x, cy), (x + 18, cy)], fill=(*RED, ), width=5)
    d.text((140, cy + 40), "plano frontal", font=font(34, False), fill=RED, anchor="lm")
    u = ease((t - 0.4) / 1.6)
    ang = math.radians(32 * u)
    # tronco (elipse) e cabeça; frente = para cima
    d.ellipse([cx - 210, cy - 70, cx + 210, cy + 70], fill=BONE_D)
    d.ellipse([cx - 62, cy - 62, cx + 62, cy + 62], fill=BONE)
    d.polygon([(cx - 16, cy - 58), (cx + 16, cy - 58), (cx, cy - 92)], fill=BONE)
    d.text((cx, cy - 130), "frente", font=font(34, False), fill=(200, 200, 200), anchor="mm")
    for s in (-1, 1):
        sx = cx + s * 200
        L = 300
        ex, ey = sx + s * L * math.cos(ang), cy - L * math.sin(ang)
        d.line([(sx, cy), (ex, ey)], fill=BONE, width=48)
        d.ellipse([ex - 28, ey - 28, ex + 28, ey + 28], fill=(80, 84, 92))
        if u > 0.05:
            a0 = 0 if s == 1 else 180
            box = [sx - 170, cy - 170, sx + 170, cy + 170]
            if s == 1:
                d.arc(box, -math.degrees(ang), 0, fill=GREEN, width=8)
            else:
                d.arc(box, 180, 180 + math.degrees(ang), fill=GREEN, width=8)
    if u > 0.9:
        d.text((cx + 330, cy - 230), "~30°", font=font(64), fill=GREEN, anchor="mm")
        d.text((cx - 330, cy - 230), "~30°", font=font(64), fill=GREEN, anchor="mm")
    rodape(d, ["Braços um pouco à frente do corpo:", "mais espaço para os tendões trabalharem"], y=1450, cor=(235, 235, 235))
    return im


def anim(fn, dur, out):
    tmp = W / f"_{out}"
    tmp.mkdir(exist_ok=True)
    n = int(dur * FPS)
    for i in range(n):
        fn(i / FPS, dur).save(tmp / f"{i:04d}.png")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS), "-i", str(tmp / "%04d.png"),
                    "-vf", "fade=in:st=0:d=0.2", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                    "-pix_fmt", "yuv420p", str(W / f"{out}.mp4")], check=True)


# ---------------- trechos de vídeo com texto ----------------
def overlay_png(path, linhas_top, linhas_bot=None, cor_top="white", tag=None):
    im = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for y in range(560):
        d.line([(0, y), (1080, y)], fill=(0, 0, 0, int(185 * (1 - y / 560))))
    if linhas_bot:
        for y in range(1380, 1920):
            d.line([(0, y), (1080, y)], fill=(0, 0, 0, int(200 * min(1, (y - 1380) / 260))))
    y = 270
    if tag:
        t, c = tag
        w = d.textlength(t, font=font(44))
        d.rounded_rectangle([540 - w / 2 - 26, y - 40, 540 + w / 2 + 26, y + 34], 18, fill=c)
        d.text((540, y - 3), t, font=font(44), fill=(15, 15, 15), anchor="mm")
        y += 110
    for l, c in linhas_top:
        d.text((540, y), l, font=font(84), fill=c, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))
        y += 95
    if linhas_bot:
        y = 1560
        for l in linhas_bot:
            d.text((540, y), l, font=font(48, False), fill="white", anchor="mm")
            y += 64
    im.save(path)


def clip(a, b, vel, out, png=None):
    vf = f"{TONE},scale=1080:1920:flags=lanczos,setsar=1,setpts=(PTS-STARTPTS)/{vel},fps={FPS},{LOOK}"
    args = ["-ss", str(a), "-t", str(b - a), "-i", SRC]
    if png:
        args += ["-loop", "1", "-i", str(png)]
        fc = f"[0:v]{vf}[v];[1:v]format=rgba,fade=in:st=0:d=0.25:alpha=1[o];[v][o]overlay=0:0:shortest=1,format=yuv420p[x]"
    else:
        fc = f"[0:v]{vf},format=yuv420p[x]"
    subprocess.run(["ffmpeg", "-y", "-v", "error", *args, "-filter_complex", fc, "-map", "[x]", "-an",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
                    str(W / f"{out}.mp4")], check=True)


def cta(out):
    im = BG.copy()
    d = ImageDraw.Draw(im)
    d.text((540, 760), "SALVA", font=font(140), fill=GOLD, anchor="mm")
    d.text((540, 880), "para o próximo treino de ombro", font=font(52, False), fill="white", anchor="mm")
    d.text((540, 1060), "Comenta OMBRO", font=font(72), fill="white", anchor="mm")
    d.text((540, 1140), "que eu te respondo no direct", font=font(46, False), fill=(210, 210, 210), anchor="mm")
    d.text((540, 1320), "@andersonbretaspersonal", font=font(46), fill=GOLD, anchor="mm")
    im.save(W / "cta.png")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-t", "3", "-i", str(W / "cta.png"),
                    "-vf", f"fade=in:st=0:d=0.3,fps={FPS}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                    "-pix_fmt", "yuv420p", str(W / f"{out}.mp4")], check=True)


if __name__ == "__main__":
    BG = fundo()
    parte = sys.argv[1]
    if parte == "clips":
        overlay_png(W / "o1.png", [("SEU OMBRO DÓI NA", "white"), ("ELEVAÇÃO LATERAL?", GOLD)])
        clip(0.0, 3.2, 1.0, "c1", W / "o1.png")
        overlay_png(W / "o5.png", [("ASSIM:", GREEN)],
                    ["braços ~30° à frente · cotovelos levemente", "flexionados · sobe até a linha do ombro"])
        clip(12.0, 19.2, 1.2, "c5", W / "o5.png")
        clip(23.0, 24.6, 0.5, "c6")
    elif parte == "anims":
        anim(ombro, 5.0, "a2")
        anim(cotovelo, 4.0, "a3")
        anim(plano, 4.2, "a4")
        cta("c7")
    elif parte == "join":
        ordem = ["c1", "a2", "a3", "a4", "c5", "c6", "c7"]
        (W / "l.txt").write_text("".join(f"file '{W}/{o}.mp4'\n" for o in ordem))
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(W / "l.txt"),
                        "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-c:v", "libx264", "-preset", "medium",
                        "-crf", "21", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", "-movflags", "+faststart",
                        "/home/claude/lateral/elevacao-lateral.mp4"], check=True)
    elif parte == "prev":
        for fn, t, nm in ((ombro, 0.2, "o_a"), (ombro, 4.0, "o_b"), (cotovelo, 0.8, "cot"), (plano, 3.5, "pl")):
            fn(t, 5.0).resize((360, 640)).save(f"/tmp/{nm}.png")
