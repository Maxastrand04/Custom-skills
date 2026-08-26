# Getting the transcript

Reached from step 2 of [`SKILL.md`](SKILL.md) when a lecture video link is in play. Two tiers: take the captions if they are usable, transcribe locally if they are not.

Transcripts are cached at `Lecture-notes/.transcripts/<deck-filename>.srt`. Check there first. A cache hit skips this file entirely, which matters because tier 2 takes minutes.

## Preflight

```bash
for t in yt-dlp ffmpeg whisper-cli; do command -v $t >/dev/null || echo "missing: $t"; done
```

Everything missing is installed by one command:

```bash
brew install yt-dlp ffmpeg whisper-cpp
```

Never install it silently. Print the command, say what each tool is for, and let the user run it.

Without `yt-dlp` there is no video branch at all. Say so, drop to the deck-only path, and keep going. A missing transcript costs coverage; it does not fail the run.

## Tier 1: captions

Cheap and instant. Most university uploads have something.

```bash
mkdir -p "<CourseRoot>/Lecture-notes/.transcripts"
yt-dlp --write-subs --write-auto-subs --sub-langs "sv,en" --skip-download \
  --convert-subs srt -o "<CourseRoot>/Lecture-notes/.transcripts/<deck-filename>.%(ext)s" "<URL>"
```

Manual subtitles beat auto-captions when both land. Prefer the one without `.auto` in its name.

**Is it usable?** Auto-captions mangle exactly the words that matter, since a technical term is the least predictable thing in the audio. Sample about 40 lines and look for the deck's own vocabulary. If the deck's key terms come through recognizably, tier 1 is good enough. If they arrive as phonetic mush, drop to tier 2.

Swedish auto-captions are the usual reason to drop. YouTube's Swedish model is much weaker than its English one, and KB-Whisper below exists precisely because of that gap.

## Tier 2: local transcription

Used when there are no captions, or tier 1 failed its check.

**Pick the model by lecture language.** KB-Whisper is fine-tuned on 50,000 hours of Swedish and cuts word error rate roughly in half against `whisper-large-v3` on Swedish audio. That tuning is what makes it the wrong choice for an English lecture.

| Lecture language | Model | Fetch |
|---|---|---|
| Swedish | `kb-whisper-large-q5_0.bin` (~1.1 GB) | `https://huggingface.co/KBLab/kb-whisper-large/resolve/main/ggml-model-q5_0.bin` |
| English | `ggml-large-v3-turbo-q5_0.bin` (~574 MB) | `https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo-q5_0.bin` |

Cache models in `~/.cache/whisper/`, download only on a miss:

```bash
mkdir -p ~/.cache/whisper
curl -L --progress-bar -o ~/.cache/whisper/kb-whisper-large-q5_0.bin \
  "https://huggingface.co/KBLab/kb-whisper-large/resolve/main/ggml-model-q5_0.bin"
```

Then pull the audio and transcribe. `whisper.cpp` only accepts 16 kHz mono WAV, so the `ffmpeg` step is not optional:

```bash
cd "<CourseRoot>/Lecture-notes/.transcripts"
yt-dlp -x --audio-format wav -o "raw.%(ext)s" "<URL>"
ffmpeg -y -i raw.wav -ar 16000 -ac 1 -c:a pcm_s16le audio16.wav
whisper-cli -m ~/.cache/whisper/<model>.bin -f audio16.wav -l <sv|en> -np -osrt -of "<deck-filename>"
rm -f raw.wav audio16.wav
```

Run this in the background and keep reading the deck while it works. An hour of lecture takes a few minutes on Apple silicon, where `whisper.cpp` gets Metal acceleration.

Always set `-l`. It does not default to auto-detect, it defaults to `en`, so a Swedish lecture left unflagged gets transcribed as though it were English for the full hour. Pass `auto` deliberately if the language is genuinely unknown, but a lecture that opens with an English greeting before switching to Swedish will still be detected wrong.

`-np` keeps the timing dump out of the output. `-fa` is already on by default, so there is no reason to pass it.

## Using it

The `.srt` carries timestamps. They become the `[🎙 mm:ss]` tags, so keep them attached as the transcript is read rather than flattening it to plain text.

**The deck spells the terminology, not the transcript.** A technical term is the least predictable word in the audio, so it is the first thing any transcript gets wrong, and this survives tier 2, where a good model still returns "each envelopes" for "eigenvalues". Read every domain term in the transcript against the deck's own vocabulary and correct it there. A mangled term copied into the notes is worse than a gap, because it looks like a real word and gets revised from.

Match the transcript to the deck by content, not by clock time. A lecturer spends nine minutes on slide 3 and twenty seconds on slide 4, so timestamps do not divide evenly across slides.

The transcript adds what the slides left out. It does not overrule them: where the two disagree, the deck is what the lecturer chose to publish. Note the disagreement in Open questions.

A transcript does not retire `[fill]`. Lecturers skip things too, and the gaps that remain are still filled and still tagged.
