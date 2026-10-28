# 运行与部署

[English](../en/deployment.md) · 简体中文 · [项目介绍](README.md)

完整实验室需要 Python/Streamlit 服务。下载的单张 HTML 图可以独立使用，但不包含应用的 Python 计算与全部调参功能。

## 本地使用

项目使用 Python 3.12 进行本地开发与部署。`.python-version` 指定 uv 的解释器版本，`pyproject.toml` 声明兼容范围，Docker 使用 Python 3.12。Community Cloud 需在 Advanced settings 中单独选择 Python 3.12。本地验证以该版本为基准。

在项目根目录运行：

```bash
uv sync --locked
uv run --locked streamlit run app.py --server.address=127.0.0.1
```

上述命令只监听本机。仓库配置不固定监听地址，交给启动环境设置，便于云端运行。`uv.lock` 锁定依赖，开发环境包含 pytest 与 Ruff。

## Streamlit Community Cloud

直接从 GitHub 仓库部署，不构建 Dockerfile。根目录保留 `pyproject.toml` 与 `uv.lock`；平台优先识别 `uv.lock`，无需另行维护 `requirements.txt`。当前交互应用不需要系统依赖清单或 Secrets。

1. 登录 [share.streamlit.io](https://share.streamlit.io/) 并授权访问仓库。
2. 从现有仓库创建应用，填写下表。
3. 高级设置选择 Python 3.12，Secrets 留空。
4. 部署并检查安装与启动日志。
5. 验证应用后，再设置分享权限。

| 设置 | 取值 |
| --- | --- |
| 仓库 | `phyllos/statmech-lab` |
| 分支 | `main` |
| 入口 | `app.py` |
| Python 版本 | `3.12` |
| 地址 | 选择未占用的 `streamlit.app` 子域名 |

仓库与应用的可见性是两个设置。私有仓库也可提供公开应用；在云端分享设置中确认访问范围。平台会自行管理部分配置，详见官方限制说明。

## 验证与更新

上传新改动前，在项目根目录执行：

```bash
uv sync --locked
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked pytest -q
```

上线后按 [手动界面清单](architecture.md#手动界面检查) 验证四个实验、术语表、语言切换、调参、抽样、保留对照和下载；检查窄屏、矮屏及 SVG 图题。若应用应公开，用独立的未登录浏览器会话核对访问权限。本地测试通过不等于云端和视觉效果已经验证。

平台跟随已部署 GitHub 分支更新。完成审查后提交并推送 `main`，线上才会更新；仅修改本地文件不会影响线上。依赖变化会触发环境安装。需要回退时，回退对应提交并推送，保留共享历史。

```bash
git status
git log -1 --oneline
git push origin main
```

闲置应用可能休眠，课堂演示前提前打开。会话状态是临时数据，新会话或服务重启可能重置参数。发布记录包含部署提交与验证结果，每个发布版本使用独立标签。

## 容器

```bash
docker build -t statmech-lab:local .
docker run --rm --name statmech-lab -p 127.0.0.1:8501:8501 statmech-lab:local
```

容器以非 root 用户运行，按锁文件安装运行依赖。构建上下文仅包含所需源码及依赖信息，不包含 Git 历史、本地环境、密钥、文档或生成图形。容器内部监听 `0.0.0.0:8501`；上述示例仅映射到宿主机本地端口。

```bash
docker inspect --format '{{.State.Health.Status}}' statmech-lab
docker logs statmech-lab
```

健康检查使用 8501 端口的 `/_stcore/health`。它验证服务就绪，不代替科学计算和交互测试。

## 其他容器托管

容器按单实例部署到支持 WebSocket 长连接的托管环境，由平台 HTTPS 入口或反向代理接入。内部端口为 8501，外部端口按环境映射；代理需保留 WebSocket 转发和默认请求保护。

应用不依赖数据库、账号系统或外部 API。实验参数与对照属于会话状态，会话更换或服务重启时重置。跨设备持久保存实验需要独立的存储或导出／导入机制；多副本部署需要会话路由，因为状态保留在服务进程中。

部署选择经过审查的提交或版本标签。Python 包版本已经锁定；基础镜像标签可能更新，需要精确复现系统环境时应记录或固定镜像摘要。仓库不包含部署密钥或托管账号配置。

## 参考

- [Community Cloud 部署设置](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)
- [Community Cloud 依赖文件优先级](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies)
- [Community Cloud 分享设置](https://docs.streamlit.io/deploy/streamlit-community-cloud/share-your-app)
- [Community Cloud 状态与配置限制](https://docs.streamlit.io/deploy/streamlit-community-cloud/status)
- [Community Cloud 管理与休眠](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app)
- [Streamlit Docker 部署](https://docs.streamlit.io/deploy/tutorials/docker)
- [uv Docker 集成](https://docs.astral.sh/uv/guides/integration/docker/)
