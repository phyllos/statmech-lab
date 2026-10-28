# 版本管理

[English](../en/git-workflow.md) · 简体中文 · [项目介绍](README.md)

**v0.1.0** 标记项目初始基线，对应 [版本说明](CHANGELOG.md) 的 v0.1.0 部分。`main` 包含已集成的改动；Unreleased／未发布列出尚未归入版本的变更。

## 开发流程

开发使用功能分支。每组改动从 `main` 创建分支：

```bash
git switch main
git switch -c feature/short-description
```

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

将 `<changed-files>` 替换为要提交的文件路径。切换分支前，先提交尚未完成的改动，或用 git stash 临时保存。

## 查看初版

```bash
git log --oneline --decorate
git show v0.1.0 --stat
git diff v0.1.0
```

版本标签标识固定源码快照，不随 `main` 的变化移动。每个发布版本使用独立标签。

源码、测试、`pyproject.toml` 和 `uv.lock` 纳入版本管理。虚拟环境、缓存、本地密钥及生成的 `figs/` 不纳入。使用 `uv sync --locked` 重建环境，使用 `uv run --locked python export_figures.py` 重新出图。

部署使用已审查的提交。版本标签标记阶段性成果；远端仓库或独立备份用于在单个工作目录之外保存这些版本。

## GitHub 与云端更新

远端仓库为 `https://github.com/phyllos/statmech-lab.git`。Community Cloud 需单独设置为跟随 `main`；只推送功能分支不会更新该部署。测试通过后合并到 `main` 并推送。`git push origin main` 只上传该分支，不会上传所有本地分支或标签。

发布验证后，同步更新 `pyproject.toml` 版本、用 `uv lock` 更新锁文件，将对应 Unreleased 说明归档到版本条目，并在发布提交上打标签。标签需单独推送。部署应用与发布版本标签是两个步骤。
