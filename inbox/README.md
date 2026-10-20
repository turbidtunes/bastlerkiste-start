# Inbox for ChatGPT / Codex deliveries

Codex (or the user) puts new deliveries here: building GLB/ZIP + texture tiles `new_<what>.png`, sheets, notes.
This repo is tiny, so Codex can clone it fast; the big project repo `turbidtunes/bastlerkiste` (40 GB) is not needed for
a delivery.

**Codex:** commit the files into `inbox/<building_name>/` (one folder per building: the model ZIP or GLB, the texture
tiles, a short `note.txt` with the building's use and wishes) and push to `main` (or open a PR the user merges).
Nothing else in this repo.

**Bastlerkiste worker:** at session start, after the slim clone, check this inbox first: copy every
`inbox/<name>/` into the project (`map/structures/<name>/src/` or per AUFTRAG_GPT_MODELLE.md), run the pipeline, push the
project, then `git rm -r inbox/<name>` here and push this repo.
