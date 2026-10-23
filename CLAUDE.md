# Bastlerkiste – session launcher

This repo is only the **starting point** for a Bastlerkiste worker. The real project is
`turbidtunes/bastlerkiste` (~40 GB with history, ~18 GB current state; the user's PC holds a full blobless clone) – too big for the session's automatic clone,
so the session starts here and clones the project **slim** itself. The user (Fabst) talks German; code comments and
prompts are English.

## First thing in every session (before anything else)

1. Add the project with push access: call the `add_repo` tool with owner `turbidtunes`, repo `bastlerkiste`,
   access `push` – but **do not run the clone command it suggests** (that would be a full clone and fill the disk).
2. Clone slim instead (blobless + sparse, ~5 MB + the folders you add):

```bash
git clone --filter=blob:none --no-checkout https://github.com/turbidtunes/bastlerkiste /home/claude/bastlerkiste
cd /home/claude/bastlerkiste
git sparse-checkout set --no-cone '/*.md' '/pipeline/' '/steer/' '/claims/' '/inbox/'
git checkout main
```

3. Call `register_repo_root` with owner `turbidtunes`, repo `bastlerkiste`, directory `/home/claude/bastlerkiste`.
4. **Deliveries first** (until milestone M2 only the Grand-Fond buildings, see the queue's inbox item): `inbox/` of THIS launcher repo (Codex pushes new buildings here, see inbox/README.md) and
   `inbox/` of the project. Process every delivery before the queue.
5. Read `/home/claude/bastlerkiste/PROJECT_STATUS.md` (the binding status page), then `steer/QUEUE.md`, and of
   `/home/claude/bastlerkiste/CLAUDE.md` only the sections Environment setup, Clone + repo diet and Git. Then work the
   **top open item tagged [any]** under the budget rules (items tagged [PC] need the user's PC, `steer/PC.md`).

## What else lives here (do not touch as a Claude worker)
`AGENTS.md`, `.github/workflows/`, `scripts/`, `prompts/`, `briefs/`, `texture_requests/`, `image_requests/`,
`references/`, `referenzbilder/`, `docs/` belong to the user's **Codex building factory** (Codex + GitHub Actions; the
build runs cost Anthropic API credits). Claude workers only read `inbox/` and remove processed deliveries from it.

## Rules
- Add the folders an item needs with `git sparse-checkout add '/<folder>/'` – never a full checkout, never
  `git ls-tree -l` over big trees (downloads every blob).
- Commit and push project work **in `/home/claude/bastlerkiste`** with `bash pipeline/push.sh` (to `main`). In this
  launcher repo only remove processed deliveries from `inbox/`.
- Only one worker at a time. Stop at the end of an item when the context gets long: push, write "next: …" into
  `steer/QUEUE.md`, end the session.
