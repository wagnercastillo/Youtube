"""Genera la voz del episodio: cada línea por separado, luego la pista completa.

Corre con el Python de Chatterbox (tiene torch, numpy, soundfile):
  ~/.chatterbox-py/Scripts/python.exe audio/gen_audio.py

Salidas (en assets/):
  voz.wav      pista de voz completa, 24 kHz mono
  lines.json   [{id, speaker, text, start, end}]
  mouth.json   {fps, neuro:[0..1 por frame], glia:[...]}  apertura de boca para lip sync
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
TMP = ROOT / "audio" / "lines"
VOCES = ROOT.parents[1] / "voces"
FFMPEG = next(Path.home().glob(
    "AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg*/ffmpeg-*/bin/ffmpeg.exe"))
EDGE = Path.home() / ".local/bin/edge-tts.exe"
SR, FPS = 24000, 30
GAP, LEAD = 0.22, 0.15  # silencio entre líneas / antes de la primera

# speaker, texto, (exaggeration, cfg) para Neuro
SCRIPT = [
    ("neuro", "¡¿Quién no sacó la basura anoche?!", (0.95, 0.3)),
    ("glia", "Tú, jefe. No dormiste… y la limpieza fuerte se hace de noche.", None),
    ("neuro", "¿Limpieza? ¿De qué basura hablas?", (0.6, 0.4)),
    ("glia", "La que dejan tus neuronas al trabajar. Una se llama beta amiloide.", None),
    ("neuro", "Eso suena… peligroso.", (0.55, 0.4)),
    ("glia", "En 2018, un estudio midió que una sola noche sin dormir la sube un cinco por ciento.", None),
    ("neuro", "Con razón hoy no encuentro ni las llaves…", (0.3, 0.5)),
    ("glia", "Entonces, jefe… ¿esta noche vas a dormir?", None),
]


def load_mono_24k(path):
    wav = TMP / (Path(path).stem + "_24k.wav")
    subprocess.run([str(FFMPEG), "-v", "error", "-y", "-i", str(path), "-ar", str(SR), "-ac", "1", str(wav)],
                   check=True)
    data, _ = sf.read(wav, dtype="float32")
    return data


def trim(x, thresh=0.01):
    idx = np.where(np.abs(x) > thresh)[0]
    return x[max(idx[0] - 240, 0): idx[-1] + 480] if len(idx) else x


def normalize(x, peak=0.89):  # ~ -1 dBFS
    m = np.max(np.abs(x))
    return x * (peak / m) if m > 0 else x


def edge_line(i, text):
    mp3 = TMP / f"{i:02d}_glia.mp3"
    for _ in range(4):  # edge-tts falla a veces sin error
        subprocess.run([str(EDGE), "-v", "es-MX-DaliaNeural", "--rate=+6%", "--pitch=+40Hz",
                        "-t", text, "--write-media", str(mp3)], capture_output=True)
        if mp3.exists() and mp3.stat().st_size > 0:
            return load_mono_24k(mp3)
    sys.exit(f"edge-tts falló en la línea {i}")


def mouth_envelope(x):
    """RMS por frame, normalizado y suavizado → 0..1."""
    hop = SR // FPS
    n = int(np.ceil(len(x) / hop))
    rms = np.array([np.sqrt(np.mean(x[k * hop:(k + 1) * hop] ** 2) + 1e-12) for k in range(n)])
    ref = np.percentile(rms[rms > 0.005], 90) if np.any(rms > 0.005) else 1
    env = np.clip((rms - 0.012) / (ref - 0.012), 0, 1)
    return np.convolve(env, [0.25, 0.5, 0.25], mode="same")


def main():
    TMP.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(exist_ok=True)
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS  # carga lenta, solo si hace falta
    import torch
    torch.manual_seed(7)  # misma actuación en cada regeneración
    model = ChatterboxMultilingualTTS.from_pretrained(device="cuda" if torch.cuda.is_available() else "cpu")
    assert model.sr == SR, model.sr

    clips = []
    for i, (spk, text, params) in enumerate(SCRIPT):
        if spk == "neuro":
            exag, cfg = params
            wav = model.generate(text, language_id="es", audio_prompt_path=str(VOCES / "ref_jorge.wav"),
                                 exaggeration=exag, cfg_weight=cfg).squeeze(0).cpu().numpy()
        else:
            wav = edge_line(i, text)
        clips.append((spk, text, normalize(trim(wav))))
        print(f"ok {i} {spk} {len(clips[-1][2]) / SR:.2f}s")

    total = LEAD + sum(len(c) / SR + GAP for _, _, c in clips)
    track = np.zeros(int(total * SR) + SR // 2, dtype="float32")
    mouth = {"fps": FPS, "neuro": [0.0] * int(np.ceil(len(track) / (SR // FPS))), "glia": None}
    mouth["glia"] = list(mouth["neuro"])
    lines, t = [], LEAD
    for i, (spk, text, c) in enumerate(clips):
        s = int(t * SR)
        track[s:s + len(c)] += c
        f0 = int(round(t * FPS))
        for k, v in enumerate(mouth_envelope(c)):
            if f0 + k < len(mouth[spk]):
                mouth[spk][f0 + k] = round(float(v), 3)
        lines.append({"id": f"l{i}", "speaker": spk, "text": text,
                      "start": round(t, 3), "end": round(t + len(c) / SR, 3)})
        t += len(c) / SR + GAP

    sf.write(OUT / "voz.wav", track, SR)
    (OUT / "lines.json").write_text(json.dumps(lines, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "mouth.json").write_text(json.dumps(mouth), encoding="utf-8")
    print(f"voz.wav {len(track) / SR:.2f}s, {len(lines)} líneas")


if __name__ == "__main__":
    main()
