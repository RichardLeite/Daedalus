# Daedalus — Plano de Implementação v0.1

> Documento de trabalho. Fonte de verdade do escopo da v0.1.
> Documentação pública será em inglês; este plano fica em PT-BR para revisão.

## 1. Visão

Daedalus é uma configuração de desenvolvimento para OpenCode, pessoal e pública,
inspirada no `.workbench` mas sem processos, domínios ou credenciais empresariais.

O nome vem de Dédalo: inventor, arquiteto e artesão. O projeto entrega
**agentes, skills, comandos, regras e ferramentas** para desenvolvimento de
software, com instalação global e camada opcional por projeto.

## 2. Decisões fechadas

| Tema | Decisão |
|---|---|
| Agentes | 18–22 no core; 22 definidos |
| Processo | Engenharia + PO/BA/Scrum genéricos |
| Integração | GitHub apenas, via `gh` CLI |
| Ferramentas | OpenCode na v0.1; Claude Code/Codex na v0.2 |
| Linguagem | Python 3.11+ para CLI/tooling; TypeScript só para plugin futuro |
| Distribuição | Pacote instalável (`pipx`/`uv`) + `python -m daedalus` |
| Uso | Global + `/daedalus-init` por projeto |
| Memória | ai-memory, adiado para v0.2 |
| MCP | Nenhum MCP no core |
| Idioma | Inglês como fonte; PT-BR depois |
| Estilo | Caveman lite always-on |
| Multi-projeto | Global + projeto na v0.1; workspace cross-repo na v0.2 |

## 3. Escopo da v0.1

### Entra

- Core global instalável: `install --global`, `update --global`, `uninstall --global`.
- Camada de projeto: `daedalus init` + comando `/daedalus-init`.
- CLI: `doctor`, `validate`, `context`, `init`, `install`, `update`, `uninstall`.
- 22 agentes, ~24 skills, ~18 comandos, regras e templates.
- Config OpenCode V2 nativa.
- Caveman lite always-on via `AGENTS.md`.
- Integração GitHub via `gh`.
- Testes e CI matrix Linux/macOS/Windows.
- README mínimo em inglês.

### Fica para depois

- ai-memory (detecção, wiring, skill `memory`, `.ai-memory.toml`).
- Workspace cross-repo (`projects.json`, `references`).
- `daedalus sync claude|codex`.
- Plugin TS (métricas, guard-rails, references dinâmicas).
- Documentação completa e PT-BR.
- Agentes opcionais `arbiter`, `sec-arch`, `perf-auditor`.

## 4. Estrutura do repositório

```text
Daedalus/
├── README.md
├── LICENSE
├── PLAN.md
├── ROADMAP.md
├── AGENTS.md
├── CONVENTIONS.md
├── opencode.jsonc
├── pyproject.toml
├── .gitignore
├── .gitattributes
├── .editorconfig
├── .github/workflows/ci.yml
├── .opencode/
│   ├── agents/
│   ├── commands/
│   ├── skills/
│   ├── rules/
│   ├── templates/
│   └── profiles/
├── daedalus/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── paths.py
│   ├── jsonc.py
│   ├── manifest.py
│   ├── install.py
│   ├── init.py
│   ├── context.py
│   ├── doctor.py
│   ├── validate.py
│   └── templates/project/
├── tests/
└── docs/
```

O pacote Python fica na raiz para permitir `python -m daedalus` no clone.

## 5. Layout global instalado

Destino: `$XDG_CONFIG_HOME/opencode` ou `~/.config/opencode`.

```text
~/.config/opencode/
├── opencode.jsonc
├── AGENTS.md
├── agents/
├── commands/
├── skills/
├── rules/
├── templates/
├── profiles/
├── plugins/            # reservado para v0.2
└── .daedalus/
    ├── install.json
    └── backups/
```

### Instalação segura

1. Criar backup em `.daedalus/backups/<timestamp>/`.
2. Copiar apenas itens do core.
3. Anexar bloco gerenciado ao `AGENTS.md` existente.
4. Criar `opencode.jsonc` se não existir.
5. Se existir, não sobrescrever; oferecer `--merge-config`.
6. Registrar versão, source, target, arquivos, hashes e backups em `install.json`.
7. Nunca apagar arquivo fora do manifesto.

`--merge-config`:
- faz backup;
- adiciona `default_agent` se ausente;
- adiciona `instructions` de `CONVENTIONS.md` se ausente, convertendo o caminho
  relativo para absoluto no install global;
- insere permissões padrão no início, para regras do usuário vencerem.

### Update e uninstall

- `update`: atualiza arquivos cujo hash atual ainda é o instalado; conflitos são reportados.
- `uninstall`: remove arquivos do manifesto e restaura backups apenas se o hash atual bater; caso contrário, reporta conflito.

## 6. Camada de projeto

Criada por `daedalus init` / `/daedalus-init`.

