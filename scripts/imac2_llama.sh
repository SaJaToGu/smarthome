#!/usr/bin/env bash
# SSH-Wrapper für iMac2 mit lokalen GGUF-Modellen
# Nutzt llama.cpp auf iMac2 für Offline/Cheap-Tasks

set -euo pipefail

MODEL="${1:-qwen2.5-coder-1.5b}"
PROMPT="${2:-Hello}"

ssh -o BatchMode=yes -o ConnectTimeout=8 -i ~/.ssh/metis_ed25519 Guido@192.168.178.43 "
  cd /Users/Guido/models
  /usr/local/bin/llama-cli \
    -m ${MODEL}.gguf \
    -p \"${PROMPT}\" \
    -n 64 \
    --temp 0.7 \
    2>/dev/null | head -20
"
