"""Thumbnail for long videos: python3 thumb.py motif "BIG LINE" "small line" out.jpg [seed]"""
import sys, motifs
from PIL import ImageDraw
motif, big, small, out = sys.argv[1:5]
seed = int(sys.argv[5]) if len(sys.argv) > 5 else 1
W, H = 1280, 720
img = motifs.make(motif, W, H, seed)
d = ImageDraw.Draw(img, 'RGBA')
d.rectangle([0, 0, W * 0.62, H], fill=(10, 8, 7, 170))
f = motifs.font('Inter.ttf', 120, 900)
lines = big.split('|')
size = 120
while max(d.textlength(l, font=f) for l in lines) > W * 0.56 and size > 50:
    size -= 6; f = motifs.font('Inter.ttf', size, 900)
y = H * 0.5 - len(lines) * size * 0.6
for l in lines:
    d.text((50 + 5, y + 5), l, font=f, fill=(0, 0, 0, 255))
    d.text((50, y), l, font=f, fill=(246, 240, 228, 255))
    y += size * 1.1
sf = motifs.font('Cormorant.ttf', 54, 700)
d.text((52, y + 20), small, font=sf, fill=motifs.GOLD + (255,))
# small seal badge
cx, cy, r = W - 90, 90, 52
d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=motifs.SEAL)
d.ellipse([cx - r * .78, cy - r * .78, cx + r * .78, cy + r * .78], outline=motifs.GOLD, width=3)
d.text((cx, cy), 'MT', font=motifs.font('Cormorant.ttf', 46, 700), fill=motifs.GOLD, anchor='mm')
img.save(out, quality=92)
