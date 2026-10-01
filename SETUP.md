# One-time setup

The settings a new repository needs that no file can carry, in order. Each step says what breaks
without it. About 20 minutes, once per project.

## 1. Before the first commit: keep your email private

- GitHub → Settings → Emails: tick **Keep my email addresses private** and **Block command line
  pushes that expose my email**. Note the `ID+USERNAME@users.noreply.github.com` address shown there.
- In the clone: `git config user.email "ID+USERNAME@users.noreply.github.com"` (this repository
  only, so other work keeps its own address).
- Check before pushing: `git log --format='%an <%ae>' | sort -u` shows only the noreply address.
- Never put an email in a file: the code of conduct sends reports to GitHub's private
  vulnerability form instead (step 3).

*Without it:* your address is in every commit, public forever. Rewriting history afterwards means
a force push and new commit ids.

## 2. Protect `main`

Settings → Rules → Rulesets → **New ruleset** → **Import a ruleset** → `.github/rulesets/main.json`.
It requires a pull request and the `ci-ok` check, forbids force pushes and deletion, and allows
squash merges only.

*Without it:* a direct push can put a red commit on `main`, and a tag on it releases it.

`ci-ok` must have run once before the ruleset can find it: push, let the `tests` workflow run,
then import.

## 3. Repository features

Settings → General:
- **Features**: tick Discussions (the issue forms send questions there).
- **Pull Requests**: tick *Allow squash merging* only, and *Automatically delete head branches*.

Settings → Code security: enable **Private vulnerability reporting** (the code of conduct and a
security report both go through it) and **Dependabot alerts**.

## 4. PyPI: trusted publishing, no token

On [pypi.org](https://pypi.org/manage/account/publishing/) → **Add a new pending publisher**:
project name = the package name, owner and repository = this one, workflow `release.yml`,
environment `pypi`. Do this before the first tag.

*Without it:* the first release builds everything, then fails on the `pypi` job
(`invalid-publisher`). Fix it here and re-run only that job.

## 5. GitHub Pages (skip if you deleted `web/` and `pages.yml`)

1. Settings → Pages → Source: **GitHub Actions**.
2. Settings → Environments → **github-pages** → Deployment branches and tags → **Add deployment
   branch or tag rule** → Tag, pattern `v*`.

*Without step 2:* the `pages` job fails with *Tag "v1.0.0" is not allowed to deploy to
github-pages due to environment protection rules*: the environment GitHub creates only accepts
`main`. Add the rule, then re-run the failed job.

## 6. Windows code signing (optional, later)

Unsigned, the Windows executable triggers SmartScreen, and Smart App Control blocks it. The
[SignPath Foundation](https://signpath.org/) signs open-source projects for free:

1. Apply with the repository URL; they review `CODE_SIGNING.md` (fill in its team table).
2. In SignPath: project slug = the package name, signing policy `release-signing`, artifact
   configuration: a single `.exe`.
3. Here: secret `SIGNPATH_API_TOKEN` and variable `SIGNPATH_ORGANIZATION_ID` (Settings → Secrets
   and variables → Actions). The next tag signs the executable; nothing else to change.

## 7. First release

Follow *Releasing* in the README. Then check: the release page has three executables, PyPI shows
the version, and the Pages URL loads and runs the example.

## Traps already hit once

| Symptom | Cause | Fix |
|---|---|---|
| `release` fails at *tag matches the version* | Tagged a commit that still has the old `__version__` (the bump sat on a branch) | Delete the tag (`git push origin :refs/tags/vX.Y.Z`), merge the bump, tag `main` |
| Pull request conflicts in `.github/workflows/` | Dependabot bumped action versions on `main` meanwhile | Merge `main` into the branch, keep your steps with the newer versions |
| The wheel contains old modules | A stale `build/` folder from a previous layout | Delete `build/` and `*.egg-info`, rebuild |
| `pages` rejected for a tag | Step 5.2 missing | Add the tag rule, re-run |
| `pypi` fails on the first tag | Step 4 missing, or the name is taken | Add the pending publisher, or rename |
| PyInstaller executable misses data files | A dependency ships non-Python files | `--collect-data PKG` in the matrix `extra` of `release.yml` |
