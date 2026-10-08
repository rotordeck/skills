# Rotordeck skills

[Agent Skills](https://agentskills.io) for FPV drones. Each skill is a folder under `skills/` with a `SKILL.md` (YAML frontmatter plus instructions) and optional supporting files. They work with Claude Code and any other agent that loads the Agent Skills format.

## Skills

| Skill | What it does |
|---|---|
| [`betaflight`](skills/betaflight/SKILL.md) | Configure Betaflight flight controllers: receiver and ports, modes, motors and ESC, PIDs, rates and filters, failsafe and GPS rescue, OSD, VTX, presets, backups, firmware, blackbox, and "why won't it arm?". Step-by-step procedures live in `workflows/`. |
| [`bf-cli`](skills/bf-cli/SKILL.md) | How to run and drive the [`bf`](https://github.com/rotordeck/bf) command line tool: npx, connecting to an FC or SITL, the JSON and exit-code contract, discovery, safe writes, streaming, troubleshooting. |

`betaflight` and `bf-cli` are companions: install both.

## Install

### Claude Code plugin

```sh
/plugin marketplace add rotordeck/skills
/plugin install betaflight@rotordeck-skills
```

### Copy the folders

```sh
git clone https://github.com/rotordeck/skills.git rotordeck-skills
mkdir -p ~/.claude/skills
cp -r rotordeck-skills/skills/* ~/.claude/skills/        # all skills, user-wide
# or per project: cp -r rotordeck-skills/skills/betaflight .claude/skills/
```

Other agents: copy the skill folders to wherever your agent discovers skills (e.g. `.github/skills/`, `.agents/skills/`).

## Layout

```text
skills/
└── <skill-name>/
    ├── SKILL.md       # required: frontmatter (name, description) + instructions
    ├── workflows/     # optional: procedures the skill points to
    ├── references/    # optional: docs read on demand
    ├── scripts/       # optional: helper scripts
    └── templates/     # optional: output templates
```

## Adding a skill

1. Create `skills/<name>/SKILL.md`. The frontmatter `name` must equal the folder name (lowercase kebab-case, ≤ 64 chars). The `description` (≤ 1024 chars) says what the skill does and when to use it.
2. Keep `SKILL.md` short; move detail into supporting files and reference them by relative path.
3. Run `bash scripts/validate-skills.sh`. CI runs it on every push and pull request.
4. Add the skill to the table above, and to `.claude-plugin/marketplace.json` if it belongs in a plugin.

## License

[AGPL-3.0-or-later](LICENSE).
