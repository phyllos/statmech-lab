# Running and deploying / 运行与部署

The complete lab requires a Python/Streamlit server. Downloaded chart HTML files work independently, but do not include the app's Python calculations or parameter controls.

完整实验室需要 Python/Streamlit 服务。下载的单张 HTML 图可以独立使用，但不包含应用的 Python 计算与全部调参功能。

## Local use / 本地使用

From the repository root / 在项目根目录运行：

```bash
uv sync --locked
uv run --locked streamlit run app.py
```

The checked-in configuration binds to `127.0.0.1`. The browser URL is normally `http://localhost:8501`. Dependencies are fixed by `uv.lock`; the development environment includes pytest.

默认配置只监听本机地址 `127.0.0.1`，通常通过 `http://localhost:8501` 访问。`uv.lock` 锁定依赖，开发环境包含 pytest。

## Container / 容器

```bash
docker build -t statmech-lab:local .
docker run --rm --name statmech-lab -p 127.0.0.1:8501:8501 statmech-lab:local
```

The runtime uses a non-root user and a locked environment without development dependencies. The build context allows only required source files and dependency metadata; it excludes Git history, local environments, credentials, documents and generated figures. The container listens on `0.0.0.0:8501` internally; the example maps it to localhost on the host.

容器以非 root 用户运行，按锁文件安装运行依赖。构建上下文仅包含所需源码及依赖信息，不包含 Git 历史、本地环境、密钥、文档或生成图形。容器内部监听 `0.0.0.0:8501`；上述示例仅映射到宿主机本地端口。

```bash
docker inspect --format '{{.State.Health.Status}}' statmech-lab
docker logs statmech-lab
```

The health check uses `/_stcore/health` on port 8501. This checks server readiness, not scientific correctness; run the test suite separately before building.

健康检查使用 8501 端口的 `/_stcore/health`。它验证服务就绪，不代替科学计算和交互测试。

## Hosting direction / 托管方向

Start with one container instance on a host that supports long-lived WebSocket connections. Put the service behind the host's HTTPS endpoint or reverse proxy. Keep the internal port at 8501 and map the external port as needed. Preserve WebSocket upgrade handling and the app's default request protections.

初期可使用支持 WebSocket 长连接的单容器托管环境，由平台 HTTPS 入口或反向代理接入。内部端口保持 8501，外部端口按环境映射，并保留 WebSocket 转发和默认请求保护。

There is no database, account system or external API dependency. Session settings and comparisons reset when the session is replaced or the server restarts. If the app later needs saved experiments across devices, add an explicit export/import format or persistent store as a separate feature. Multiple replicas require session routing considerations because state is held by the serving process.

目前不依赖数据库、账号系统或外部 API。会话更换或服务重启会重置参数及对照。若以后需要跨设备保留实验，可单独增加导出／导入格式或持久化存储；多副本部署需要考虑会话路由，因为状态保留在服务进程中。

Deploy a reviewed commit or release tag. Python package versions are locked, while base-image tags can receive updates; record or pin image digests when a release needs an exactly repeatable OS image. No deployment credentials or hosting account are included in this repository.

部署选择经过审查的提交或版本标签。Python 包版本已经锁定；基础镜像标签可能更新，需要精确复现系统环境时应记录或固定镜像摘要。仓库不包含部署密钥或托管账号配置。

## References / 参考

- [Streamlit Docker deployment](https://docs.streamlit.io/deploy/tutorials/docker)
- [uv Docker integration](https://docs.astral.sh/uv/guides/integration/docker/)
