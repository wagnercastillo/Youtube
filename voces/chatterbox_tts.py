"""Chatterbox Multilingual TTS (GPU) — clona una voz de referencia y habla en español.

Uso:
  python chatterbox_tts.py "texto" salida.wav --ref voz_referencia.wav [--exag 0.5] [--cfg 0.5]

--ref    audio de ~10 s de la voz a clonar (wav/mp3). Sin --ref usa la voz por defecto.
--exag   0.25 = calmado, 0.5 = normal, 0.8+ = muy expresivo/dramático.
--cfg    ritmo: más bajo (0.3) = más pausado; con --exag alto conviene bajarlo.
"""
import argparse

import soundfile as sf
import torch
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

ap = argparse.ArgumentParser()
ap.add_argument("text")
ap.add_argument("out")
ap.add_argument("--ref")
ap.add_argument("--lang", default="es")
ap.add_argument("--exag", type=float, default=0.5)
ap.add_argument("--cfg", type=float, default=0.5)
a = ap.parse_args()

device = "cuda" if torch.cuda.is_available() else "cpu"
model = ChatterboxMultilingualTTS.from_pretrained(device=device)
wav = model.generate(
    a.text,
    language_id=a.lang,
    audio_prompt_path=a.ref,
    exaggeration=a.exag,
    cfg_weight=a.cfg,
)
# torchaudio>=2.9 needs torchcodec to save; soundfile is already installed
sf.write(a.out, wav.squeeze(0).cpu().numpy(), model.sr)
print(f"ok {a.out} ({wav.shape[-1] / model.sr:.1f}s, {device})")
