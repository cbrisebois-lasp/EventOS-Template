---
name: version-control
description: Rules for branching, rebasing, and committing changes in this repository
user-invocable: true
---

# Version Control

This skill defines the version control workflow for TP-GSE. The [Rules](#rules) section defines how branching, committing, and messaging must be done. The [Collaborative workflow](#collaborative-workflow) section defines how the agent and user work together during development, referencing the rules when performing version control tasks.

## Rules

### Branch naming

- **Lower-case, dash-separated** strings describing the subject of the change (e.g. `route-rework`, `hal-timer-fix`, `add-logging-tests`).

### Branching strategy

- All changes MUST be made on a separate branch off `main`. Never commit directly to `main`.
- Before opening a PR or finalizing work, **rebase the branch against `main`** (`git rebase main`).
- When pushing a rebased branch, always use `git push --force-with-lease`. Never use `--force`.

### Commit strategy

The goal is one logical unit per commit so that reviewers can follow changes file-by-file.

#### Modified (pre-existing) files

- **One commit per file**, unless the changes are interdependent (e.g. a header and its source file), in which case they may share a commit.
- **Commit in dependency order** so the repo builds at each step, regardless of the order changes were made during development.

#### New or deleted files

- New and deleted files may be **batched into one commit per directory**.
- For example, three new files added under `app/source/route/` can share a single commit, but a new file in `app/source/route/` and another in `test/source/route/` require separate commits (different directories).

### Commit messages

Every commit message has three parts: a **subject line**, a **description**, and an **Agent trailer**.

#### Subject line

A single sentence that completes the statement _"If pushed, this commit will..."_. Write it in imperative mood, lowercase after the first word is acceptable, and keep it under 72 characters.

Examples:
- `Add multi-hop routing support to Route.c`
- `Fix sign-comparison warning in CmdSetRoute.c`
- `Add new test fixtures for hal/comip`

#### Description

A brief paragraph (max 200 characters) on the next line after a blank line. It should give additional context about _why_ the change was made or _how_ it works — details that aren't obvious from the diff alone.

#### Agent trailer

End every commit message with a single trailer line recording AI assistance and the model(s) used:

Example:
- `Agent: claude-opus-4-6`

If multiple models were used, comma-separate them (e.g. `Agent: claude-opus-4-6, claude-sonnet-4-6`).

#### Full example

```
Add multi-hop routing support to Route.c

Enable packets to traverse intermediate nodes by chaining SpW addresses
in the route table. Needed for the new ground network topology.

Agent: claude-opus-4-6
```

## Collaborative workflow

The default workflow when the agent and user are working together. The agent should **never commit without the user's approval**.

### Making changes

1. The agent makes changes as requested.
2. The agent presents the changes for review (a brief summary of what was changed and why is sufficient — the user can inspect the diff themselves).
3. The user reviews and either approves or requests revisions.
4. If revisions are requested, the agent edits and re-presents. Repeat until approved.
5. Once approved, the user asks the agent to commit. The agent commits per the [Rules](#rules).

### Revising uncommitted changes

Simply edit the file and re-present for review. No special git handling needed.

### Revising already-committed changes

When the user requests a change to a file that has already been committed on the branch, the modification must be folded back into the original commit to maintain one-commit-per-file history.

Use the **fixup/autosquash** pattern:

```bash
# 1. Stash uncommitted work if any exists
git stash

# 2. Stage the revised file and create a fixup commit targeting the original
git add <file>
git commit --fixup=<original-sha>

# 3. Non-interactive autosquash rebase
GIT_SEQUENCE_EDITOR=: git rebase --autosquash main

# 4. Restore uncommitted work
git stash pop
```

**When to use `--squash` instead of `--fixup`:** If the revision changes the _meaning_ of the commit (e.g. a renamed variable makes the original subject line inaccurate), use `git commit --squash=<sha>` instead. This opens the editor to let you update the commit message. Provide the updated message via `GIT_SEQUENCE_EDITOR="sed -i ..."` or by amending after the rebase.

### Handling review feedback that spans multiple files

- If the feedback is independent per file, apply each change and fixup into its respective commit.
- If the feedback introduces a new interdependency between files (e.g. a header change that requires a source change), those files may be squashed into a single commit.

## Validating commit history

When the user asks to validate the commit history (or when finalizing work before a PR), the agent should perform the following checks and present the results.

### Checks

1. **Branch naming** — Confirm the branch name is lower-case, dash-separated, and descriptive.
2. **No commits on main** — All work is on a feature branch.
3. **One commit per modified file** — Each pre-existing file appears in exactly one commit, unless it shares a commit with an interdependent file (e.g. a header/source pair).
4. **New/deleted files batched by directory** — New or deleted files are grouped per directory, not scattered across commits.
5. **Commit message format** — Each commit has: imperative subject (< 72 chars), description paragraph, and `Agent:` trailer.
6. **Build order** — Commits are ordered so the repo could theoretically build at each step (dependencies come before dependents).
7. **No fixup/squash leftovers** — No commit subjects starting with `fixup!` or `squash!`.
8. **No untracked or uncommitted changes** — Working tree is clean (or any remaining changes are intentionally uncommitted and noted).

### Output format

Present results as a checklist, then provide a **session summary** covering:

- **Branch**: name and base
- **Commits**: count and one-line list
- **What was done**: brief narrative of the changes made during the session, including any revisions from user review
- **What's next**: any remaining uncommitted work, pending review items, or next steps (e.g. rebase, push, open PR)

Example:

```
## Commit history validation

- [x] Branch naming: `route-rework` — lowercase, dash-separated
- [x] No commits on main
- [x] One commit per modified file (4 modified files, 4 commits)
- [x] New files batched by directory (2 new files in route/, 1 commit)
- [x] Commit message format (all 5 pass)
- [x] Build order (dependencies before dependents)
- [x] No fixup/squash leftovers
- [x] Working tree clean

## Session summary

**Branch**: `route-rework` (off `main`)
**Commits**: 5

1. `a1b2c3d` Add packet counter to Route.c
2. `d4e5f6a` Update routing logic in CmdSetRoute.c
3. ...

**What was done**: Added packet counting to the route service and
updated the set-route command to validate comId bounds. User requested
a revision to the Route.c counter name during review, which was folded
back into the original commit via fixup.

**What's next**: Ready to rebase and push.
```

## Workflow summary

```
1. git checkout main && git pull
2. git checkout -b <branch-name>
3. ... make changes (collaborative workflow above) ...
4. Stage and commit per the rules above
5. Validate commit history
6. git rebase main
7. Push / open PR
```
