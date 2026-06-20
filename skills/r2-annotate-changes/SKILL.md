---
name: r2-annotate-changes
description: Launch Plannotator for interactive browser-based annotations on uncommited changes in the repository
user-invocable: true
disable-model-invocation: true
---

Plannotator is a browser-based UI for interactive annotation where the user can review and provide feedback on uncommitted changes in the repository.

## Workflow

**Step 1:** Run: `plannotator review`

**Step 2:** Wait — the user may take a long time reviewing. Do not run the command again.

**Step 3:** If it returns feedback or annotations, address them in the same conversation.

**Step 4:** If it returns an approval/LGTM-style message, acknowledge that review passed and continue.

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