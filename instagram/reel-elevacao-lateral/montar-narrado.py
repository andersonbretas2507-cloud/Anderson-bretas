import subprocess
from PIL import Image, ImageDraw, ImageFont
import editar as e
W=e.W; FB=e.FB
def png(name, top=None, bot=None, cor=(255,255,255), grande=None):
    im=Image.new('RGBA',(1080,1920),(0,0,0,0)); d=ImageDraw.Draw(im)
    if top:
        for y in range(520): d.line([(0,y),(1080,y)],fill=(0,0,0,int(190*(1-y/520))))
        y=260
        for l,c in top:
            d.text((540,y),l,font=ImageFont.truetype(FB,80),fill=c,anchor='mm',stroke_width=3,stroke_fill='black'); y+=92
    if bot:
        for y in range(1360,1920): d.line([(0,y),(1080,y)],fill=(0,0,0,int(205*min(1,(y-1360)/260))))
        y=1560
        for l,c in bot:
            d.text((540,y),l,font=ImageFont.truetype(FB,56),fill=c,anchor='mm',stroke_width=2,stroke_fill='black'); y+=70
    if grande:
        d.text((540,960),grande,font=ImageFont.truetype(FB,170),fill=e.GREEN,anchor='mm',stroke_width=6,stroke_fill='black')
    im.save(W/name)
G,O,GR=e.GOLD,e.ORANGE,e.GREEN
png('t1.png',top=[("O JEITO CERTO DA",(255,255,255)),("ELEVAÇÃO LATERAL",G)])
png('t2.png',bot=[("Afaste a mão ao máximo,",(255,255,255)),("para LONGE do corpo",G)])
png('t3.png',bot=[("Não é lateralizado totalmente:",(255,255,255)),("PLANO ESCAPULAR",GR),("mão um pouco na diagonal, à frente",(255,255,255))])
png('t4.png',bot=[("Esse é o jeito certo:",(255,255,255)),("sempre afastando bem do corpo",G)])
png('t5.png',grande="PERFEITO!")
png('t6.png',top=[("E OS ERROS QUE",(255,255,255)),("MAIS VEJO 👇".replace(" 👇",""),O)])
END=27.3
vf=f"{e.TONE},scale=1080:1920:flags=lanczos,setsar=1,fps=30,{e.LOOK}"
win=[('t1.png',0,3.2),('t2.png',3.2,10),('t3.png',10,18.5),('t4.png',18.5,25.4),('t5.png',25.4,END)]
inp=['-ss','0','-t',str(END),'-i',e.SRC,'-stream_loop','-1','-i',str(W/'a4.mp4')]
for p,_,_ in win: inp+=['-loop','1','-i',str(W/p)]
fc=f"[0:v]{vf}[b];[1:v]trim=0:8.5,setpts=PTS-STARTPTS+10/TB,scale=400:-2,format=yuva420p[pip];"
fc+="[b][pip]overlay=650:130:enable='between(t,10,18.5)':eof_action=pass[v0];"
for i,(p,a,b) in enumerate(win):
    fc+=f"[v{i}][{i+2}:v]overlay=0:0:enable='between(t,{a},{b})'[v{i+1}];"
fc+=f"[v{len(win)}]format=yuv420p[vo];[0:a]highpass=f=90,afftdn=nf=-25,loudnorm=I=-16:TP=-1.5:LRA=9,afade=out:st={END-0.4}:d=0.4[ao]"
subprocess.run(['ffmpeg','-y','-v','error',*inp,'-filter_complex',fc,'-map','[vo]','-map','[ao]','-t',str(END),
 '-c:v','libx264','-preset','veryfast','-crf','18','-c:a','aac','-ar','48000','-ac','2',str(W/'n1.mp4')],check=True)
# erros com título + CTA, com áudio mudo
def mudo(src,out,extra=None):
    args=['-i',str(W/src),'-f','lavfi','-i','anullsrc=r=48000:cl=stereo']
    fc='[0:v]null[v]'
    if extra:
        args+=['-loop','1','-i',str(W/extra)]; fc="[0:v][2:v]overlay=0:0:enable='lt(t,1.6)'[v]"
    subprocess.run(['ffmpeg','-y','-v','error',*args,'-filter_complex',fc,'-map','[v]','-map','1:a','-shortest',
     '-c:v','libx264','-preset','veryfast','-crf','18','-c:a','aac','-ar','48000','-ac','2',str(W/out)],check=True)
mudo('a2.mp4','n2.mp4'); mudo('a3.mp4','n3.mp4'); mudo('c7.mp4','n4.mp4')
# cartela "erros que mais vejo"
im=e.fundo(); d=ImageDraw.Draw(im)
d.text((540,880),"E OS ERROS",font=ImageFont.truetype(FB,110),fill='white',anchor='mm')
d.text((540,1010),"QUE MAIS VEJO",font=ImageFont.truetype(FB,110),fill=O,anchor='mm')
im.save(W/'cart.png')
subprocess.run(['ffmpeg','-y','-v','error','-loop','1','-t','1.4','-i',str(W/'cart.png'),'-f','lavfi','-i','anullsrc=r=48000:cl=stereo',
 '-vf','fade=in:st=0:d=0.2,fps=30','-shortest','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-ar','48000','-ac','2',str(W/'n15.mp4')],check=True)
(W/'l2.txt').write_text(''.join(f"file '{W}/{n}.mp4'\n" for n in ['n1','n15','n2','n3','n4']))
subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(W/'l2.txt'),'-c:v','libx264','-preset','medium','-crf','21',
 '-pix_fmt','yuv420p','-c:a','aac','-movflags','+faststart','/home/claude/lateral/elevacao-lateral-narrada.mp4'],check=True)
