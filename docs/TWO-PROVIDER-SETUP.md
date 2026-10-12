# Focused setup: ChatGPT subscription and LM Studio

The current pair is direct ChatGPT Q&A plus the user's already loaded LM Studio model. Claude and Codex CLI execution remain blocked. Other provider expansion and all live inference tests remain pending.

## Verified setup — 2026-10-11

- Direct app ChatGPT sign-in completed and credentials were saved successfully on VM333. Authenticated catalog discovery returned seven models. This verifies account and catalog access, not inference.
- Workstation LM Studio at `http://127.0.0.1:1234` reports `gemma-4-e4b-it-ultra-uncensored-heretic`, Q4_K_M, as loaded. The VM adapter offers exactly that loaded model and its selection has been saved. Unloaded models are not offered.
- VM333's loopback port 1234 forwards over SSH to workstation loopback port 1234. Inference would run on the workstation, not in the VM. The app's Local label means this user-owned local setup, not necessarily the VM itself. LM Studio was not exposed on a LAN interface.
- The tunnel is temporary and does not survive workstation reboot. If it ends, discovery fails visibly; there is no fallback. Keep LM Studio running and the model loaded.
- No generation, latency, answer-quality or streaming test has been run. Ordinary file/app search continues through the existing local search implementation; this model only handles explicit AI questions and has no app-provided tools.

## Model choice

Use the existing E4B Heretic first. A smaller candidate is Gemma 4 E2B IT Heretic Q4_K_M, but its owner-approved download was paused before completion when priority moved to jcode. It has not been imported, loaded or benchmarked. Do not resume without owner approval. Heretic describes a model modification, not training specifically for Spotlight search. Fast app/file matching should remain deterministic. Any later task-specific prompt or fine-tuning needs an evaluation set before claiming an improvement. No model downloads or swaps are needed for this setup.

Sources: [loaded model's publisher](https://huggingface.co/llmfan46/gemma-4-E4B-it-ultra-uncensored-heretic-GGUF), [smaller candidate](https://huggingface.co/mradermacher/gemma-4-E2B-it-heretic-GGUF), [LM Studio model-state API](https://lmstudio.ai/docs/developer/rest/endpoints). Existing user-owned weights remain outside the repository; this change redistributes no model or runtime.

## Lab tunnel lifecycle

A dedicated temporary SSH key is restricted on VM333 to forwarding, with remote listen permission only for `127.0.0.1:1234`, no usable local-forward target, and a forced false command. It cannot open an interactive shell. Existing authorized keys were preserved. The workstation control directory is recorded in `/tmp/model-search-lmstudio-tunnel-path`; private key material stays outside the repository and diagnostics.

Stop from the workstation:

```sh
tunnel_dir=$(cat /tmp/model-search-lmstudio-tunnel-path)
ssh -S "$tunnel_dir/control" -O exit mp@10.0.0.210
```

To restart during this lab session, use the same existing control directory and key:

```sh
ssh -M -S "$tunnel_dir/control" -fNT -i "$tunnel_dir/key" \
  -o IdentitiesOnly=yes -o BatchMode=yes -o ExitOnForwardFailure=yes \
  -o ServerAliveInterval=30 -o ServerAliveCountMax=3 \
  -R 127.0.0.1:1234:127.0.0.1:1234 mp@10.0.0.210
```

For complete cleanup, stop the tunnel, remove only the dedicated `model-search-lmstudio-lab` entry from VM333's `~/.ssh/authorized_keys`, then remove that temporary control directory and pointer file. Plugin removal does not manage this separate test connection. No daily-desktop plugin was installed.

## Superseded llama.cpp setup

Before LM Studio was selected, an official llama.cpp b11429 CPU runtime and Qwen3 0.6B Q8_0 model were installed only on VM333, after snapshot `model-search-prelocal-20261011`. Both checksums were verified and licenses retained. The user service `model-search-llamacpp.service` is now stopped and disabled. Its files remain inert under `~/.local/share/model-search-runtime/` and `~/.config/systemd/user/`. It is not the selected local route and must not be restarted automatically. No Ollama installation occurred.
