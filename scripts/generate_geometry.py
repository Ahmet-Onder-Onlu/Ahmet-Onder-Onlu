"""Generate the profile's small, seamless geometry animation. Requires Pillow."""
from pathlib import Path
import math
from PIL import Image, ImageDraw

WIDTH, HEIGHT, SCALE = 1000, 150, 2
BACKGROUND = '#0d1117'
COLOURS = ['#a78bfa', '#60a5fa', '#2dd4bf', '#fbbf24', '#fb7185']
FRAMES, DURATION = 100, 60


def transform(points, cx, cy, angle):
    c, s = math.cos(angle), math.sin(angle)
    return [((cx + x*c-y*s)*SCALE, (cy + x*s+y*c)*SCALE) for x, y in points]


def regular(sides, radius):
    return [(radius*math.cos(-math.pi/2 + i*math.tau/sides),
             radius*math.sin(-math.pi/2 + i*math.tau/sides)) for i in range(sides)]


def frame(index):
    canvas = Image.new('RGB', (WIDTH*SCALE, HEIGHT*SCALE), BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    for x in range(20, WIDTH, 24):
        for y in range(16, HEIGHT, 24):
            draw.ellipse((x*SCALE,y*SCALE,x*SCALE+1,y*SCALE+1), fill='#222a36')
    shapes = [regular(4,31), [(-35,-20),(35,-20),(35,20),(-35,20)],
              None, regular(3,34), regular(6,32)]
    for slot, (shape, colour, turns) in enumerate(zip(shapes, COLOURS, [1,-1,2,-2,1])):
        cx, cy = 100+slot*200, 73
        angle = index/FRAMES*math.tau*turns + slot*0.3
        if shape is None:
            draw.ellipse(((cx-29)*SCALE,(cy-29)*SCALE,(cx+29)*SCALE,(cy+29)*SCALE), outline=colour, width=3*SCALE)
            px,py=transform([(29,0)],cx,cy,angle)[0]
            draw.ellipse((px-4*SCALE,py-4*SCALE,px+4*SCALE,py+4*SCALE),fill=colour)
        else:
            points=transform(shape,cx,cy,angle)
            draw.polygon(points, fill='#141c28')
            draw.line(points+[points[0]], fill=colour, width=3*SCALE, joint='curve')
            px,py=points[0]
            draw.ellipse((px-3*SCALE,py-3*SCALE,px+3*SCALE,py+3*SCALE),fill=colour)
        draw.line((cx*SCALE,119*SCALE,(cx+20)*SCALE,119*SCALE),fill=colour,width=2*SCALE)
    return canvas.resize((WIDTH,HEIGHT),Image.Resampling.LANCZOS)


if __name__ == '__main__':
    output = Path(__file__).resolve().parents[1] / 'assets'
    output.mkdir(exist_ok=True)
    frames = [frame(i) for i in range(FRAMES)]
    # A shared palette prevents colour flicker between frames.
    palette = frames[0].quantize(colors=96)
    frames = [f.quantize(palette=palette, dither=Image.Dither.NONE) for f in frames]
    frames[0].save(output/'geometry.gif',save_all=True,append_images=frames[1:],duration=DURATION,loop=0,optimize=True,disposal=2)
    print(output/'geometry.gif')