```text
<project>/
├── AGENTS.md
└── .opencode/
    ├── opencode.jsonc
    ├── project.json
    ├── .daedalus.json
    ├── agents/
    ├── skills/
    ├── commands/
    └── knowledge/
        ├── README.md
        ├── decisions/
        ├── specs/
        └── plans/
```

### `project.json`

```json
{
  "version": 1,
  "name": "my-app",
  "profile": "backend",
  "stack": ["python", "postgres"],
  "created_at": "2026-11-11T00:00:00Z"
}
```

Sem `repos`, `workspace` ou memória na v0.1.

### Bloco gerenciado no `AGENTS.md`

```md
<!-- daedalus:begin v1 -->
## Project: my-app
- Stack: python, postgres
- Profile: backend
- Read `.opencode/knowledge/README.md` before implementing.
- Run `daedalus validate` before opening a PR.
<!-- daedalus:end -->
```

`--update` substitui apenas o bloco. `--force` só explícito.

### Perfis

`minimal`, `backend`, `frontend`, `fullstack`, `data`.

Cada perfil contém:
- `profile.json`;
- `AGENTS.block.md`;
- `gitignore.append`;
- opcionalmente `agents/`, `skills/`, `commands/`, `knowledge/`.

## 7. Precedência

| Elemento | Comportamento |
|---|---|
| `opencode.jsonc` do projeto | Mesclado depois do global; vence |
| `agents/*.md` com mesmo ID | Substitui o global (validado no CI) |
| `commands/*.md` com mesmo nome | Substitui o global |
| `skills/<id>/SKILL.md` | Projeto vence o global pelo ID |
| `instructions` | Combinadas |
| `permissions` | Concatenadas; última regra que casa vence |
| `mcp.servers` | Projeto sobrescreve; core vazio |
| `references` | Aditivas; não usadas na v0.1 |

## 8. Config V2 e validador

### Agentes

Aceita:
`description`, `mode`, `model`, `color`, `hidden`, `steps`.

Rejeita campos V1:
`temperature`, `permission`, `prompt`, `tools`, `disable`, `maxSteps`,
`skills`, `trigger`, `projects`.

Permissões centralizadas em `opencode.jsonc`:

```jsonc
{
  "agents": {
    "code-reviewer": {
      "permissions": [
        { "action": "edit", "resource": "*", "effect": "deny" },
        { "action": "shell", "resource": "*", "effect": "deny" }
      ]
    }
  }
}
```

### Skills

`SKILL.md` com `name` e `description`; opcional
`metadata.opencode/autoinvoke: false`.

### Comandos

Frontmatter: `description`, `agent`, `model`, `subagent`.
Corpo é o template. `template` no frontmatter é erro.

### Config

Aceita:
`agents`, `commands`, `plugins`, `permissions`, `mcp.servers`, `references`,
`instructions`, `default_agent`, `model`, `skills`.

Rejeita:
`agent`, `permission`, `mcp` sem `servers`, `plugin`, `reference`.

### Validações extras

- IDs de agente únicos e consistentes com `opencode.jsonc`.
- Skills referenciadas existem.
- Nenhum path absoluto de máquina.
- Nenhum segredo óbvio.
- `opencode.jsonc` parseável.

## 9. Inventário

### Agentes (22)

`orchestrator`, `backend-dev`, `frontend-dev`, `database-dev`, `tdd-guide`,
`implementer`, `code-reviewer`, `security-reviewer`, `architect`, `tech-lead`,
`debugger`, `pr-reviewer`, `explorer`, `ux-analyzer`, `image-analyzer`,
`devops-engineer`, `qa-engineer`, `business-analyst`, `product-manager`,
`scrum-master`, `planner`, `token-manager`.

### Skills (~24)

`code-review`, `architecture-review`, `bugfix`, `feature`, `commit`, `pr`,
`planning-analysis`, `planning-setup`, `complex-task-planner`, `repo-scan`,
`qa-test`, `api-testing`, `e2e-testing`, `performance`, `observability`,
`db-migrations`, `deployment`, `release-management`, `security-audit-api`,
`security-audit-database`, `property-testing`, `mutation-testing`,
`skill-creator`, `find-skills`.

### Comandos (~18)

`/plan`, `/feature`, `/bug`, `/adr`, `/spec`, `/review`, `/review-all`,
`/pipeline`, `/execute-spec`, `/commit`, `/pr`, `/release`, `/refine`,
`/docs`, `/handoff`, `/new-project`, `/daedalus-init`, `/daedalus-context`.

### Regras

`constitution`, `decision-tree`, `token-policy`, `style`.

## 10. CLI

| Comando | Função |
|---|---|
| `daedalus install --global` | Copia o core para o config global |
| `daedalus update --global` | Atualiza arquivos gerenciados |
| `daedalus uninstall --global` | Remove o que foi instalado |
| `daedalus init` | Cria a camada do projeto |
| `daedalus context --json` | Contexto para o orquestrador |
| `daedalus doctor` | Diagnóstico de ambiente |
| `daedalus validate` | Valida agentes, skills, comandos e config |

