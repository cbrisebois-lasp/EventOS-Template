---
name: create-skill
description: How to create a new skill — structure, conventions, and rules for writing SKILL.md files
user-invocable: true
---

# Creating a New Skill

Use this skill when creating a new skill for the project. Skills are markdown files that provide agents with focused context for a specific type of task.

## What a skill is

A skill is a `SKILL.md` file in its own directory under `.claude/skills/`. When an agent loads a skill, the file's contents become part of the agent's context. Skills are instructional — they tell the agent what to do and how to do it. They do not execute anything themselves.

## Directory structure

```
.claude/skills/<skill-name>/
    SKILL.md
```

The directory name is the skill's invocation name (e.g. `.claude/skills/run-tests/` is invoked as `/run-tests`).

## SKILL.md format

Every skill file has two parts: frontmatter and body.

### Frontmatter

```yaml
---
name: <skill-name>
description: <one-line description of what the skill helps with>
user-invocable: true
---
```

- `name` must match the directory name
- `description` is what the skill selector reads to decide relevance — be specific
- `user-invocable` should be `true` unless the skill is only loaded programmatically

### Body

The body is markdown. Structure it for an agent audience — concise, scannable, action-oriented. Common sections:

1. **Title and purpose** — one paragraph explaining when to use the skill
2. **MCP tools** — table of relevant tools with parameters (see rules below)
3. **Procedures or rules** — step-by-step instructions, constraints, or decision logic
4. **Fallbacks** — alternative approaches if MCP tools are unavailable
5. **Examples** — concrete examples where they aid understanding

Not every skill needs every section. Use what fits.

## Rules

### Reference MCP tools by name

Skills should list the MCP tools that are relevant to the task. Present them in a table with the tool name, parameters, and purpose so the agent knows exactly what to call.

```markdown
## MCP tools

| Goal | MCP Tool | Parameters |
|------|----------|------------|
| Build the app | `build_app` | — |
| Run tests for a module | `run_tests` | `module` (e.g. `"sample"`) |
```

A skill may reference any number of tools. Include every tool the agent might need for the task the skill covers — don't force the agent to guess or load a second skill.

### Tool names must match

Tool names in the skill must exactly match the `name` field in the server's `tools.py`. If a tool is renamed in the server, update every skill that references it.

### Write for agents, not humans

- Be direct and imperative: "Run `build_app` before running tests" not "You might want to build first"
- Use tables for structured information (tools, parameters, naming conventions)
- Keep prose to a minimum — agents extract instructions, not narrative
- Include concrete parameter examples: `module` (e.g. `"sample"`) not just `module`

### One concern per skill

Each skill covers one type of task. If a skill is growing to cover two unrelated workflows, split it. An agent can load multiple skills.

### Don't duplicate other skills

If a skill needs context from another skill, reference it by name rather than repeating the content. For example: "The container must be running — see `/use-container` if it needs to be started."

## After creating the skill

1. **Add to `CLAUDE.md` skill catalog** — add a row to the table in the `## Skill Catalog` section
2. **Add to skill selector** — add a row to the table in `.claude/skills/skill-selector/SKILL.md` with the trigger condition
3. **Verify** — invoke the skill with `/skill-name` to confirm it loads correctly

## Checklist

- [ ] Directory created: `.claude/skills/<skill-name>/SKILL.md`
- [ ] Frontmatter: `name`, `description`, `user-invocable` set correctly
- [ ] MCP tools listed by exact name with parameters
- [ ] Written for agent audience (concise, scannable, tables for structure)
- [ ] Added to `CLAUDE.md` skill catalog
- [ ] Added to `.claude/skills/skill-selector/SKILL.md`
