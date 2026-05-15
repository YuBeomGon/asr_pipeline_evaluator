# Bakeoff Versions

Record exact versions, install commands, model choices, prompts, and manual interventions here.

| Framework | Workspace | Version / Commit | Install command | Model used | Prompt file | Manual interventions | Notes |
|---|---|---|---|---|---|---|---|
| Spec Kit | workspaces/spec-kit | 0.8.11.dev0 (commit: 6322a4d) | `uvx --from git+https://github.com/github/spec-kit.git specify init . --integration claude --no-git --force` | TBD | common_asr_pipeline_prompt.md | removed .gitkeep before init | skills in .claude/skills/, templates in .specify/ |
| OpenSpec | workspaces/openspec | 1.3.1 | `npm install -g @fission-ai/openspec && openspec init --tools claude` | TBD | common_asr_pipeline_prompt.md | none | skills+commands in .claude/ |
| GSD | workspaces/gsd | 1.42.1 | `cd workspaces/gsd && npx get-shit-done-cc@latest --local --claude` | TBD | common_asr_pipeline_prompt.md | used --local flag to force local install; first attempt went global and was cleaned up | skills in .claude/ |
| BMAD | workspaces/bmad | 6.6.0 (BMad Core) | `cd workspaces/bmad && npx bmad-method install --yes --tools claude-code` | TBD | common_asr_pipeline_prompt.md | none | skills in .claude/skills/, config in _bmad/ |

## Kit changelog

| Date | Change |
|---|---|
| 2026-05-15 | Added explicit implementation scope sources: `docs/07-implementation-scope.md` and `.claude/skills/asr-pipeline-evaluator/assets/baseline/IMPLEMENTATION_SCOPE.md`. Updated README, CLAUDE.md, generation command, common prompt, target contract, and evaluator documentation scoring to require implementation-scope documentation. |
