"""Render a Mühürlü Tarih video from a JSON spec.

Usage: python3 render.py spec.json out.mp4

Spec:
{
  "format": "short" | "long",
  "seed": 1,
  "intro": true,                # long only: 3.5 s seal + title card
  "title_card": "Göbeklitepe Neden Gömüldü?",
  "scenes": [
    {"motif": "mountains", "params": {"tent": true}, "lines": [
        "plain sentence (spoken and shown)",
        {"say": "bin dokuz yüz elli dokuz", "show": "1959"}
    ]}
  ]
}
TTS: sherpa-onnx 1.13.8 + Piper Turkish VITS voice (see setup.sh). Numbers in "say" must be written as words.
"""
import json, os, subprocess, sys, hashlib, random, math, shutil
from PIL import Image, ImageDraw
import motifs

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.environ.get('MT_MODELS', '/home/claude/tts/sherpa')
FPS = 30
ENC = ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', '-r', str(FPS)]
_synth = None


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-3000:])
        raise SystemExit('ffmpeg failed: ' + ' '.join(cmd[:6]))
    return r


def synth():
    global _synth
    if _synth is None:
        import sherpa_onnx
        v = os.environ.get('MT_VOICE', 'fahrettin')
        d = os.path.join(MODELS, f'vits-piper-tr_TR-{v}-medium')
        onnx = [f for f in os.listdir(d) if f.endswith('.onnx')][0]
        cfg = sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
            vits=sherpa_onnx.OfflineTtsVitsModelConfig(model=os.path.join(d, onnx), tokens=os.path.join(d, 'tokens.txt'),
                                                      data_dir=os.path.join(d, 'espeak-ng-data'), length_scale=float(os.environ.get('MT_PACE', '1.18'))),
            num_threads=2))
        _synth = sherpa_onnx.OfflineTts(cfg)
    return _synth


def tts(text, path):
    if os.path.exists(path):
        return
    import soundfile as sf
    a = synth().generate(text, sid=0, speed=1.0)
    tmp = path + '.raw.wav'
    sf.write(tmp, a.samples, a.sample_rate)
    run(['ffmpeg', '-y', '-i', tmp, '-af',
         'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,'
         'highpass=f=70,equalizer=f=180:t=q:w=1:g=2,aecho=0.8:0.5:40:0.12,loudnorm=I=-16:TP=-1.5',
         '-ar', '44100', '-ac', '2', path])
    os.remove(tmp)


def dur(path):
    r = run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path])
    return float(r.stdout.strip())


def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ''
    for wd in words:
        t = (cur + ' ' + wd).strip()
        if d.textlength(t, font=f) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def caption_png(text, W, H, fmt, path, heading=None):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if fmt == 'short':
        size, maxw, cy = 66, W * 0.84, H * 0.76
    else:
        size, maxw, cy = 50, W * 0.76, H * 0.83
    f = motifs.font('Inter.ttf', size, 700)
    lines = wrap(d, text, f, maxw)
    while len(lines) > (4 if fmt == 'short' else 2) and size > 30:
        size -= 4
        f = motifs.font('Inter.ttf', size, 700)
        lines = wrap(d, text, f, maxw)
    lh = size * 1.28
    top = cy - lh * len(lines) / 2
    # soft backing band
    band = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    db = ImageDraw.Draw(band)
    bw = max(d.textlength(l, font=f) for l in lines) + size * 1.2
    db.rounded_rectangle([W / 2 - bw / 2, top - size * 0.45, W / 2 + bw / 2, top + lh * len(lines) + size * 0.2], radius=int(size * 0.4), fill=(8, 6, 5, 150))
    img.alpha_composite(band)
    for i, l in enumerate(lines):
        y = top + i * lh
        d.text((W / 2 + 3, y + 3), l, font=f, fill=(0, 0, 0, 200), anchor='ma')
        d.text((W / 2, y), l, font=f, fill=(246, 240, 228, 255), anchor='ma')
    # channel tag
    tf = motifs.font('Cormorant.ttf', 44 if fmt == 'short' else 30, 700)
    tag = 'MÜHÜRLÜ TARİH'
    ty = H * 0.075 if fmt == 'short' else H * 0.05
    tx = W / 2 if fmt == 'short' else W * 0.06
    d.text((tx, ty), tag, font=tf, fill=motifs.GOLD + (230,), anchor='mm' if fmt == 'short' else 'lm')
    if heading:
        hf = motifs.font('Cormorant.ttf', 92 if fmt == 'short' else 64, 700)
        hl = wrap(d, heading, hf, W * 0.86)
        for i, l in enumerate(hl):
            d.text((W / 2, H * (0.2 if fmt == 'short' else 0.16) + i * 100), l, font=hf, fill=motifs.GOLD + (255,), anchor='mm')
    img.save(path)


