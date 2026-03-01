# Lessons.md

Purpose: capture durable lessons from implemented features and bug fixes so future feature development is faster, safer, and less repetitive.

## How To Use This File
- Read this file before starting implementation.
- For every feature/bug fix, append lessons if new behavior, risk, or debugging pattern was discovered.
- Keep lessons concrete and tied to file/module realities in this repo.

## Lessons Learned (Current Repo State)

### 1) Use requirement IDs as the implementation spine
- Map code, tests, docs, and plans to requirement IDs early.
- This reduces drift between behavior and documentation and prevents silent contract regressions.

### 2) Documentation drift appears quickly; update docs in the same change set
- If behavior changes and docs are deferred, gaps spread across architecture, specs, plans, and debt trackers.
- Always update:
  - architecture docs,
  - product specs,
  - execution plans,
  - tech debt tracker,
  - internal API contract docs.

### 3) PlantUML source must be first-class, not an afterthought
- Keep `.puml` as the canonical flow artifact.
- Regenerate `.svg` whenever interaction flow or architecture changes.
- Stale diagrams cause onboarding confusion and incorrect implementation assumptions.

### 4) Parser fallbacks should be constrained, not broad
- Broad text scanning caused false-positive discussion dates (for example subject deadlines like `Ends YYYY-MM-DD`).
- Better pattern:
  - prefer explicit metadata (`<time>`, `datetime`, date-tagged attributes/classes),
  - only use strict metadata-line fallbacks (`Date:`, `Sent:`, `Posted:`),
  - avoid generic container-wide date extraction.

### 5) Bounded fetches are necessary, but trade precision for latency
- Active drafts and discussions can be expensive if unbounded.
- Current repo pattern uses practical limits (for example 10 drafts, bounded discussion pages).
- Any cap should be documented and tracked as tech debt if it can under-sample.

### 6) Keep CLI and MCP behavior aligned for shared features
- Divergence (for example full charter in CLI but summary in MCP) creates user confusion and breaks requirement parity.
- For common features, apply changes to both surfaces unless the requirement explicitly allows asymmetry.

### 7) Prompt UX stability matters for automation and test reliability
- Small prompt-text changes can break tests and degrade usability.
- Keep prompts minimal and consistent; avoid repeating verbose navigation hints in every prompt.

### 8) Regression tests should target real failure modes, not only happy paths
- Add tests for bugs actually observed in usage (date parsing regressions, output-format regressions, limit behavior).
- Preserve tests that enforce contracts around prompts, limits, and output shape.

### 9) Tech debt should be explicit and narrow
- Record debt with:
  - requirement references,
  - current progress,
  - concrete gap,
  - next action.
- This keeps roadmap decisions deterministic and reviewable.

### 10) Maintain a closed-loop workflow
- Every meaningful implementation change should finish with:
  - tests passing,
  - docs synced,
  - diagrams synced,
  - lessons captured.

## Feature-Specific Notes From Recent Work
- Vector DB quality improved when WG `/documents/` corpus text was included in addition to charter text.
- Technology onboarding output currently includes score for debug value; UX cleanup to hide score by default is tracked debt.
- Discussion summaries are highly sensitive to date parsing; metadata-first extraction is the stable approach.

## Update Template (Use For New Entries)
- Date:
- Change type: feature | bug fix | refactor
- Modules touched:
- What went wrong / what was discovered:
- What pattern now works:
- Test added to protect it:
- Docs/diagrams updated:
- Follow-up debt (if any):
