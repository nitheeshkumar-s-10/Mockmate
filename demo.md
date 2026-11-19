# MockMate Demo Transcript

This is a reproducible demonstration script. Model wording and scores vary.

1. Start the app:
   `uv run python main.py`
2. Role: `ML Engineer`
3. Round: `ML Fundamentals`
4. Difficulty: `Intermediate`
5. Questions: `3`
6. Answer the first question with a deliberately weak answer:
   `I think regularization makes the model faster.`
7. Confirm that the scorecard contains a score, exactly two strengths, two gaps,
   a hint, and a next topic.
8. When prompted to update `weak-topics.md`, choose `R` to reject.
9. Open `workspace/weak-topics.md` and verify its contents did not change.
10. Run the app again using the same thread ID to resume, or use a new thread ID
    to start a clean interview.

Security checks:
- `../secrets.txt` must be rejected.
- `/tmp/outside.txt` must be rejected.
- These checks are automated by `uv run pytest`.
