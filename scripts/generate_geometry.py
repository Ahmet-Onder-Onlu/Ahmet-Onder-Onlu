"""Generate seamless profile motion graphics with Pillow; no remote services."""
from pathlib import Path
import math
from PIL import Image, ImageDraw

W, H, S = 1000, 170, 2
BG = '#0d1117'
COLOURS = ['#a78bfa', '#60a5fa', '#2dd4bf', '#fbbf24', '#fb7185']
N, MS = 150, 40
OUT = Path(__file__).resolve().parents[1] / 'assets'


def regular(n, r):
    return [(r*math.cos(-math.pi/2+i*math.tau/n), r*math.sin(-math.pi/2+i*math.tau/n)) for i in range(n)]


def rotate(p, a):
    x,y=p
    return x*math.cos(a)-y*math.sin(a),x*math.sin(a)+y*math.cos(a)


def line(d, pts, colour, width=2):
    d.line([(x*S,y*S) for x,y in pts],fill=colour,width=width*S,joint='curve')


def dot(d,x,y,r,colour):
    d.ellipse(((x-r)*S,(y-r)*S,(x+r)*S,(y+r)*S),fill=colour)


def canvas(h):
    im=Image.new('RGB',(W*S,h*S),BG)
    d=ImageDraw.Draw(im)
    for x in range(20,W,24):
        for y in range(15,h,24):
            dot(d,x,y,.4,'#263040')
    return im,d


def burst_frame(i):
    im,d=canvas(H)
    t=i/N
    for k,(colour,turns) in enumerate(zip(COLOURS,[1,-1,2,-2,1])):
        cx,cy=100+k*200,80
        pts=[regular(4,31),[(-35,-20),(35,-20),(35,20),(-35,20)],regular(48,29),regular(3,34),regular(6,32)][k]
        angle=t*math.tau*turns+k*.3
        # Each shape gets a fast, staggered burst followed by an elastic rebuild.
        phase=(t-k/5)%1
        q=phase/.19
        amount=0
        if q<1:
            if q<.3:
                amount=1-(1-q/.3)**3
            else:
                u=(q-.3)/.7
                amount=(1-u)**2*(1+.13*math.sin(u*math.tau*2))
        segments=[]
        for j,p in enumerate(pts):
            end=pts[(j+1)%len(pts)]
            steps=1 if k==2 else 6
            for m in range(steps):
                a=(p[0]+(end[0]-p[0])*m/steps,p[1]+(end[1]-p[1])*m/steps)
                b=(p[0]+(end[0]-p[0])*(m+1)/steps,p[1]+(end[1]-p[1])*(m+1)/steps)
                mx,my=(a[0]+b[0])/2,(a[1]+b[1])/2
                norm=max(1,math.hypot(mx,my))
                distance=amount*(20+((j*7+m*11)%18))
                spin=amount*((j+m)%3-1)*1.9
                ends=[]
                for point in (a,b):
                    dx,dy=rotate((point[0]-mx,point[1]-my),spin)
                    x,y=rotate((mx+dx+mx/norm*distance,my+dy+my/norm*distance),angle)
                    ends.append((cx+x,cy+y))
                segments.append(ends)
        for ends in segments:line(d,ends,colour,2)
        if amount>.05:
            for j in range(8):
                a=j*math.tau/8+angle
                r=32+amount*42
                dot(d,cx+math.cos(a)*r,cy+math.sin(a)*r,1.3,colour)
        line(d,[(cx-10,149),(cx+10,149)],colour,1)
    return im.resize((W,H),Image.Resampling.LANCZOS)


def flow_frame(i):
    h=74
    im,d=canvas(h)
    t=i/100
    # Two quiet travelling signals weave between research and engineering.
    for lane,colour in enumerate(['#60a5fa','#a78bfa']):
        for x in range(40,961,3):
            y=37+math.sin(x/72-t*math.tau+lane*math.pi)*13
            dot(d,x,y,.7,'#273449')
        for j in range(24):
            x=40+((t*920+j*3+lane*460)%920)
            y=37+math.sin(x/72-t*math.tau+lane*math.pi)*13
            dot(d,x,y,1+j/22,colour)
    return im.resize((W,h),Image.Resampling.LANCZOS)


def save(frames,name):
    # Use colours sampled across the whole cycle to avoid frame-to-frame flicker.
    strip=Image.new('RGB',(W,frames[0].height*10))
    for n in range(10):strip.paste(frames[n*len(frames)//10],(0,n*frames[0].height))
    pal=strip.quantize(colors=80)
    images=[f.quantize(palette=pal,dither=Image.Dither.NONE) for f in frames]
    images[0].save(OUT/name,save_all=True,append_images=images[1:],duration=MS,loop=0,optimize=True,disposal=2)
    print(name,(OUT/name).stat().st_size,'bytes')


if __name__=='__main__':
    OUT.mkdir(exist_ok=True)
    save([burst_frame(i) for i in range(N)],'geometry.gif')
    save([flow_frame(i) for i in range(100)],'signal-flow.gif')
