# Running and deploying

English · [简体中文](../zh-CN/deployment.md) · [Project overview](../../README.md)

The complete lab requires a Python/Streamlit server. Downloaded chart HTML files work independently, but do not include the app's Python calculations or parameter controls.

## Local use

The project uses Python 3.12 for local development and deployment. `.python-version` specifies the interpreter version for uv, and `pyproject.toml` declares the compatibility range. Docker uses Python 3.12. Community Cloud requires a separate Python 3.12 selection in Advanced settings. Local validation targets this version.

From the repository root:

```bash
uv sync --locked
uv run --locked streamlit run app.py --server.address=127.0.0.1
```

The command binds only to localhost. The checked-in configuration leaves the address to the launch environment so it also works with hosting platforms. Dependencies are fixed by `uv.lock`; the development environment includes pytest and Ruff.

## Streamlit Community Cloud

Deploy the GitHub repository directly; this route does not build the Dockerfile. Keep `pyproject.toml` and `uv.lock` together at the repository root. Community Cloud recognizes `uv.lock` before other dependency files, so do not maintain a competing `requirements.txt`. No system package file or secrets are currently required by the interactive app.

1. Sign in at [share.streamlit.io](https://share.streamlit.io/) and authorize repository access.
2. Create an app from the existing repository using the settings below.
3. Select Python 3.12 in Advanced settings; leave Secrets empty.
4. Deploy and inspect the build/startup logs.
5. Verify the app, then choose its sharing visibility.

| Setting | Value |
| --- | --- |
| Repository | `phyllos/statmech-lab` |
| Branch | `main` |
| Main file path | `app.py` |
| Python version | `3.12` |
| App URL | Choose an available `streamlit.app` subdomain |

Repository visibility and app visibility are separate settings. A private repository can serve a public app; verify the intended audience in the cloud sharing settings. Community Cloud manages some configuration values itself, as listed in its status/limitations documentation.

## Verify and update

Before uploading changes, run from the project root:

```bash
uv sync --locked
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked pytest -q
```

After deployment, follow the [manual UI checklist](architecture.md#manual-ui-checks): visit all four experiments and the glossary, switch languages, change parameters, resample, retain a comparison and download a chart. Check narrow/short screens and SVG titles as well. Verify sharing from a separate signed-out browser session if the app should be public. Passing local tests does not establish cloud or visual correctness.

Community Cloud updates when the deployed GitHub branch changes. Commit reviewed changes and push `main` to update the app; local edits alone have no effect. Dependency changes trigger environment installation. If a deployed change fails, revert the relevant commit and push the revert rather than rewriting shared history.

```bash
git status
git log -1 --oneline
git push origin main
```

Community Cloud may put idle apps to sleep; open the app before a scheduled demonstration. Session state is temporary and can reset after a new session or server restart. Release records include the deployed commit and validation results; each release uses a distinct version tag.

## Container

```bash
docker build -t statmech-lab:local .
docker run --rm --name statmech-lab -p 127.0.0.1:8501:8501 statmech-lab:local
```

The runtime uses a non-root user and a locked environment without development dependencies. The build context allows only required source files and dependency metadata; it excludes Git history, local environments, credentials, documents and generated figures. The container listens on `0.0.0.0:8501` internally; the example maps it to localhost on the host.

```bash
docker inspect --format '{{.State.Health.Status}}' statmech-lab
docker logs statmech-lab
```

The health check uses `/_stcore/health` on port 8501. This checks server readiness, not scientific correctness; run the test suite separately before building.

## Other container hosts

The container runs as a single instance on a host with long-lived WebSocket support. HTTPS is provided by the hosting endpoint or a reverse proxy. The internal port is 8501; external port mapping depends on the host. Proxies must preserve WebSocket upgrade handling and the app's default request protections.

The app has no database, account system or external API dependency. Experiment settings and comparisons are session-local and reset when the session is replaced or the server restarts. Persistent experiments across devices require a separate storage or export/import mechanism. Multiple replicas require session routing because state is held by the serving process.

Deploy a reviewed commit or release tag. Python package versions are locked, while base-image tags can receive updates; record or pin image digests when a release needs an exactly repeatable OS image. No deployment credentials or hosting account are included in this repository.

## References

- [Community Cloud deployment settings](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)
- [Community Cloud dependency file precedence](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies)
- [Community Cloud sharing](https://docs.streamlit.io/deploy/streamlit-community-cloud/share-your-app)
- [Community Cloud status and configuration limitations](https://docs.streamlit.io/deploy/streamlit-community-cloud/status)
- [Community Cloud management and hibernation](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app)
- [Streamlit Docker deployment](https://docs.streamlit.io/deploy/tutorials/docker)
- [uv Docker integration](https://docs.astral.sh/uv/guides/integration/docker/)
