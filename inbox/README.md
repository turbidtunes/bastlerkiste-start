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

## Texture deliveries (Codex generates photo textures)

**Codex:** one folder `inbox/<set_name>_textures/` with the images `new_<motif>.png` and a `note.txt` (one line per file:
`new_<motif>.png | tile or atlas | real size in m | what it shows`). Push to `main`. Nothing else.

**Bastlerkiste worker:** `python3 map/textures/usertex.py <folder> --tile <motif>=<m>,…` (sizes from note.txt) puts them
into `map/textures/gpt/`, mapping.json and derive; then the assets waiting for the motif swap their placeholder
material (the brief that requested them, e.g. AUFTRAG_STREUGUT.md), one REVIEW line, `git rm -r` the folder here.
