# Upstream provenance and integration gate

On 2026-10-11, omaSearch HEAD resolved to `a002289c04dff552fd9c73ef2bd7d7be838ca271`; GitHub identifies its license as MIT. The Markdown formatter in ui/Markdown.js was adapted from AskModel.js at that revision. The bounded subprocess design informed backend/runner.py. MIT notices for omaSearch/omAsk are retained in THIRD_PARTY_NOTICES.md; Omarchy overlay lifecycle attribution is also retained. Spotlight code was not copied.

Current upstream README and ask.py show agent command execution, external session imports, and auxiliary title-generation requests. Do not reuse these behaviors. Explicit Q&A-only controls must replace them; safe-mode/read-only-agent settings alone are insufficient.

Spotlight remains a visual reference. No Spotlight code is authorized for reuse. Installed Omarchy example licensing must also be checked before copying any clone source into this repository.

Sources: https://github.com/5h3rd1l/omaSearch and https://github.com/maajix/omarchy-spotlight .
