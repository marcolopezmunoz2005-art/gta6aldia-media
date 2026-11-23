"""Editor automático de vídeos verticales para GTA 6 al Día.

Uso:
    python3 render.py spec.json --key-file KEY --work DIR --usage usage.json

spec.json:
{
  "id": "2026-11-24_a",
  "hook": "3 COSAS QUE GTA 6\\nNO TE EXPLICA",          # rótulo superior durante la 1ª frase
  "lines": [                                           # una entrada por frase de la voz
    {"text": "Frase que dice la voz.", "caption": "TEXTO\\nEN PANTALLA", "color": "#FFFFFF", "tags": ["police", "cars"]}
  ],
  "outro_caption": "HASTA MAÑANA"
}

Hace: voz con ElevenLabs por frase (con pausas naturales), elige planos del catálogo por etiquetas
(sin repetir dentro del vídeo y priorizando los menos usados), quita las franjas negras, recorta a 9:16
con un zoom suave, subtítulos con Inter Display, música con ducking bajo la voz y cierre animado.
"""
import argparse
import json
import random
import subprocess
import urllib.request
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
FONTS = HERE.parent / "fonts"
W, H, FPS = 1080, 1920, 30
LINE_GAP = 0.28      # pausa entre frases (s)
LEAD_IN = 0.15       # silencio antes de la primera frase (s)


def run(cmd):
    subprocess.run(cmd, check=True, capture_output=True)


def probe_duration(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                   "-of", "csv=p=0", str(path)])
    return float(out.decode().strip())


def download(url, dest):
    if dest.exists() and dest.stat().st_size > 1000:
        return dest
    with urllib.request.urlopen(url, timeout=300) as r, open(dest, "wb") as f:
        f.write(r.read())
    return dest


def read_key(path):
    raw = Path(path).read_bytes().decode("utf-8-sig")
    return "".join(raw.split())


