---
name: r2-pr-describe
description: (TODO)
argument-hint: Qual o hash do commit do qual iniciar a análise?
---

# r2-pr-describe

You are reviewing the current Git branch before opening a Pull Request.

Starting on the provided commit all the way to the HEAD of the branch, inspect the diffs and generate a Pull Request description based on the combined changes, not as a commit-by-commit summary.

This is supposed to be a summary to guid reviewers, not a comprehensive list of every single object or file touched.

Instead, follow these guidelines:
- Eliminate duplicate or intermediate work (refactors, fixups, renames, formatting, etc.) unless they are relevant to the final result.
- Group related changes into logical features/fixes instead of listing every file touched.
- Focus on what changed an why, from the perspective of the reviewer.
- Infer the intent behind the changes when possible.
- Mention important implementation details when they help reviewers understand the change.
- Mention breaking changes, migrations, configuration changes, API changes, behavioral changes, or potential risks when applicable.
- Do not invent functionality that is not supported by the commits.
- Summarize the final result, not the individual commits.

Important: Write in Brazilian Portuguese.

Use this format (output markdown source):

```md
## Sumário

A short paragraph describing the overall purpose of the PR (max two lines).

## Mudanças

- ...
- ...
- ...

# Verificação

 Describe how these changes were tested or how they can be verified. Omit this section if it is not applicable.

## Notas
- Important information reviewers should know.
- Omit this section if there is nothing noteworthy.
```
