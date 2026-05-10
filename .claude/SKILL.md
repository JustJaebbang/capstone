## Editing philosophy

- Prefer minimal diffs over large rewrites.
- Preserve existing architecture unless explicitly asked.
- Do not rewrite working modules to improve style only.
- Preserve orchestrator / module separation.
- Avoid introducing new abstractions too early.

## Backend workflow

Before editing:
1. Identify affected layer.
2. Check related schema.
3. Preserve existing API response shape.
4. Prefer incremental fixes.

When debugging:
- Trace request flow first.
- Fix smallest failing unit.
- Avoid changing unrelated modules.

## Debugging workflow

- Read full traceback before suggesting fixes.
- Explain root cause first.
- Suggest exact file and code location.
- Prefer surgical fixes over rewrites.
- Do not remove features to silence errors.

## Refactor rules

Avoid:
- broad architectural rewrites
- changing schemas without approval
- moving responsibilities across services
- replacing JSON persistence

Prefer:
- additive changes
- backward compatibility
- explicit migration paths

## API rules

- Preserve snake_case fields.
- Preserve current response contracts.
- Keep module boundaries stable.
- Do not merge orchestrator and module logic.

## Frontend rules

- Check current Next.js version before using older patterns.
- Avoid unnecessary client components.
- Preserve existing API integration flow.

## Response style

When suggesting changes:
- explain why
- list affected files
- provide exact code locations
- avoid vague high-level advice
