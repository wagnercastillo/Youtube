# REVIEW — EP01 "Tu cerebro sin dormir"

Render: `renders/ep01-cerebro-sin-dormir.mp4` — 1080×1920, 30 fps, 31.5 s, 20 MB.

## Creative calls
- Idea #1 of the "cuerpo humano" niche, chosen by me (the person delegated the choice). Thick-outline cartoon style, as requested.
- Cast: Neuro (Chatterbox, Jorge's cloned voice, emotion per line) and Glía, an astrocyte (a real star-shaped brain cell) as the cleaner (edge-tts Dalia, +40 Hz).
- Science kept honest: the human fact (one night without sleep → ~5% more beta-amyloid, Shokri-Kojori et al., PNAS 2018, 20 people) is cited on screen. "The brain cleans itself while you sleep" comes from mouse studies and is disputed (2024), so the script only says "la limpieza fuerte se hace de noche" and never claims a mechanism.
- No alternative storylines built (no-stops request).

## Measured vs. looked at
- `check`: ok. Snapshots at 0, 1.2, 3.5, 8.5, 9, 12.5, 14.5, 16.5, 17, 21.5, 23.2, 26.5, 30.5, 31.25 s, reviewed by eye.
- Audio measured, not heard: −13.2 LUFS integrated, true peak −1.1 dB, no clipping.
- Transcript matched the script word for word ("midio" → "midió" fixed in captions).

## Fixed after the first review
- Frame 0 (thumbnail) showed Neuro with a closed mouth → angry mood keeps the mouth open.
- Lip sync too subtle → larger mouth range.
- Arm angles hid the raised fists behind the brain.
- Cutaway: third neuron sat under the captions → moved up.

## Weakest points / next time
- No music: there's no source without a HeyGen sign-in. A light bed at ~0.14 under the voice would help.
- "BETA-AMILOIDE" sticker sits right above the caption with the same word (P2).
- Neuro's arms are simple sticks; hands could get fingers/fists.
- Line 4 ("Eso suena… peligroso.") has a 1.3 s pause from Chatterbox; it plays as a dramatic beat but could be trimmed.

## Warnings kept on purpose
- `rotation_pivot_drift` / `off_pivot_rotation`: Glía rotates about her feet on entry and the broom about the hand, intentionally.
- `composition_file_too_large` (stage.html ~390 lines): one stage keeps the shared character rig in one place.