def segment(bg, cap, W, H, start, length, scene_len, out, fade_in=False, fade_out=False):
    """Slow push-in over the whole scene; this segment covers [start, start+length)."""
    e = f'(({start}+t)/{scene_len})'
    sw = f"trunc({W}*(1.03+0.09*{e})/2)*2"
    sh = f"trunc({H}*(1.03+0.09*{e})/2)*2"
    vf = (f"[0:v]scale=w='{sw}':h='{sh}':eval=frame:flags=bicubic,crop={W}:{H}:x='(iw-{W})/2+(iw-{W})*0.3*sin({e}*3.14)':y='(ih-{H})/2',setsar=1,format=yuv420p[bg];"
          f"[bg][1:v]overlay=0:0:format=auto")
    fades = []
    if fade_in:
        fades.append('fade=t=in:st=0:d=0.5')
    if fade_out:
        fades.append(f'fade=t=out:st={max(0, length - 0.5):.3f}:d=0.5')
    if fades:
        vf += ',' + ','.join(fades)
    vf += ',format=yuv420p'
    tmp = out[:-4] + '.part.mp4'
    run(['ffmpeg', '-y', '-loop', '1', '-framerate', str(FPS), '-i', bg, '-loop', '1', '-framerate', str(FPS), '-i', cap,
         '-filter_complex', vf, '-t', f'{length:.3f}', '-an'] + ENC + [tmp])
    os.replace(tmp, out)


def music(path, length, seed):
    rnd = random.Random(seed)
    base = rnd.choice([55, 58.27, 61.74, 49])
    expr = (f"0.10*sin(2*PI*{base}*t)*(0.6+0.4*sin(2*PI*0.05*t))+0.07*sin(2*PI*{base*1.5}*t)*(0.5+0.5*sin(2*PI*0.031*t+1))"
            f"+0.05*sin(2*PI*{base*2}*t)*(0.5+0.5*sin(2*PI*0.023*t+2))+0.03*sin(2*PI*{base*3.01}*t)*(0.5+0.5*sin(2*PI*0.07*t))")
    run(['ffmpeg', '-y', '-f', 'lavfi', '-i', f"aevalsrc='{expr}':s=44100:d={length + 1:.2f}",
         '-f', 'lavfi', '-i', f'anoisesrc=color=brown:amplitude=0.05:d={length + 1:.2f}:r=44100',
         '-filter_complex', '[1]lowpass=f=300[n];[0][n]amix=inputs=2:weights=1 0.6,aecho=0.8:0.7:600|900:0.3|0.2,lowpass=f=1800,'
         f'afade=t=in:d=2,afade=t=out:st={max(0, length - 2.5):.2f}:d=2.5,volume=0.55',
         '-ac', '2', '-ar', '44100', '-t', f'{length:.3f}', path])


