# MockMate - An AI-Powered Mock Technical Interview Agent

MockMate is a terminal-based AI interviewer built with Python, LangChain, LangGraph, and Deep Agents. It asks one technical question at a time, evaluates candidate answers using a validated Pydantic scorecard, records interview sessions, tracks weak topics, and adapts future questions based on candidate performance.

## Features

- AI-powered technical interview question generation.
- One question at a time.
- Structured answer evaluation with scores, strengths, gaps, and hints.
- Persistent interview sessions with resume support.
- Weak-topic detection and adaptive questioning.
- User approval before saving or modifying weak-topic records.
- Deep Agents workspace assistant for interview summaries.
- Workspace path validation and protected file operations.
- SQLite-based LangGraph checkpoint memory.

## Requirements

- Python 3.12+
- Git
- uv
- A free-tier model-provider API key (for example, an available OpenRouter or Groq free model).

Provider/model availability and rate limits may change.

## Installation (Windows PowerShell)

Clone the repository:

```powershell
git clone YOUR_REPOSITORY_URL
cd MockMate
```

Install dependencies:

```powershell
uv sync
```

Create the environment file:

```powershell
Copy-Item .env.example .env
notepad .env
```

Configure these variables in `.env`:

```env
MODEL_PROVIDER=openai
MODEL_NAME=YOUR_AVAILABLE_MODEL
MODEL_API_KEY=YOUR_API_KEY
MODEL_BASE_URL=https://openrouter.ai/api/v1
MODEL_TEMPERATURE=0.2
```

Use the appropriate provider, model name, and API key for your chosen service.

**Never commit `.env` or expose your API key.**

## Run MockMate

```powershell
uv run python main.py
```

Enter your:
- Interview role
- Interview round
- Difficulty level
- Number of questions

Press Enter at the thread ID prompt to start a new session, or enter an existing thread ID to resume an interview.

### Available Commands

| Command | Description |
|---|---|
| `/quit` | Pause the interview |
| `/workspace-summary` | Generate a Deep Agents workspace summary |
| `/delete-session` | Open the protected session deletion workflow |

## Answer Evaluation

MockMate evaluates answers using a structured scorecard containing:

- Score (0-10)
- Strengths
- Knowledge gaps
- Improvement hints
- Suggested next topic

Weak answers can be recorded as weak topics after user approval.

## Memory and Storage

- `workspace/sessions/` - Human-readable interview transcripts.
- `workspace/weak-topics.md` - Persistent weak-topic memory.
- `workspace/mockmate_checkpoints.sqlite` - LangGraph checkpoint database.

Local session data, databases, and API credentials are excluded from Git.

## Architecture and Technologies

| Technology | Purpose |
|---|---|
| Python | Core application |
| LangChain | Model integration |
| LangGraph | Interview workflow and state management |
| Pydantic | Structured answer evaluation |
| SQLite | Persistent conversation checkpoints |
| Deep Agents | Workspace assistant |
| FilesystemBackend | Workspace file access |
| uv | Dependency and environment management |

### Workflow

1. Candidate starts or resumes an interview.
2. MockMate generates an interview question.
3. Candidate submits an answer.
4. The AI evaluates the answer.
5. Feedback and score are displayed.
6. Weak topics are identified.
7. User approves or rejects weak-topic updates.
8. Future questions adapt to recorded weak areas.
9. Session information is saved for future resumption.

## Tests

Run the automated test suite:

```powershell
uv run pytest -q
```

Tests cover:
- Workspace path validation.
- Protection against directory traversal.
- Approval-required file operations.
- Schema validation.
- Session memory behavior.

## Project Structure

```text
MockMate/
├── src/mockmate/
│   ├── agent.py
│   ├── approval.py
│   ├── cli.py
│   ├── config.py
│   ├── deep_workspace.py
│   ├── evaluator.py
│   ├── memory.py
│   ├── model.py
│   ├── prompts.py
│   ├── schemas.py
│   └── security.py
├── skills/
├── tests/
├── workspace/
├── main.py
├── pyproject.toml
├── uv.lock
├── .env.example
├── .gitignore
└── README.md
```

## Notes

Interview scores are intended for practice and learning. They are not an objective certification of technical ability.

MockMate is designed as a local, terminal-based AI interview practice application.