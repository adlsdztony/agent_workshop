# Stage 3 · Multi-Agent Workflow

Now that you can extend a single agent, orchestrate an end-to-end workflow with multiple specialists. Each agent can own a slice of the problem; the coordinator decides how to route tasks and merge results.

## Learning Goals

- Model a multi-step process with cooperating agents and handoffs.
- Maintain lightweight shared context across the workflow.
- Decide when to stop at tool output vs returning control to the LLM.
- Capture structured outputs for downstream automation.

## 1. Concepts Refresher

- **Handoffs** — An agent can delegate to another agent (or a `handoff(...)` wrapper) when it needs help. Provide a `handoff_description` so the coordinator knows when to call it.
- **Coordinator Agent** — The top-level agent that routes work across specialists.
- **Run Context** — Mutable object you can design to store shared state (not required, but powerful).
- **RunConfig** — Controls limits like `max_turns` or disables tracing for silent runs.

## 2. Demo Overview

File: `stages/stage3/demo.py`

Agents involved:

1. `ResearchAgent` — pulls TODOs and curriculum insights (reuses Stage 2 tooling).
2. `PlannerAgent` — packages discoveries into a workflow outline.
3. `ReviewerAgent` — double-checks the plan and suggests guardrails.
4. `Coordinator` — orchestrates the flow, calling the others via handoffs.

Run the demo:

```bash
python stages/stage3/demo.py
```

Observe the console output to see which agent handled each step. Compare the final structured workflow against the intermediate messages logged during the run.

### Highlights

- Specialists share a light-weight context object (`WorkflowState`) where they store intermediate notes.
- The coordinator uses explicit instructions to call specific handoffs in order: research → plan → review.
- Each handoff returns structured data that the coordinator can enrich or summarise.

## 3. Designing Workflow State

`WorkflowState` (defined inside `demo.py`) tracks:

- `research_notes`: textual discoveries from shell + MCP calls.
- `action_items`: list of planned tasks.
- `risks`: guardrail suggestions from the reviewer.

You can extend this pattern to store file paths, test results, or tool outputs for later steps.

## 4. Activity

File: `stages/stage3/activity/starter_workflow.py`

> Build a deployment workflow comprised of:
>
> 1. A **Preflight agent** that validates configuration (use shell + optional MCP).
> 2. An **Execution agent** that drafts deployment steps.
> 3. A **Validation agent** that specifies success criteria and rollback triggers.
>
> The coordinator should return a structured `DeploymentWorkflow` object with `preflight_checks`, `deployment_steps`, and `validation_plan`.
>
> Tasks:
> - Flesh out the agent instructions so delegation happens automatically.
> - Decide which tools each agent needs (reuse Stage 1 & Stage 2 components).
> - Populate the shared context to capture key facts between stages.

Run your workflow:

```bash
python stages/stage3/activity/starter_workflow.py
```

**Stretch ideas**

- Add a `ToolInputGuardrail` to block destructive shell commands.
- Create an MCP server that returns environment metadata and plug it into the preflight agent.
- Serialize the final plan to disk for future automation scripts.

Congrats! Completing this stage means you can spin up a reproducible multi-agent environment with local LLMs, custom tools, and MCP integrations. Use this structure to prototype real automations with your team.