def main(spec_path, out_path):
    spec = json.load(open(spec_path, encoding='utf-8'))
    fmt = spec.get('format', 'short')
    W, H = (1080, 1920) if fmt == 'short' else (1920, 1080)
    seed = spec.get('seed', 1)
    work = out_path + '.work'
    os.makedirs(work, exist_ok=True)
    segs, audio_parts = [], []
    gap = 0.38 if fmt == 'short' else 0.5
    silence = os.path.join(work, 'gap.wav')
    run(['ffmpeg', '-y', '-f', 'lavfi', '-i', f'anullsrc=r=44100:cl=stereo', '-t', str(gap), silence])
    idx = 0

    if fmt == 'long' and spec.get('intro', True):
        bg = os.path.join(work, 'intro_bg.png')
        motifs.make('seal', int(W * 1.12), int(H * 1.12), seed).save(bg)
        cap = os.path.join(work, 'intro_cap.png')
        img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        f = motifs.font('Cormorant.ttf', 76, 700)
        d.text((W / 2, H * 0.86), spec.get('title_card', ''), font=f, fill=motifs.GOLD + (255,), anchor='mm')
        img.save(cap)
        o = os.path.join(work, f'seg{idx:03d}.mp4'); idx += 1
        segment(bg, cap, W, H, 0, 3.5, 3.5, o, True, True)
        segs.append(o)
        sil = os.path.join(work, 'intro.wav')
        run(['ffmpeg', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo', '-t', '3.5', sil])
        audio_parts.append(sil)

    for si, sc in enumerate(spec['scenes']):
        bg = os.path.join(work, f'bg{si:02d}.jpg')
        motifs.make(sc['motif'], int(W * 1.12), int(H * 1.12), seed * 100 + si, **sc.get('params', {})).save(bg, quality=92)
        lines = [l if isinstance(l, dict) else {'say': l, 'show': l} for l in sc['lines']]
        lens = []
        for li, l in enumerate(lines):
            key = hashlib.md5(l['say'].encode()).hexdigest()[:10]
            wav = os.path.join(work, f'v_{key}.wav')
            tts(l['say'], wav)
            lens.append(dur(wav) + gap)
            audio_parts += [wav, silence]
        scene_len = sum(lens)
        t = 0
        for li, l in enumerate(lines):
            cap = os.path.join(work, f'cap{si:02d}_{li:02d}.png')
            caption_png(l.get('show', l['say']), W, H, fmt, cap, sc.get('heading') if li == 0 else None)
            o = os.path.join(work, f'seg{idx:03d}.mp4'); idx += 1
            segment(bg, cap, W, H, t, lens[li], scene_len, o, fade_in=(li == 0), fade_out=(li == len(lines) - 1))
            segs.append(o)
            t += lens[li]
        print(f'scene {si + 1}/{len(spec["scenes"])} done ({scene_len:.1f}s)', flush=True)

    # join video
    lst = os.path.join(work, 'list.txt')
    open(lst, 'w').write(''.join(f"file '{s}'\n" for s in segs))
    vid = os.path.join(work, 'video.mp4')
    run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', vid])
    # join voice
    alst = os.path.join(work, 'alist.txt')
    open(alst, 'w').write(''.join(f"file '{a}'\n" for a in audio_parts))
    voice = os.path.join(work, 'voice.wav')
    run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', alst, '-c:a', 'pcm_s16le', voice])
    total = dur(vid)
    bgm = os.path.join(work, 'music.wav')
    music(bgm, total, seed)
    tmp = out_path[:-4] + '.part.mp4'
    run(['ffmpeg', '-y', '-i', vid, '-i', voice, '-i', bgm, '-filter_complex',
         '[1]apad[v];[v][2]amix=inputs=2:duration=longest:weights=1 0.35:normalize=0,alimiter=limit=0.95[a]',
         '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-t', f'{total:.3f}', '-movflags', '+faststart', tmp])
    os.replace(tmp, out_path)
    print(f'OK {out_path} {total:.1f}s')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
