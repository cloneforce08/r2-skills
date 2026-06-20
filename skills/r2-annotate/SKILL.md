---
name: r2-annotate
description: >
  Launch Plannotator for interactive browser-based annotations. Handles 2 modes:
  annotating a markdown file (auto-triggered when producing a plan or document for the user to review); annotating the latest assistant response ("response").
  Use when the user explicitly invokes this skill or when intent detection signals apply.
argument-hint: "'response', a MD file path or leave empty to auto-detect"
user-invocable: true
---

Plannotator is a browser-based UI for interactive annotation. Use it in one of 2 modes depending on context.

## Intent Detection — When to Auto-Trigger

### Document mode (plan/document review)

Trigger when:

- You just produced a plan, proposal, architecture document, checklist, or any substantial markdown output (50 lines or more) and it makes sense to offer the user a chance to review and annotate it interactively.
- You're working on a markdown file and the user indicates that they want to review the file (words like "review", "annotate" or "check" in the user message are tells, especially when combined with a file name or "this file" or similar - in any language, e.g., "quero revisar isso", "anotar esse plano", "deixa eu revisar essa documentação").
- The user invokes this skill with a markdown file name/path as argument.
- The user invokes this skill without an argument and there is a recently created/modified markdown file that is the most likely target.

If you're not sure what is it the user wants to annotate, ask a clarifying question.

### Latest response mode (review latest assistante response)

Trigger **only** when:

- The user invokes this skill with the argument `response` and there is a recent assistant response with 100 words or more.
  - If there is no recent assistant response, ask the user to clarify what they want to annotate.
  - If the recent assistant response is too short, reply to the user that it is too short to annotate and that they can give feedback directly in the chat.

## Mode 1 — Document

Use when annotation a specific markdown file.

**Step 1:** If the content is not yet saved to a file, save it first (e.g., `plan.md`).

**Step 2:** Run: `plannotator annotate "<file-path>"`

**Step 3:** Wait — the user may take a long time reviewing. Do not run the command again.

**Step 4:** If annotations are returned, address them directly and thoroughly.

## Mode 2 — Latest response

Use when the user wants to annotate your latest message.

**Step 1:** Export your last response to a temporary markdown file in a system temp directory (e.g., `/tmp/`). Choose a filename that reflects the context of the response in the format `<yyyymmdd-hhmm>-<slug>.md` (e.g., `20260619-2303-explanation-docker-setup.md`).

**Step 2:** Run: `plannotator annotate "<file-path>"`

**Step 3:** Wait — the user may take a long time reviewing. Do not run the command again.

**Step 4:** If annotations come back, incorporate the feedback into a follow-up response.

## Patience Rule

Plannotator opens a browser session driven by the user. The process remains blocked while the user works on it, and that may take a very long time. **Never** close, kill, restart, or reopen Plannotator while it is running. Wait until the command exits on its own.

## Error Handling

### Plannotator is not installed

If Plannotator is not installed or not found in PATH, reply to the user that it is required for this feature and provide installation instructions:

Website: https://plannotator.ai

Installation command:

```bash
curl -fsSL https://plannotator.ai/install.sh | bash
```

Ask the user if they want to install it now. If they say yes, run the installation command. If they say no, acknowledge and do not proceed.

### Plannotator exits with an error code or with no output

Plannotator always exits with a success code, even when the user closes it without leaving feedback.

If the command exits with an error code or with no output, it is ambiguous — the user may have closed it intentionally or accidentally, or something went wrong. In all these cases:
1. Briefly acknowledge that no feedback was received (or that an error occurred).
2. Ask the user to either paste the exported annotations into chat or provide feedback directly.
3. **Do not proceed** with the task until the user responds.