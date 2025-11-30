"""
Stage 3 Activity: Red Team vs. Blue Team (File-Based).

Objective:
  A vulnerable `server.py` exists on disk.
  - Red Team reads the code and reports vulnerabilities.
  - Blue Team reads the code and rewrites it to fix the issues.
  - CISO coordinates the loop until the file is clean.

Run with: python -m stages.stage3.activity.starter_workflow
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from agents import (
    Agent,
    ModelSettings,
    RunContextWrapper,
    Runner,
    ToolOutputText,
    function_tool,
)
from pydantic import BaseModel

from utils.cli import build_verbose_hooks, parse_common_args
from utils.ollama_adaptor import model


# --- Setup: The Vulnerable File ---

TARGET_FILE = Path(__file__).parent / "server.py"

# --- Shared State ---

@dataclass
class AuditState:
    """Tracks the audit progress."""
    vulnerabilities: list[str] = field(default_factory=list)
    iteration: int = 0


# --- Output Schema ---

class SecurityReport(BaseModel):
    final_file_path: str
    resolved_issues: list[str]
    status: Literal["SECURE", "UNSAFE"]
    iterations: int


# --- Tools ---

@function_tool(name_override="fs.read_code")
def read_code() -> str:
    """Read the current content of 'server.py'."""
    if not TARGET_FILE.exists():
        return "Error: server.py does not exist."
    return TARGET_FILE.read_text(encoding="utf-8")


@function_tool(name_override="fs.rewrite_code")
def rewrite_code(
    ctx: RunContextWrapper[AuditState],
    new_content: str,
    fix_summary: str,
) -> str:
    """
    (Blue Team) Overwrite 'server.py' with fixed code.
    
    Args:
        new_content: The complete Python code to write.
        fix_summary: Brief description of what was fixed.
    """
    TARGET_FILE.write_text(new_content, encoding="utf-8")
    
    # Clear vulnerabilities as we are attempting a fix
    count = len(ctx.context.vulnerabilities)
    ctx.context.vulnerabilities.clear()
    ctx.context.iteration += 1
    
    return f"File rewritten. Cleared {count} reported vulnerabilities. Fix: {fix_summary}"


@function_tool(name_override="audit.report_issue")
def report_issue(
    ctx: RunContextWrapper[AuditState],
    severity: Literal["high", "medium", "low"],
    description: str,
) -> str:
    """
    (Red Team) Report a specific security issue found in the code.
    """
    entry = f"[{severity.upper()}] {description}"
    ctx.context.vulnerabilities.append(entry)
    return f"Logged issue: {entry}"


# --- Main Workflow ---

async def main(verbose: bool = False) -> None:
    # 1. Setup the environment
    hooks = build_verbose_hooks(verbose)
    state = AuditState()

    # 2. Define Agents
    blue_agent = Agent(
        # TODO: Define Blue Team agent to fix vulnerabilities
        ...
    )

    red_agent = Agent(
        # TODO: Define Red Team agent to audit vulnerabilities
        ...
    )

    ciso_agent = Agent(
        name="CISO",
        instructions=(
            "Orchestrate the security audit of 'server.py'.\n"
            "Phase 1: Call Red Team to scan the code.\n"
            "Phase 2: Check results.\n"
            "   - If vulnerabilities found: Call Blue Team to fix them. Then loop back to Red Team.\n"
            "   - If NO vulnerabilities found: Output the final SecurityReport (Status: SECURE).\n"
            "   - If iteration > 3: Abort and output SecurityReport (Status: UNSAFE)."
        ),
        handoffs=[blue_agent, red_agent],
        model=model,
        model_settings=ModelSettings(temperature=0.1),
        output_type=SecurityReport,
    )

    # 3. Run
    print("> Starting Code Audit Simulation...\n")
    
    result = await Runner.run(
        ciso_agent, 
        "Audit the server.py file until it is secure.", 
        context=state, 
        hooks=hooks
    )

    report = result.final_output_as(SecurityReport)

    print("\n=== Final Security Report ===")
    print(report.model_dump_json(indent=2))
    
    print(f"\nFinal Code Content ({TARGET_FILE.name}):")
    print("-" * 40)
    print(TARGET_FILE.read_text(encoding="utf-8"))
    print("-" * 40)


if __name__ == "__main__":
    args = parse_common_args(__doc__)
    asyncio.run(main(verbose=args.verbose))