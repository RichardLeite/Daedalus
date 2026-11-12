# Daedalus — Roadmap v0.1

> Checklist executável. Marcar `[x]` ao concluir cada item.
> Escopo detalhado em `PLAN.md`.

## Legenda

- `[ ]` pendente
- `[~]` em andamento
- `[x]` concluído
- `[!]` bloqueado

## Fase 0 — Planejamento

- [x] Analisar o `.workbench` e separar core / processo / domínio
- [x] Definir escopo da v0.1 com o usuário
- [x] Fechar decisões de agentes, integração, linguagem e distribuição
- [x] Definir arquitetura global + projeto
- [x] Registrar plano em `PLAN.md`
- [x] Registrar roadmap em `ROADMAP.md`

## Fase 1 — Scaffold do repositório

- [x] Criar `pyproject.toml` (Python 3.11+, sem dependências runtime, CLI `daedalus`)
- [x] Criar `.gitignore`
- [x] Criar `.gitattributes`
- [x] Criar `.editorconfig`
- [x] Criar `README.md` mínimo em inglês
- [x] Criar `AGENTS.md` global com regras e Caveman lite
- [x] Criar `CONVENTIONS.md`
- [x] Criar `opencode.jsonc` V2 com `default_agent: orchestrator`
- [x] Criar `daedalus/__init__.py`
- [x] Criar `daedalus/__main__.py`
- [x] Criar `daedalus/cli.py` com argparse e `--version`
- [x] Criar estrutura `tests/`
- [x] Validar `python -m daedalus --help`

## Fase 2 — Base do CLI

- [x] `daedalus/paths.py`: config global, XDG, source root, path safety
- [x] `daedalus/jsonc.py`: parser/escritor JSONC mínimo com testes
- [x] `daedalus/manifest.py`: leitura/escrita de `install.json` e `.daedalus.json`
- [x] `daedalus/doctor.py`: checks de Python, git, gh, OpenCode, install, projeto
- [x] `daedalus/validate.py`: validação de agentes, skills, comandos, config V2
- [x] `daedalus/cli.py`: subcomandos `doctor`, `validate`, `context`
- [x] Testes unitários de paths, JSONC, manifest e validate
- [x] `daedalus validate --root .` roda no próprio repo

## Fase 3 — Instalação global

- [x] `daedalus/install.py`: plano de instalação (`--dry-run`)
- [x] Cópia segura de `agents/`, `commands/`, `skills/`, `rules/`, `templates/`, `profiles/`
- [x] Backup automático em `.daedalus/backups/<timestamp>/`
- [x] Manifesto `install.json` com versão, source, target, arquivos e hashes
- [x] Bloco gerenciado no `AGENTS.md` global
- [x] Criação de `opencode.jsonc` quando ausente
- [x] `--merge-config` com backup
- [x] `daedalus update --global`
- [x] `daedalus uninstall --global` com restauração de backup
- [x] Idempotência e detecção de conflito
- [x] Testes de instalação em HOME temporário (Linux/macOS/Windows)

## Fase 4 — Agentes V2

- [x] `orchestrator`
- [x] `backend-dev`
- [x] `frontend-dev`
- [x] `database-dev`
- [x] `tdd-guide`
- [x] `implementer`
- [x] `code-reviewer`
- [x] `security-reviewer`
- [x] `architect`
- [x] `tech-lead`
- [x] `debugger`
- [x] `pr-reviewer`
- [x] `explorer`
- [x] `ux-analyzer`
- [x] `image-analyzer`
- [x] `devops-engineer`
- [x] `qa-engineer`
- [x] `business-analyst`
- [x] `product-manager`
- [x] `scrum-master`
- [x] `planner`
- [x] `token-manager`
- [x] Permissões centralizadas em `opencode.jsonc`
- [x] Remover referências empresariais e campos V1
- [x] Teste de IDs únicos e consistência com config

## Fase 5 — Skills, comandos e regras

- [x] `rules/constitution.md`
- [x] `rules/decision-tree.md`
- [x] `rules/token-policy.md`
- [x] `rules/style.md`
- [x] Skills de review: `code-review`, `architecture-review`, `security-audit-api`, `security-audit-database`
- [x] Skills de dev: `bugfix`, `feature`, `commit`, `pr`
- [x] Skills de planejamento: `planning-analysis`, `planning-setup`, `complex-task-planner`
- [x] Skills de teste: `qa-test`, `api-testing`, `e2e-testing`, `property-testing`, `mutation-testing`
- [x] Skills de infra: `performance`, `observability`, `db-migrations`, `deployment`, `release-management`
- [x] Skills de meta: `skill-creator`, `find-skills`, `repo-scan`
- [x] Comandos core (19)
- [x] Templates: ADR, spec, feature, bug, issue, PR
- [x] Revisão cross-platform (sem `sed`, `grep`, `find`, `xargs`)
- [x] `daedalus validate` sem erros

## Fase 6 — Init de projeto e perfis

- [x] `daedalus/templates/project/`
- [x] `daedalus/init.py`: detecção de git root e stack
- [x] `daedalus init --plan`
- [x] Criação de `.opencode/opencode.jsonc`
- [x] Criação de `.opencode/project.json`
- [x] Criação de `.opencode/.daedalus.json`
- [x] Criação de `.opencode/knowledge/`
- [x] Bloco gerenciado no `AGENTS.md`
- [x] Ajuste de `.gitignore`
- [x] `--profile` com `minimal`, `backend`, `frontend`, `fullstack`, `data`
- [x] `--update` com detecção de conflito
- [x] `--force` explícito
- [x] Testes de init idempotente e não destrutivo