Flags comuns: `--dry-run`, `--yes`, `--force`, `--source`, `--dir`, `--json`.

Exit codes:
- `0` sucesso;
- `1` erro de validação/execução;
- `2` uso incorreto;
- `3` conflito.

## 11. Multi-plataforma

- `pathlib.Path` em todo o código.
- `encoding="utf-8"` explícito.
- `sys.executable` para subprocessos.
- `shutil.which` para detectar `git` e `gh`.
- Sem symlink na v0.1.
- `.gitattributes` com `* text=auto`, `*.py eol=lf`, `*.sh eol=lf`, `*.cmd eol=crlf`.
- Testes com `tmp_path`.
- Sem dependência de `/tmp` ou `C:\`.
- CI matrix Linux/macOS/Windows.

## 12. Testes e CI

Matrix:
- `ubuntu-latest`, `macos-latest`, `windows-latest`;
- Python 3.11, 3.12, 3.13.

Checks:
- `ruff check`
- `ruff format --check`
- `pytest`
- `python -m daedalus validate --root .`
- Integração: install global em HOME temporário, init em repo git temporário,
  validate, update, uninstall.
- Path safety, JSONC, manifest, backups, colisões, idempotência.
- Sem rede.

## 13. Critérios de aceite

- `pipx install -e .` funciona nos três SOs.
- `daedalus install --global --dry-run` não escreve.
- Instalação repetida é idempotente.
- `daedalus init --plan` não escreve.
- `daedalus init` não sobrescreve arquivos do usuário.
- `daedalus validate` rejeita config V1.
- `daedalus doctor` explica o que falta sem alterar nada.
- Projeto inicializado carrega `orchestrator` e overrides no OpenCode.

## 14. Riscos e mitigação

| Risco | Mitigação |
|---|---|
| Precedência de agente por ID no V2 não confirmada | Teste de integração no CI |
| `opencode.jsonc` existente com comentários | Não sobrescrever por padrão; `--merge-config` com backup |
| Windows sem `python` no PATH | Documentar `py -3` e usar `sys.executable` |
| Skills com comandos Unix | Revisão cross-platform e uso de `gh`/Python |
| Config global do usuário colidir | Manifest, backup, `--force` explícito |
| Duplicação com ai-memory no futuro | v0.2 define a integração; v0.1 não cria vault |

## 15. Roadmap

Ver `ROADMAP.md` para o checklist executável.

## 16. Instaladores one-liner

### Linux, macOS e WSL2

```bash
curl -fsSL https://raw.githubusercontent.com/RichardLeite/Daedalus/main/install.sh | bash
```

### Windows nativo

```powershell
iex (irm https://raw.githubusercontent.com/RichardLeite/Daedalus/main/install.ps1)
```

### Comportamento

1. Instala o OpenCode quando ausente:
   - Windows: `winget` com o pacote `Anomaly.OpenCode`;
   - Linux, macOS e WSL2: script oficial `https://opencode.ai/v2/install`.
2. Detecta Git; usa clone raso. Sem Git, baixa o archive `.tar.gz`/`.zip`.
3. Instala em `~/.local/share/daedalus` ou `%LOCALAPPDATA%\Daedalus`.
4. Instala `uv` e Python 3.11 quando necessário.
5. Instala a CLI com `uv tool install -e`.
6. Executa `daedalus install --global --merge-config`.

### Fallbacks do OpenCode no Windows

1. `winget install --id Anomaly.OpenCode`.
2. Git Bash + instalador oficial.
3. `npm install -g @opencode/cli@latest`.
4. `mise use -g opencode`.

### Opções

`--dry-run`, `--yes`, `--no-global`, `--no-merge-config`, `--skip-opencode`,
`--ref`, `--dir`, `--uninstall`; equivalentes em PowerShell com `-`.

### Segurança

- Sem `sudo` e sem admin.
- Backup do `opencode.jsonc` antes do merge.
- `--dry-run`/`-DryRun` não altera arquivos.
- Scripts são arquivos versionados no repo; o usuário pode lê-los antes de
  executar.
- `--ref` permite fixar uma tag em vez de seguir `main`.

## 17. CI/CD e release

### CI

- Matrix Python 3.11, 3.12 e 3.13 em Linux, macOS e Windows.
- Lint, format, testes e `daedalus validate`.
- Job separado de instaladores nas três plataformas com `--source .`,
  `--skip-opencode`, `--no-global` e `--no-shell`.
- O job de instaladores executa o install global em diretório temporário e
  valida com `daedalus validate --global`.

### Release

Disparado por tag `v*` ou manualmente.

1. Verifica lint, testes e config.
2. Confere se a versão da tag bate com `pyproject.toml`.
3. Gera:
   - wheel;
   - sdist;
   - tarball completo do repositório (`git archive`);
   - `SHA256SUMS`.
4. Sobe os artefatos como artifacts do workflow.
5. Cria ou atualiza a GitHub Release com os arquivos e notas geradas.

Fluxo:

```bash
git tag v0.1.0
git push origin v0.1.0
```
