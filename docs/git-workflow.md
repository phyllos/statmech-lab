# Version control / 版本管理

**v0.1.0** identifies the initial project baseline on `main`. It includes all features described in the [release notes](../CHANGELOG.md).

**v0.1.0** 标记 `main` 上的项目初始基线，包含 [版本说明](../CHANGELOG.md) 中列出的完整功能。

## Explore safely / 开始新尝试

Keep `main` as the working baseline. Create a branch before trying new UI or interactions:

将 `main` 作为稳定基线；尝试新界面或交互前创建分支：

```bash
git switch main
git switch -c feature/short-description
```

Review and commit coherent changes after checking the app:

检查应用后，将一组完整改动提交：

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

将 `<changed-files>` 替换为要提交的文件路径。切换分支前，先提交尚未完成的改动，或用 git stash 临时保存。

## Inspect the baseline / 查看初版

```bash
git log --oneline --decorate
git show v0.1.0 --stat
git diff v0.1.0
```

The tag keeps this release reproducible as `main` moves forward. Preserve `v0.1.0`; use a new version tag for subsequent releases.

`main` 后续增加提交时，标签仍固定指向本次发布基线。保留 `v0.1.0`，后续发布使用新的版本标签。

Source, tests, `pyproject.toml`, and `uv.lock` are tracked. `.venv/`, caches, local secrets, and generated `figs/` are ignored. Recreate the environment with `uv sync --locked`, and figures with `uv run --locked python export_figures.py`.

源码、测试、`pyproject.toml` 和 `uv.lock` 纳入版本管理。虚拟环境、缓存、本地密钥及生成的 `figs/` 不纳入。使用 `uv sync --locked` 重建环境，使用 `uv run --locked python export_figures.py` 重新出图。

Use reviewed commits as deployment inputs. Version tags identify milestones; a remote repository or independent backup preserves them beyond one checkout.

部署使用已审查的提交。版本标签标记阶段性成果；远端仓库或独立备份用于在单个工作目录之外保存这些版本。


`.gitignore` excludes regenerable environments, caches, test/build output, local secrets and the `backups/` directory. Keep source, tests, configuration, example environment files and `uv.lock` tracked. Ignore rules do not remove already-tracked files and do not control Finder/ZIP folder compression.

`.gitignore` 排除可重建环境、缓存、测试／构建产物、本地密钥和 `backups/` 目录。源码、测试、配置、环境示例与 `uv.lock` 仍应纳入版本管理。忽略规则不会移除已跟踪文件，也不控制 Finder／ZIP 对文件夹的压缩。
