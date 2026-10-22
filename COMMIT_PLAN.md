# Git commit plan: 3 people, one commit every ~40-60 min (event: 09:00 - 21:00)

Everyone commits from **their own laptop and their own GitHub account**, so the history shows all three of you working all day.

---

## A. One-time setup (do this first, ~15 min)

**1. Everyone: tell Git who you are** (use the email linked to YOUR GitHub):
```
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

**2. Aryan (leader): make the repo**
- GitHub -> New repository -> name `routewise` -> Public -> **don't** tick README -> Create.
- Repo -> Settings -> Collaborators -> add **Lakshya** and **Pallavi** (they must accept the email invite).

**3. Everyone: unzip `routewise.zip` into a folder called `routewise-source`**
This folder is your **parts box**. Keep it **outside** the git repo folder. You will copy only *your* files from it, at your time slot.

**4. Aryan, first push (empty repo):**
```
mkdir routewise
cd routewise
git init
git branch -M main
git remote add origin https://github.com/<aryan-username>/routewise.git
```
(then do Aryan's commit #1 below)

**5. Lakshya and Pallavi:** wait until Aryan's first push is done, then
```
git clone https://github.com/<aryan-username>/routewise.git
```
Open the `routewise` folder in VS Code.

---

## B. The 5-step routine for EVERY commit (same each time)

```
git pull --rebase                 # 1. get teammates' latest files
# 2. copy YOUR files for this commit from routewise-source into routewise (same folder paths!)
git add <files listed below>      # 3. stage only those files
git commit -m "<message below>"   # 4. save the snapshot
git push                          # 5. upload to GitHub (first time: git push -u origin main)
```
Rules: copy **only your own files**, so you never clash with a teammate. If `git push` says "rejected", just run `git pull --rebase` and `git push` again.
VS Code alternative: Source Control icon (left bar) -> `+` next to files -> type message -> Commit -> Sync Changes.

---

## C. Timeline (who commits what, when)

| Time | Who | Commit message | Files (copy + `git add`) |
|---|---|---|---|
| 11:00 | **Aryan** | `chore: project skeleton, README and requirements` | `.gitignore README.md COMMIT_PLAN.md backend/requirements.txt` |
| 11:40 | **Lakshya** | `feat(frontend): scaffold Vite + React + Tailwind app` | `frontend/package.json frontend/vite.config.ts frontend/tsconfig.json frontend/postcss.config.js frontend/tailwind.config.js frontend/index.html frontend/src/main.tsx` |
| 12:00 | **Pallavi** | `feat(backend): add route simulator and metrics` | `backend/app/evaluate.py` |
| 12:30 | **Aryan** | `feat(backend): add data models and Indore sample scenario` | `backend/app/models.py backend/app/sample_data.py` |
| 13:15 | **Lakshya** | `feat(frontend): add shared types and API client` | `frontend/src/types.ts frontend/src/api.ts` |
| 13:30 | **Pallavi** | `feat(baseline): add round-robin baseline solver` | `backend/app/baseline.py` |
| 14:00 | **Aryan** | `feat(backend): add distance matrix with OSRM fallback` | `backend/app/geo.py` |
| 14:30 | **Lakshya** | `feat(ui): add cartoon theme and original mascots` | `frontend/src/index.css frontend/src/mascots.ts` |
| 14:50 | **Pallavi** | `feat(ui): add sound effects with mute toggle` | `frontend/src/sfx.ts` |
| 15:15 | **Aryan** | `feat(optimizer): add OR-Tools VRPTW solver and cost weights` | `backend/app/objective.py backend/app/solver_ortools.py` |
| 15:45 | **Lakshya** | `feat(map): draw depot, orders and coloured agent routes` | `frontend/src/components/MapView.tsx` |
| 16:10 | **Pallavi** | `feat(ui): add baseline vs RouteWise comparison dashboard` | `frontend/src/components/Comparison.tsx` |
| 16:40 | **Aryan** | `feat(optimizer): add pure-Python fallback solver` | `backend/app/solver_heuristic.py` |
| 17:10 | **Lakshya** | `feat(ui): add agents panel and orders panel` | `frontend/src/components/AgentsPanel.tsx frontend/src/components/OrdersPanel.tsx` |
| 17:30 | **Pallavi** | `feat(ui): add Rooty helper and re-optimization log` | `frontend/src/components/Rooty.tsx frontend/src/components/EventLog.tsx` |
| 18:00 | **Aryan** | `feat(engine): live re-optimization for add/cancel/delay/reassign/agent events` | `backend/app/engine.py` |
| 18:20 | **Lakshya** | `feat(ui): add new-order form with map picking` | `frontend/src/components/AddOrderForm.tsx` |
| 18:45 | **Aryan** | `feat(api): add FastAPI endpoints` | `backend/app/main.py` |
| 19:10 | **Pallavi** | `test: add engine tests for dynamic events` | `backend/tests/test_engine.py` |
| 19:30 | **Lakshya** | `feat(app): connect everything in App with sounds and header` | `frontend/src/App.tsx` |
| 20:00 | **Everyone** | `docs/fix: <what you changed>` | see section E |

That is 8 commits for Aryan, 8 for Lakshya and 7 for Pallavi (including the final 20:00 slot). If you finish early, nothing breaks: the order above also keeps the repo in a sensible state (models before solver, solver before engine, engine before API).

> The app only runs fully once all parts are in. For the live demo, run it from your `routewise-source` folder (the complete copy), or from the repo after the 19:30 commit.

---

## D. Real work to run in parallel (so your commits are honest)

Each person should **run, read and tweak** their own area. Judges and mentors can ask questions.

- **Aryan:** run the backend, open http://localhost:8000/docs, try each endpoint. Tweak weights in `objective.py` (e.g. `W_LATE`) and see the plan change.
- **Lakshya:** run the frontend. Change a colour, a mascot name or a header text in your files. Test "pick location" and add an order.
- **Pallavi:** run `pytest`, try the demo, and note the baseline vs RouteWise numbers for the PPT. Add one more test.

---

## E. Final slot, 20:00 (everyone, one small commit each)

- **Aryan:** `docs: add API notes and how-to-run`: add a short section to `README.md`
- **Lakshya:** `fix(ui): final polish`: any small UI fix or text change
- **Pallavi:** `docs: add mentor speech guide` (`docs/MENTOR_SPEECH.md`; later add `docs/DEMO_SCRIPT.md` too)

Final check before 21:00: GitHub repo page shows 3 contributors, README renders, and the app runs from a fresh `git clone`.

---

## F. If something goes wrong

| Problem | Fix |
|---|---|
| `git push` rejected | `git pull --rebase` then `git push` |
| Asked for username/password | Use a **Personal Access Token** as password (GitHub -> Settings -> Developer settings -> Tokens), or sign in via the VS Code popup |
| "nothing to commit" | You forgot to copy the files into the repo folder, or didn't `git add` |
| Committed the wrong file | `git reset --soft HEAD~1`, fix, commit again (before pushing) |
| `node_modules` showing in Source Control | `.gitignore` is missing: Aryan's first commit adds it. `git pull --rebase` first |
