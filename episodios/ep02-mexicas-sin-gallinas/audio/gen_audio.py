"""Voz del EP02: las dos voces con Chatterbox (nada de edge-tts) para que suenen naturales.

  ~/.chatterbox-py/Scripts/python.exe audio/gen_audio.py

Salidas (assets/): voz.wav, lines.json, mouth.json  (mismo formato que EP01)
"""
import json
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
VOCES = ROOT.parents[1] / "voces"
SR, FPS = 24000, 30
GAP, LEAD = 0.12, 0.12  # ritmo más rápido que EP01 (0.22)
REF = {"crono": VOCES / "ref_jorge.wav", "totola": VOCES / "muestras" / "02_MX_Dalia_mujer.mp3"}

# speaker, texto, exaggeration, cfg
SCRIPT = [
    ("crono", "¡Oye! ¡En todo Tenochtitlan no hay ni una sola gallina!", 0.9, 0.3),
    ("totola", "Claro que no. Las gallinas llegaron con los españoles.", 0.7, 0.4),
    ("crono", "¿Y entonces de dónde sacaban los huevos?", 0.6, 0.4),
    ("totola", "De mí, mi rey. En náhuatl, huevo se dice totoltetl: piedra de guajolota.", 0.75, 0.35),
    ("crono", "¿Piedra de guajolota? ¿En serio?", 0.8, 0.35),
    ("totola", "Y del lago sacaban huevos de un insecto de agua: el ahuautle.", 0.65, 0.4),
    ("crono", "¿Comían huevos de insecto?", 0.85, 0.3),
    ("totola", "Hoy le dicen caviar mexicano. Y el kilo cuesta unos cincuenta dólares.", 0.7, 0.4),
    ("crono", "¿Y qué dijeron los españoles cuando te vieron?", 0.55, 0.4),
    ("totola", "Me llamaron gallina de la tierra. ¡Gallina! ¡Qué falta de respeto!", 0.95, 0.3),
]


def trim(x, thresh=0.01):
    idx = np.where(np.abs(x) > thresh)[0]
    return x[max(idx[0] - 240, 0): idx[-1] + 480] if len(idx) else x


def normalize(x, peak=0.89):
    m = np.max(np.abs(x))
    return x * (peak / m) if m > 0 else x


def mouth_envelope(x):
    hop = SR // FPS
    n = int(np.ceil(len(x) / hop))
    rms = np.array([np.sqrt(np.mean(x[k * hop:(k + 1) * hop] ** 2) + 1e-12) for k in range(n)])
    ref = np.percentile(rms[rms > 0.005], 90) if np.any(rms > 0.005) else 1
    env = np.clip((rms - 0.012) / (ref - 0.012), 0, 1)
    return np.convolve(env, [0.25, 0.5, 0.25], mode="same")


def main():
    OUT.mkdir(exist_ok=True)
    import torch
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    torch.manual_seed(11)
    model = ChatterboxMultilingualTTS.from_pretrained(device="cuda" if torch.cuda.is_available() else "cpu")
    assert model.sr == SR, model.sr

    clips = []
    for i, (spk, text, exag, cfg) in enumerate(SCRIPT):
        wav = model.generate(text, language_id="es", audio_prompt_path=str(REF[spk]),
                             exaggeration=exag, cfg_weight=cfg).squeeze(0).cpu().numpy()
        clips.append((spk, text, normalize(trim(wav))))
        sf.write(ROOT / "audio" / "lines" / f"{i:02d}_{spk}.wav", clips[-1][2], SR)
        print(f"ok {i} {spk} {len(clips[-1][2]) / SR:.2f}s")

    total = LEAD + sum(len(c) / SR + GAP for _, _, c in clips)
    track = np.zeros(int(total * SR) + SR // 2, dtype="float32")
    nf = int(np.ceil(len(track) / (SR // FPS)))
    mouth = {"fps": FPS, "crono": [0.0] * nf, "totola": [0.0] * nf}
    lines, t = [], LEAD
    for i, (spk, text, c) in enumerate(clips):
        s = int(t * SR)
        track[s:s + len(c)] += c
        f0 = int(round(t * FPS))
        for k, v in enumerate(mouth_envelope(c)):
            if f0 + k < nf:
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