def tts(text, key, voice_id, model, dest):
    if dest.exists():
        return dest
    body = json.dumps({"text": text, "model_id": model,
                       "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.35}}).encode()
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44100_128",
        data=body, headers={"xi-api-key": key, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
        f.write(r.read())
    return dest


# ---------- selección de planos ----------
def pick_shots(catalog, usage, tags, need, used_ids, rng):
    """Devuelve [(shot, start, dur)] que suman `need` segundos."""
    def score(s):
        overlap = len(set(s["tags"]) & set(tags))
        last = usage.get(s["id"], "2000-01-01")
        return (-overlap, last, rng.random())

    pool = [s for s in catalog if s["id"] not in used_ids]
    pool.sort(key=score)
    picks, left = [], need
    for s in pool:
        if left <= 0.05:
            break
        seg = s["end"] - s["start"]
        if seg < 1.0:
            continue
        dur = min(left if left < 2.3 else rng.uniform(1.3, 1.9), seg)
        if left - dur < 0.7 and left - dur > 0.05:          # evitar un último plano demasiado corto
            dur = min(left, seg)
        start = s["start"] + rng.uniform(0, max(0.0, seg - dur))
        picks.append((s, round(start, 2), round(dur, 3)))
        used_ids.add(s["id"])
        left = round(left - dur, 3)
    if left > 0.05:                                         # alarga el último plano si faltara algo
        s, st, d = picks[-1]
        picks[-1] = (s, st, round(d + left, 3))
    return picks


def render_shot(src, crop, start, dur, dest):
    frames = max(1, round(dur * FPS))
    vf = (f"crop={crop},scale=-2:{H},crop={W}:{H},setsar=1,fps={FPS},"
          f"zoompan=z='1+0.06*on/{frames}':d=1:s={W}x{H}:fps={FPS},"
          f"eq=contrast=1.05:saturation=1.1")
    run(["ffmpeg", "-y", "-ss", f"{start:.2f}", "-t", f"{dur:.3f}", "-i", str(src), "-vf", vf,
         "-frames:v", str(frames), "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
         "-pix_fmt", "yuv420p", str(dest)])


# ---------- subtítulos ASS ----------
def ass_time(t):
    t = max(0.0, t)
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def ass_color(hex_rgb, alpha="00"):
    hex_rgb = hex_rgb.lstrip("#")
    r, g, b = hex_rgb[0:2], hex_rgb[2:4], hex_rgb[4:6]
    return f"&H{alpha}{b}{g}{r}".upper()


def build_ass(spec, timeline, total, outro_start, dest):
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Brand,Inter Display ExtraBold,30,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,2,0,1,2,0,8,60,60,70,1
Style: Hook,Inter Display Black,76,&H00FFFFFF,&H00FFFFFF,&H00882EFF,&H00882EFF,0,0,0,0,100,100,0,0,3,22,0,8,90,90,230,1
Style: Cap,Inter Display Black,72,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,7,3,5,80,80,0,1
Style: Outro,Inter Display Black,64,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,0,0,5,80,80,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    ev.append(f"Dialogue: 0,{ass_time(0)},{ass_time(outro_start)},Brand,,0,0,0,,GTA 6 AL DÍA  ·  Imágenes: Rockstar Games")
    first_end = timeline[0][1]
    hook = spec["hook"].replace("\n", "\\N")
    ev.append(f"Dialogue: 1,{ass_time(0)},{ass_time(first_end)},Hook,,0,0,0,,{{\\fad(80,120)}}{hook}")
    for i, ((st, en), line) in enumerate(zip(timeline, spec["lines"])):
        if i == 0 and not line.get("caption"):
            continue
        cap = line.get("caption", "").replace("\n", "\\N")
        if not cap:
            continue
        col = ass_color(line.get("color", "#FFFFFF"))
        pop = "{\\fscx88\\fscy88\\t(0,120,\\fscx100\\fscy100)\\fad(60,80)}"
        ev.append(f"Dialogue: 2,{ass_time(st)},{ass_time(en)},Cap,,0,0,0,,{{\\pos({W//2},{int(H*0.64)})\\c{col}}}{pop}{cap}")
    if spec.get("outro_caption"):
        oc = spec["outro_caption"].replace("\n", "\\N")
        ev.append(f"Dialogue: 2,{ass_time(outro_start + 0.25)},{ass_time(total)},Outro,,0,0,0,,{{\\pos({W//2},{int(H*0.68)})\\fad(150,0)}}{oc}")
    dest.write_text(head + "\n".join(ev) + "\n", encoding="utf-8")


# ---------- montaje ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--key-file", required=True)
    ap.add_argument("--work", default="work")
    ap.add_argument("--usage", default=str(HERE / "usage.json"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--seed", type=int, default=None)
    a = ap.parse_args()

    cfg = json.loads((HERE / "config.json").read_text())
    catalog = json.loads((HERE / "catalog.json").read_text())
    spec = json.loads(Path(a.spec).read_text())
    usage_path = Path(a.usage)
    usage = json.loads(usage_path.read_text()) if usage_path.exists() else {}
    rng = random.Random(a.seed if a.seed is not None else hash(spec["id"]))

    work = Path(a.work) / spec["id"]
    (work / "clips").mkdir(parents=True, exist_ok=True)
    assets = Path(a.work) / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    src = {name: download(url, assets / f"{name}.mp4") for name, url in cfg["sources"].items()}
    outro = download(cfg["outro_url"], assets / "outro.mp4")
    music = None
    if cfg.get("music_url"):
        try:
            music = download(cfg["music_url"], assets / "music.mp3")
        except Exception as e:                               # sin música si no se puede descargar
            print("sin música:", e)

    # 1) voz por frase
    key = read_key(a.key_file)
    timeline, t = [], LEAD_IN
    voice_files = []
    for i, line in enumerate(spec["lines"]):
        mp3 = tts(line["text"], key, cfg["voice_id"], cfg["tts_model"], work / f"line{i}.mp3")
        d = probe_duration(mp3)
        timeline.append((t, t + d))
        voice_files.append((mp3, t))
        t += d + LINE_GAP
    voice_end = t - LINE_GAP + 0.35

    # 2) planos
    used, plan = set(), []
    for i, ((st, en), line) in enumerate(zip(timeline, spec["lines"])):
        seg_start = 0.0 if i == 0 else st
        seg_end = timeline[i + 1][0] if i + 1 < len(timeline) else voice_end
        plan += pick_shots(catalog, usage, line.get("tags", []), seg_end - seg_start, used, rng)
    clips = []
    for k, (s, st, d) in enumerate(plan):
        dest = work / "clips" / f"{k:02d}.mp4"
        render_shot(src[s["src"]], s["crop"], st, d, dest)
        clips.append(dest)
    outro_norm = work / "clips" / "zz_outro.mp4"
    run(["ffmpeg", "-y", "-i", str(outro), "-vf", f"scale={W}:{H},setsar=1,fps={FPS}", "-an",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", str(outro_norm)])
    clips.append(outro_norm)
    (work / "concat.txt").write_text("".join(f"file '{c.resolve()}'\n" for c in clips))
    base = work / "base.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(work / "concat.txt"), "-c", "copy", str(base)])
    total = probe_duration(base)
    outro_start = total - probe_duration(outro_norm)

    # 3) subtítulos
    ass = work / "subs.ass"
    build_ass(spec, timeline, total, outro_start, ass)

    # 4) audio: voz + música con ducking
    inputs, filt = [], []
    for j, (mp3, st) in enumerate(voice_files):
        inputs += ["-i", str(mp3)]
        filt.append(f"[{j}:a]aresample=44100,adelay={int(st*1000)}|{int(st*1000)},volume=1.6[v{j}]")
    n = len(voice_files)
    filt.append("".join(f"[v{j}]" for j in range(n)) + f"amix=inputs={n}:normalize=0,apad=whole_dur={total:.2f}[voice]")
    if music:
        inputs += ["-stream_loop", "-1", "-i", str(music)]
        m = n
        filt.append(f"[{m}:a]aresample=44100,atrim=0:{total:.2f},volume=0.55,"
                    f"afade=t=out:st={max(0, total-1.2):.2f}:d=1.2[mus]")
        filt.append("[voice]asplit=2[vk][vmix]")
        filt.append("[mus][vk]sidechaincompress=threshold=0.03:ratio=9:attack=15:release=350[duck]")
        filt.append("[vmix][duck]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=9[aout]")
    else:
        filt.append("[voice]loudnorm=I=-14:TP=-1.5:LRA=9[aout]")
    audio = work / "audio.m4a"
    run(["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(filt), "-map", "[aout]",
         "-t", f"{total:.2f}", "-c:a", "aac", "-b:a", "192k", str(audio)])

    # 5) final
    out = Path(a.out) if a.out else work / f"{spec['id']}.mp4"
    subs = f"ass={ass.as_posix()}:fontsdir={FONTS.as_posix()}"
    run(["ffmpeg", "-y", "-i", str(base), "-i", str(audio), "-vf", subs, "-map", "0:v", "-map", "1:a",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
         "-c:a", "copy", "-movflags", "+faststart", "-t", f"{total:.2f}", str(out)])

    # 6) uso de planos para variar en días siguientes
    today = date.today().isoformat()
    for s, _, _ in plan:
        usage[s["id"]] = today
    usage_path.write_text(json.dumps(usage, indent=1))
    report = {"id": spec["id"], "out": str(out), "duration": round(total, 2),
              "voice_chars": sum(len(l["text"]) for l in spec["lines"]),
              "shots": [(s["id"], st, d) for s, st, d in plan],
              "timeline": [[round(x, 2), round(y, 2)] for x, y in timeline]}
    (work / "report.json").write_text(json.dumps(report, indent=1))
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
