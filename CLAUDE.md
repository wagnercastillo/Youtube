# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Production repo for **Puro Chisme**, a Spanish-language YouTube Shorts channel (history and curiosities told as gossip),
channel `@PuroChismeAnimado`. Each episode is a 45–65 s vertical video (1080×1920, 30 fps) built from code: script → AI voices
→ animation → captions → render → API upload. The owner lives in Ecuador; the audience is Mexico/LatAm.

## Layout

- `episodios/epNN-slug/` — one self-contained project per episode (HyperFrames project: `index.html`, `compositions/`,
  `assets/`, `audio/` scripts, `renders/`). `SPEC.md` = creative spec, `ESTADO.md` = state, pipeline and upload metadata,
  `REVIEW.md` = review notes. Read the latest episode's `ESTADO.md` before starting a new one.
- `marca/` — brand: logo (`puro-chisme.svg`, `-800.png`), banner (`_banner.html` → `puro-chisme-banner.png` via headless Chrome),
  watermark, the name/logo options page (`logos.html`).
- `research/yt_niches.py` — finds fast-growing young channels per niche with YouTube Data API v3
  (`python yt_niches.py "historia animada" "datos curiosos" --shorts --region MX`; key in `research/.env`; `--selftest`).
- `ideas/IDEAS.md` — topic bank and the reel formula (hook ≤1.5 s, payoff, loop ending). Every fact must be verified before scripting.
- `.env` (root) holds `ELEVENLABS_API_KEY`; the episode scripts search parent folders for it.

## Episode pipeline (EP04 is the most complete reference)

Python environments: `~/.chatterbox-py/Scripts/python.exe` (numpy, soundfile, librosa) for voice and casting scripts;
`~/.manim-py/Scripts/manim.exe` for Manim; system `python -I` for the stdlib-only scripts.

1. Voices — `audio/design_voices.py` designs ElevenLabs voices by description (ids saved in `audio/voices.json`);
   `audio/audition.py` (EP04) designs ~9 candidates and ranks them by pitch variance, dynamics, speed and brightness.
2. Dialogue — `audio/gen_audio_el.py`: `SCRIPT` holds `(id, speaker, text with [audio tags])`; calls
   `/v1/text-to-speech/{voice}/with-timestamps` with `eleven_v3`, caches responses in `audio/el/` (delete a file to regenerate
   a line), writes `assets/voz.wav`, `assets/lines.json`, `assets/mouth.json` and word-level `transcript.json`.
   Use `mp3_44100_128` (decoded) — `pcm_24000` sounds dull and `pcm_44100` is refused on this plan.
3. Music/SFX — `audio/gen_music_sfx.py` (Eleven Music `/v1/music`, Sound Effects `/v1/sound-generation`), cached in `assets/`.
4. Visuals — either a HyperFrames stage with SVG character rigs (`compositions/stage.html`, EP02/EP03: moods keyed by time,
   camera re-frame per line, mouth driven by `mouth.json` injected between `/*DATA-START*/…/*DATA-END*/`) or Manim
   (`manim/script.py`, EP04: `cd manim && ~/.manim-py/Scripts/manim.exe script.py EP04`, copy
   `media/videos/script/1920p30/EP04.mp4` to `assets/manim.mp4`, which `index.html` plays muted).
   EP04 binds every cue to a word with `W(line, word)` / `L(line)` read from `transcript.json`, so a new voice re-syncs by itself.
5. Captions/assembly — `python -I audio/build.py` writes `compositions/captions.html` (word-highlight captions at y≈1530)
   and injects mouth data; EP04 also has `audio/build_index.py`, which writes `index.html` with word-anchored SFX and music.
6. Check and render — `npx hyperframes check`, `npx hyperframes snapshot --at 1,5,9` (look at the frames),
   `npm run render` (pinned `hyperframes@0.9.17`). The render lands as `renders/<slug>_<timestamp>.mp4`; rename it to
   `renders/<slug>.mp4`.
7. Verify — transcribe the voice (`npx hyperframes transcribe voz.wav -l es -d <dir>`) and compare with the script;
   regenerate any line that slipped (v3 stability 0.0 sometimes swallows words). Measure loudness with
   `ffmpeg -i x.mp4 -af volumedetect -vn -f null -`.

## Upload

`~/.claude/skills/youtube-uploader/scripts` (OAuth token already authorized for the channel account). On Windows the npx shim
drops arguments after a multi-line or accented value, so keep metadata in files in the episode folder:

```bash
cd ~/.claude/skills/youtube-uploader/scripts
npx ts-node youtube-upload.ts --video <mp4> --title "<title>" --description-file <ep>/youtube_description.txt --category 27 --privacy public
npx ts-node update-video.ts <videoId> <ep>/youtube_description.txt 27 public <ep>/youtube_tags.txt   # fix/complete metadata
npx ts-node check-video.ts <videoId>                                                                  # verify privacy, tags, category
```

**Publishing schedule (owner rule, 2026-11-06): 3 Shorts per day, every day including Saturday and Sunday (same slots)**, scheduled with `publishAt` (upload private, then
`update-video.ts <id> <desc> 27 <ISO time>`), at fixed slots in Mexico City time (UTC−6, no DST), ≥4 h apart so each Short
gets its own evaluation window:
- 12:00 pm CDMX = 18:00Z (1:00 pm Ecuador): lunch break
- 4:00 pm CDMX = 22:00Z (5:00 pm Ecuador): after school/work
- 8:00 pm CDMX = 02:00Z next day (9:00 pm Ecuador): evening peak — put the strongest video of the day here
Fill the next free slot. Re-check Studio → Analytics → "When your viewers are on YouTube" once the channel has data and
move the slots to the real peaks. The VPN must be off when uploading (TLS gets intercepted). Custom thumbnails need the
channel's intermediate features; until then the owner sets `renders/miniatura.jpg` by hand.

## Channel rules (from the owner — apply to every episode)

**Always the same (brand):** history/curiosities told as gossip; a big question hook on screen from frame 0; the word-highlight
caption style; the Puro Chisme end card (logo with peeking eyes, "PURO CHISME", "¿A poco no sabías este chisme?",
"SÍGUENOS PARA MÁS"); a cheeky gossip tone; facts verified with sources shown on screen or in the description.

**Always different:** no two videos alike — change the format (cartoon characters / real paintings / Manim explainer, max 3),
the structure (dialogue, narrator, quiz…), the cast, the voices and the look. Compare with previous episodes' `SPEC.md` first.

**Never:** "line boil" filters or constant shake (shake only as a ≤0.5 s burst on a mood change); quiet music (mix Eleven Music
≈12 dB under the voice, louder under the end card); flat narrators (Mexican-Spanish native voices; foreign accents sounded
"robotic" to the owner); free-plan ElevenLabs audio in a monetized video (EP01/EP02 audio must be regenerated before applying
to the Partner Program).

**Motion graphics (every episode):**
1. Reveal text through a mask (clip-path/mask wipe), not a plain fade.
2. Chain movements: each element starts as the previous one settles (overlap ~0.1–0.2 s, follow-through), never all at once.
3. The camera follows what matters: re-frame/dolly onto whoever talks or the key object.
4. Transform an object to introduce the next scene (match cut / morph: a coin becomes a planet, a map becomes a face).
5. Sync entrances with the narration: every entrance anchored to a word with `W(line, word)`, no hand-typed times.
