# coding_practices.md

Purpose: define coding standards, review standards, and test considerations for this repository.

## 1. Coding Standards

### 1.1 Requirements-first development
- Identify requirement IDs before coding.
- Preserve requirement-to-code traceability in PR/change summaries.

### 1.2 Deterministic and defensive parsing
- Prefer official API sources first; use HTML fallback parsers when needed.
- Fallback parsing must be explicit and constrained.
- Never silently swallow parser/network failures; return actionable errors.
- Network access policy: use a 120-second timeout for Datatracker/mailarchive web requests.
- Error messages for network failures must include the exact URL that was unreachable.

### 1.3 Surface parity and contract consistency
- Keep shared feature semantics aligned across CLI and MCP.
- If behavior intentionally differs by surface, document rationale in design/spec docs.

### 1.4 Performance-aware defaults
- Use bounded data-fetch limits for expensive operations.
- Document limits in code comments and docs.
- Track quality/performance tradeoffs in tech debt if limits can reduce completeness.

### 1.5 Safe maintainability patterns
- Keep functions focused and names descriptive.
- Preserve dataclass/API return contracts when extending behavior.
- Avoid introducing hidden state or non-deterministic behavior in core parsing/matching flows.

## 2. Review Standards

### 2.1 Review checklist (mandatory)
1. Requirement mapping is explicit.
2. Behavior changes include tests.
3. Parser changes include fallback/edge-case coverage.
4. CLI and MCP parity reviewed for shared features.
5. Docs are synchronized.
6. PlantUML source + render updated for flow/architecture changes.
7. `Lessons.md` and this file are updated if new standards/lessons emerged.

### 2.2 Change quality gates
- No undocumented behavior changes.
- No unexplained prompt/output format changes.
- No regression in requirement contracts without explicit requirement update.

## 3. Test Considerations

### 3.1 Minimum tests per behavioral change
- At least one CLI-path test.
- At least one parser/unit test.

### 3.2 Preferred test design
- Keep tests deterministic and isolated.
- Stub network calls in parser tests.
- Add regression tests for observed production-like bugs.
- Validate user-visible outputs where format/wording is part of contract.

### 3.3 Core commands
- Primary validation command:
  - `python -m pytest -q tests`
- If environment maps differently:
  - `python3 -m pytest -q tests`

## 4. Documentation And Diagram Discipline
- Update relevant docs in `docs/` for every behavior/interface/data-source change.
- Update execution plan records:
  - `docs/exec-plans/active/`
  - `docs/exec-plans/completed/`
  - `docs/exec-plans/tech-debt-tracker.md`
- If flow/architecture changed:
  - update PlantUML `.puml`,
  - regenerate corresponding `.svg` (or `.png`) artifact.

## 5. Current Repo-Specific Standards
- Discussion date parsing: metadata-first extraction only; avoid broad date matching from arbitrary container text.
- Onboarding prompts: keep minimal and stable; avoid repeating long navigation hints.
- Active drafts onboarding path: bounded output for latency control.
- Use requirement-named wrappers in `ietf.py` for contract-level integrations.
- Web fetch defaults in `ietf.py` use `HTTP_TIMEOUT_SECONDS = 120` and URL-specific failure messages.

## 6. Update Rules For This File
- Update when new review standards or test expectations are introduced.
- Do not remove existing standards without a documented replacement and rationale.
