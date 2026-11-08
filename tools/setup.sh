#!/bin/bash
# One-time setup per session: TTS engine + Turkish voice. Fonts are in tools/fonts.
set -e
pip install --break-system-packages -q "sherpa-onnx==1.13.8" soundfile pillow
M=${MT_MODELS:-/home/claude/tts/sherpa}
mkdir -p "$M"; cd "$M"
V=${MT_VOICE:-fahrettin}
if [ ! -d vits-piper-tr_TR-$V-medium ]; then
  curl -sSL -o $V.tar.bz2 https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-tr_TR-$V-medium.tar.bz2
  tar xjf $V.tar.bz2 && rm $V.tar.bz2
fi
echo "setup ok: voice $V in $M"