## Fase 7 — Comandos `/daedalus-init` e `/daedalus-context`

- [x] `.opencode/commands/daedalus-init.md`
- [x] `.opencode/commands/daedalus-context.md`
- [x] `daedalus/context.py` com saída JSON
- [x] `context` lê `project.json`, git, stack, install global
- [x] `orchestrator` usa `daedalus context` quando disponível
- [x] Fallback para leitura direta de `AGENTS.md`/`project.json`

## Fase 8 — Testes, CI e README

- [x] `.github/workflows/ci.yml` com matrix Linux/macOS/Windows
- [x] Python 3.11, 3.12, 3.13
- [x] `ruff check` e `ruff format --check`
- [x] `pytest`
- [x] `python -m daedalus validate --root .`
- [x] Teste de integração install → init → validate → update → uninstall
- [x] README mínimo com instalação, init, doctor, validate
- [x] Revisão de segurança: nenhum segredo, path absoluto ou nome empresarial
- [x] Instalação como ferramenta validada com `uv tool install -e .`

## Fase 9 — Release v0.1.0

- [x] Atualizar versão em `pyproject.toml` e `daedalus/__init__.py`
- [x] Revisar `PLAN.md` e `ROADMAP.md`
- [x] Workflow de release no GitHub Actions
- [x] Build de wheel e sdist via `python -m build`
- [x] Build do tarball completo do repositório via `git archive`
- [x] Geração de `SHA256SUMS`
- [x] Upload dos artefatos no workflow
- [x] Publicação automática da release ao empurrar tag `v*`
- [ ] CI verde nos três SOs
- [ ] Criar tag `v0.1.0`
- [ ] Publicar release no GitHub
- [ ] Registrar limitações conhecidas

## Fase 10 — Instaladores one-liner

- [x] `install.sh` para Linux, macOS e WSL2
- [x] `install.ps1` para Windows nativo
- [x] Instalação automática do OpenCode no Unix via script oficial
- [x] Instalação automática do OpenCode no Windows via winget (`Anomaly.OpenCode`)
- [x] Fallbacks do OpenCode no Windows: Git Bash, npm e mise
- [x] Detecção de Git com fallback para archive `.tar.gz`/`.zip`
- [x] Bootstrap de `uv` e Python 3.11 quando ausentes
- [x] Instalação da CLI em diretório de dados do usuário
- [x] Execução automática de `daedalus install --global --merge-config`
- [x] Opções `--dry-run`, `--yes`, `--no-global`, `--no-merge-config`, `--skip-opencode`, `--no-shell`, `--source`, `--ref`, `--dir`, `--uninstall`
- [x] Help e validação de sintaxe nos testes
- [x] CI job de instaladores em Linux, macOS e Windows
- [x] README com quick install e opções
- [ ] Push para o GitHub para ativar as URLs raw
- [ ] Teste E2E do one-liner a partir do GitHub público

## Pós-v0.1 (v0.2+)

- [ ] Integração ai-memory (detecção, wiring, skill `memory`, `.ai-memory.toml`)
- [ ] Workspace cross-repo (`projects.json`, `references`, `daedalus workspace`)
- [ ] `daedalus sync claude|codex`
- [ ] Plugin TS (métricas, guard-rails, references dinâmicas)
- [ ] Documentação completa e PT-BR
- [ ] Agentes opcionais `arbiter`, `sec-arch`, `perf-auditor`

## Log de progresso

| Data | Fase | Observação |
|---|---|---|
| 2026-11-11 | 0 | Plano e roadmap criados |
| 2026-11-11 | 1 | Scaffold, pacote Python e CLI base |
| 2026-11-11 | 2 | Paths, JSONC, manifest, doctor, validate e context |
| 2026-11-11 | 3 | Install, update e uninstall globais com manifest e backups |
| 2026-11-11 | 4 | 22 agentes V2 e permissões centralizadas |
| 2026-11-11 | 5 | 24 skills, 19 comandos, regras e templates |
| 2026-11-11 | 6 | Init de projeto, perfis e estado gerenciado |
| 2026-11-11 | 7 | Comandos `/daedalus-init` e `/daedalus-context` |
| 2026-11-11 | 8 | 51 testes, CI matrix, README e validação de segurança |
| 2026-11-11 | 8 | Teste completo pós-restart: lint, testes, E2E, build e merge simulado |
| 2026-11-11 | 8 | Install global real aplicado com `--merge-config`; 91 arquivos; backup criado |
| 2026-11-11 | 8 | Pós-restart: projeto externo detecta global, init+validate+doctor OK |
| 2026-11-12 | 10 | Instaladores one-liner `install.sh` e `install.ps1` com dry-run e testes |
| 2026-11-12 | 10 | OpenCode auto-install: winget no Windows; script oficial no Unix |
| 2026-11-12 | 10 | Validado `winget Anomaly.OpenCode` (OpenCode CLI 2.2.7) |
| 2026-11-12 | 9 | Workflow de release: wheel, sdist, source tar.gz, SHA256SUMS e GitHub Release |
| 2026-11-12 | 9 | Job de CI dos instaladores em Linux, macOS e Windows |
