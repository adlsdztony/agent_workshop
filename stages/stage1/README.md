# Stage 1 · Build the Read Tool

Stage 0 confirmed the SDK wiring with a mock tool. Stage 1 keeps the momentum
by pairing a real shell tool demo with an activity where you implement the
`read.file` helper that every later stage relies on.

## Learning Goals

- Wrap subprocess calls with `function_tool` and return structured
  `ToolOutputText` payloads.
- Enforce guardrails: workspace-only file access, short timeouts, trimmed output.
- Teach an agent how to read source files safely so it can reason about edits
  before writing.

## 1. Demo · `bash.run`

File: `stages/stage1/demo.py`

- Exposes `utils/tools/bash.py::run_bash_command` as the `bash.run` tool.
- The prompt asks for: root directories, Dockerfile presence, and a suggested
  next command.
- Shows how to cite executed commands in the final report.

Run it:

```bash
python -m stages.stage1.demo --verbose
# append --verbose to stream the tool calls in real time
```

## 2. Activity · Implement `read.file`

Files:

- `utils/tools/read_file.py` — where you will implement the tool body.
- `stages/stage1/activity/test_read_file.py` — executable spec and smoke test.
- `stages/stage1/activity/starter_agent.py` — an agent harness that can edit
  the tool using the provided `bash.run` and `write.file` helpers.

### Requirements for `read.file`

The `@function_tool` in `utils/tools/read_file.py` should:

1. Accept a repo-relative `path` plus optional `start_line`, `end_line`, and a
   `max_output_chars` clamp (default 4000 characters).
2. Resolve the target via `utils.workspace_path.resolve_workspace_path` so
   callers cannot escape `/workspace`.
3. Emit numbered lines to make surgical edits easier. When no line range is
   provided, show the full file; when a range is given, validate that it is
   increasing and inside the file.
4. Gracefully handle empty files, missing files, and OS errors by returning a
   descriptive `ToolOutputText`.
5. Truncate overly long responses and append `...` so outputs never exceed the
   `max_output_chars` budget.

### Workflow

1. Inspect `utils/tools/read_file.py` to understand the scaffolding.
2. Run `python -m stages.stage1.activity.starter_agent --verbose` to let the
   agent help you reason about the change (it only has `bash.run` and
   `write.file`, so you may see it using shell commands until `read.file`
   works).
3. Once the tool is implemented, run the smoke test:

   ```bash
   python -m stages.stage1.activity.test_read_file --verbose
   ```

   This spins up a tiny QA agent that calls `read.file` against sample files and
   a missing-file edge case; the `--verbose` flag lets you watch the tool calls.
4. Commit when you are happy, then move on to Stage 2 to combine custom tools
   with a FastMCP server.

`write.file` and `bash.run` are already implemented for you. Focus entirely on
getting `read.file` production-ready.
