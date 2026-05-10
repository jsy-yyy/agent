# AI Coding Rules

These rules guide every AI agent or LLM-assisted coding session in this repository. They are mandatory unless the user explicitly overrides them in the current task.

## 1. Mandatory Pre-Coding Reads

Before writing, editing, generating, or refactoring any code, the agent must fully read:

1. `memory-bank/architecture.md`
2. `memory-bank/design-document.md`

This is required even for small code changes. The architecture file is the source of truth for data models, persistence, API contracts, and cross-module boundaries. The database schema may evolve during implementation, but every implemented schema change must be reflected there.

If either file is missing, empty, or unreadable:

- Do not write code yet.
- Inform the user which required file is missing or unreadable.
- Ask whether to create or restore the missing memory-bank file before implementation.

## 2. Architecture Memory Must Stay Current

After completing any major feature, milestone, schema change, API change, data-flow change, or module-boundary change, the agent must update:

```text
memory-bank/architecture.md
```

The update must reflect the actual implemented system, not just the intended design.

Examples of changes that require an architecture update:

- New backend module, service, route, worker, or provider.
- New frontend feature area or major component boundary.
- Database schema changes.
- New API endpoint or changed request/response shape.
- New file storage layout.
- Changes to RAG indexing, graph construction, textbook parsing, or integration decisions.
- Any migration from mock data to real data.

## 3. Modular Code Is Required

The project must be implemented as a clean, modular, multi-file codebase. Prefer small files with a single clear responsibility over large files that mix concerns.

Required principles:

- Keep parsing, graph extraction, integration, RAG, chat, reporting, and configuration in separate modules.
- Keep API route handlers thin; business logic belongs in services.
- Keep data schemas/models separate from route handlers and UI components.
- Keep reusable frontend UI pieces in components.
- Keep API client code separate from React components.
- Keep prompts in dedicated prompt/template files or clearly separated service modules.
- Keep constants and configuration in dedicated files.
- Add new files when a new responsibility emerges instead of expanding an unrelated file.

Recommended backend shape:

```text
backend/
  app/
    api/
    core/
    models/
    schemas/
    services/
    prompts/
    storage/
    main.py
```

Recommended frontend shape:

```text
frontend/
  src/
    api/
    components/
    features/
    hooks/
    types/
    App.tsx
```

## 4. Monolithic Giant Files Are Forbidden

Do not create or grow single-file implementations that contain multiple unrelated responsibilities.

Forbidden patterns:

- One backend file containing routes, database setup, parsing, LLM calls, RAG indexing, and report generation.
- One frontend component containing upload UI, graph rendering, RAG chat, integration decisions, and API calls.
- Large prompt strings scattered through unrelated files.
- Duplicated schemas across frontend and backend without a clear reason.
- Utility dumping grounds such as `helpers.py`, `utils.ts`, or `common.ts` containing unrelated logic.

Soft limits:

- Prefer keeping most source files under 300 lines.
- If a file approaches 400 lines, split it unless there is a strong reason not to.
- If a function exceeds roughly 60 lines, consider extracting smaller functions.
- If a component manages more than one feature area, split it into feature-level components.

These are not arbitrary style limits; they exist to keep the project readable, testable, and safe for multiple AI-assisted edits.

## 5. Keep The Repository Clean

The repository should stay easy to inspect and safe to submit.

Rules:

- Do not commit uploaded textbooks, PDFs, vector indexes, generated caches, secrets, or local environment files.
- Keep generated runtime data under `data/` and ensure it is ignored by git unless a placeholder is needed.
- Keep reports under `report/`.
- Keep planning and design documents under `memory-bank/`.
- Keep dependency files minimal and explicit.
- Do not introduce a framework, service, or dependency unless it directly supports the project goals.
- Prefer boring, reliable code over clever abstractions.

## 6. Implementation Workflow

For every coding task:

1. Read `memory-bank/architecture.md` completely.
2. Read `memory-bank/design-document.md` completely.
3. Identify the affected modules and files.
4. Make the smallest modular change that satisfies the task.
5. Avoid touching unrelated files.
6. Run relevant checks or explain why they could not be run.
7. If a major feature or milestone was completed, update `memory-bank/architecture.md`.

## 7. Source Of Truth Order

When making technical decisions, use this priority order:

1. Current user request.
2. `memory-bank/architecture.md`
3. `memory-bank/design-document.md`
4. `memory-bank/tech-stack.md`
5. `memory-bank/implementation-plan.md`
6. `memory-bank/progress.md`
7. Existing code behavior.

If these sources conflict, pause and explain the conflict before writing code.

## 8. AI Prompting Rules For This Project

When asking an LLM to generate project code, include these constraints:

- Use a modular multi-file structure.
- Do not produce a single giant file.
- Follow the existing directory layout.
- Keep route handlers thin and put business logic in services.
- Keep frontend API calls outside UI components.
- Use explicit typed schemas where possible.
- Do not invent database fields without checking `memory-bank/architecture.md`.
- Do not change API contracts without updating architecture documentation.
- Preserve existing user code and avoid unrelated refactors.

## 9. Definition Of Done

A task is not done until:

- The implementation follows the modular structure.
- No new monolithic file was introduced.
- Required memory-bank files were read before coding.
- Relevant docs were updated when architecture changed.
- Generated data, secrets, and large files are not tracked.
- The final response clearly states what changed and what was verified.
