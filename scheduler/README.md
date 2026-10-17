# Commit scheduler

Automates small, real, roadmap-ordered commits to this repo: **2 or 3 a day, at
random times between 09:00 and 21:30 IST**, pushed by a GitHub Actions workflow
(`.github/workflows/auto-commit.yml`). No laptop needs to be on.

## How it works

- The workflow wakes up every 20 minutes and runs `scheduler/run.py`.
- The script derives today's plan from the date (2 or 3 random times, at least
  an hour apart). Every run on the same day sees the same plan.
- If a planned time has passed and its commit has not been made, it applies the
  next folder from `scheduler/queue/`, commits it, and pushes. Otherwise it exits.
- `scheduler/progress.json` records what has been applied and when. It is
  committed together with each step.
- Commit times are the real time of the run (within roughly 20 to 30 minutes
  after the planned time). Nothing is backdated.

## Queue format

```
scheduler/queue/012-some-step/
├── message.txt      # the commit message
└── files/           # copied over the repo root when the step runs
    └── src/....
```

Steps run in folder-name order. Add more by creating the next numbered folder.
When the queue is empty the scheduler does nothing; it never makes filler commits.

## Useful commands

```bash
python scheduler/run.py --plan                    # today's planned times
python scheduler/run.py --dry-run                 # what would happen right now
python scheduler/run.py --now 2026-10-19T14:05 --dry-run
python scheduler/run.py --force --push            # commit the next step now
```

You can also run the workflow by hand from the Actions tab; tick "force" to
commit the next step immediately.

## Settings

- **Commit identity**: defaults to your GitHub noreply address, so commits count
  on your contribution graph without exposing a personal email. Override with
  repository variables `COMMIT_NAME` and `COMMIT_EMAIL`.
- **Plan seed**: change `DEFAULT_SALT` in `run.py` to reshuffle the schedule.
- **Window and counts**: `COMMITS_PER_DAY`, `WINDOW_START`, `WINDOW_END`, `MIN_GAP`.

## Things to know

- Pushes made with the built-in `GITHUB_TOKEN` cannot modify files under
  `.github/workflows/`, so keep workflow edits out of queue steps.
- GitHub may delay scheduled workflows by several minutes under load, and
  disables scheduled workflows after 60 days without repository activity. The
  daily commits keep it active.
- The queue lives in this repo, so queued code is visible before it is
  committed. If you want the work to appear only as it lands, keep the queue in
  a private repo and check it out in the workflow.
