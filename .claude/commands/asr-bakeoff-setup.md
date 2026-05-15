# ASR Bakeoff Setup

Prepare this repository for a fair ASR serving pipeline bakeoff.

## Task

1. Read `README.md`, `CLAUDE.md`, and `docs/06-what-this-kit-does.md`.
2. Verify the expected directories exist:
   - `workspaces/spec-kit/`
   - `workspaces/openspec/`
   - `workspaces/gsd/`
   - `workspaces/bmad/`
   - `outputs/spec-kit/`
   - `outputs/openspec/`
   - `outputs/gsd/`
   - `outputs/bmad/`
   - `reports/`
3. Create `versions.md` if missing.
4. Summarize what still needs to be installed manually.

## Important

Do not install the four frameworks into the same workspace.

Each framework must be isolated:

```text
workspaces/spec-kit/
workspaces/openspec/
workspaces/gsd/
workspaces/bmad/
```

## versions.md template

```markdown
# Bakeoff Versions

| Framework | Workspace | Version / Commit | Install command | Model used | Prompt file | Notes |
|---|---|---|---|---|---|---|
| Spec Kit | workspaces/spec-kit | TBD | TBD | TBD | common_asr_pipeline_prompt.md | |
| OpenSpec | workspaces/openspec | TBD | TBD | TBD | common_asr_pipeline_prompt.md | |
| GSD | workspaces/gsd | TBD | TBD | TBD | common_asr_pipeline_prompt.md | |
| BMAD | workspaces/bmad | TBD | TBD | TBD | common_asr_pipeline_prompt.md | |
```
