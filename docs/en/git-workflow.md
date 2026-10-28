# Version control

English · [简体中文](../zh-CN/git-workflow.md) · [Project overview](../../README.md)

**v0.1.0** identifies the initial project baseline. Its scope is recorded in the v0.1.0 section of the [release notes](../../CHANGELOG.md). `main` contains integrated changes, and Unreleased lists changes not yet assigned to a release.

## Development workflow

Development takes place on feature branches. Create a branch from `main` for each change:

```bash
git switch main
git switch -c feature/short-description
```

Review and commit coherent changes after checking the app:

```bash
git status
git diff
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked pytest -q
git add <changed-files>
git diff --cached
git commit -m "Describe the change"
```

Replace `<changed-files>` with the paths you intend to commit. Commit or stash unfinished work before switching branches.

## Inspect the baseline

```bash
git log --oneline --decorate
git show v0.1.0 --stat
git diff v0.1.0
```

Version tags identify fixed source snapshots independently of changes to `main`. Each release uses a distinct tag.

Source, tests, `pyproject.toml`, and `uv.lock` are tracked. `.venv/`, caches, local secrets, and generated `figs/` are ignored. Recreate the environment with `uv sync --locked`, and figures with `uv run --locked python export_figures.py`.

Use reviewed commits as deployment inputs. Version tags identify milestones; a remote repository or independent backup preserves them beyond one checkout.

## GitHub and cloud updates

The remote repository is `https://github.com/phyllos/statmech-lab.git`. Community Cloud is configured separately to follow `main`; pushing a feature branch does not update that deployment. Merge tested changes into `main`, then push. `git push origin main` uploads the branch, not all local branches or tags.

After a release has been verified, update the version in `pyproject.toml`, refresh `uv.lock` with `uv lock`, move the relevant Unreleased notes into a versioned section, and tag that release commit. Push the version tag explicitly. Hosting the app and publishing a version tag are separate steps.
