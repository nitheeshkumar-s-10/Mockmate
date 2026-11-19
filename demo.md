# MockMate – Demo Guide

## 1. Project Overview

MockMate is an AI-powered mock technical interview agent built using Python, LangChain, LangGraph, and Deep Agents.

It conducts technical interviews, evaluates candidate answers, identifies weak topics, and adapts future questions based on interview performance.

## 2. Running the Application

Start MockMate:

```bash
uv run python main.py
```

## 3. Sample Interview Demonstration

Use the following settings:

- **Role:** ML Engineer
- **Round:** ML Fundamentals
- **Difficulty:** Intermediate
- **Questions:** 3

Answer the first question with a deliberately weak response:

```text
I think regularization makes the model faster.
```

Observe the evaluation scorecard:

- Score out of 10
- Exactly two strengths
- Two knowledge gaps
- Improvement hint
- Suggested next topic

Continue answering the interview questions.

## 4. Adaptive Interview and Weak-Topic Tracking

MockMate identifies topics where the candidate performs poorly.

When prompted to update `workspace/weak-topics.md`:

- Select `A` to approve.
- Select `E` to edit.
- Select `R` to reject.

Verify that rejected updates do not modify the weak-topic file.

Start another interview in the same round and verify that relevant weak topics influence question selection.

Switch to a different round, such as DSA, and verify that unrelated ML weak topics are not selected.

## 5. Session Persistence

MockMate saves interview sessions and supports resuming previous interviews.

To resume an interview:

1. Run the application.
2. Enter an existing thread ID.
3. Continue the interview.

Session checkpoints are stored locally using SQLite.

## 6. Deep Agents Workspace Assistant

MockMate includes a Deep Agents-powered workspace assistant.

Try:

```text
/workspace-summary
```

The assistant can inspect and summarize interview workspace files while respecting workspace restrictions.

## 7. Security Features

MockMate protects workspace files against unsafe operations.

Test these paths:

```text
../secrets.txt
/tmp/outside.txt
```

Both paths must be rejected.

Additional protections include:

- Workspace path validation.
- Approval before destructive file operations.
- Restricted workspace access.
- Protection against unauthorized file deletion.

## 8. Automated Testing

Run the test suite:

```bash
uv run pytest -q
```

Latest verified result:

```text
12 passed, 1 skipped
```

The skipped test is related to a Windows symlink restriction.

## 9. Technology Stack

- Python
- LangChain
- LangGraph
- Deep Agents
- Pydantic
- SQLite
- uv
- pytest
- OpenRouter-compatible model API

## 10. GitHub Repository

Repository: https://github.com/nitheeshkumar-s-10/Mockmate
