# Bastlerkiste – session launcher

This repo is only the **starting point** for a Bastlerkiste worker. The real project is
`turbidtunes/bastlerkiste` (~40 GB with history, 17.5 GB current state) – too big for the session's automatic clone,
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
4. Read `/home/claude/bastlerkiste/steer/QUEUE.md` and of `/home/claude/bastlerkiste/CLAUDE.md` only the sections
   Environment setup, Clone + repo diet and Git. Then work the **top open item** of the queue under its budget rules,
   then the next one.

## Rules
- Add the folders an item needs with `git sparse-checkout add '/<folder>/'` – never a full checkout, never
  `git ls-tree -l` over big trees (downloads every blob).
- Commit and push **in `/home/claude/bastlerkiste`** with `bash pipeline/push.sh` (to `main`). Never commit work into
  this launcher repo.
- Only one worker at a time. Stop at the end of an item when the context gets long: push, write "next: …" into
  `steer/QUEUE.md`, end the session.
