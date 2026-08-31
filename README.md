# Autonomous Code Debugging Agent

An autonomous AI agent that investigates software bugs, uses repository tools, runs tests, modifies code, verifies its own fixes, and produces structured execution traces.

The project focuses on agent engineering rather than a simple LLM wrapper. The model does not receive a fixed sequence of steps. It decides which action to take based on the bug report and evidence collected during the investigation.

## What It Does

Given a bug report such as:

> Users receive a 401 when refreshing their access token with a valid refresh token.

The agent can:

1. Inspect the repository
2. Search the codebase
3. Read relevant files
4. Run approved tests
5. Form a diagnosis from collected evidence
6. Generate a targeted code change
7. Apply the patch inside an isolated workspace
8. Run tests after the modification
9. Revise the fix if verification fails
10. Stop only after the fix has been verified or a safety limit is reached

The important distinction is that these steps are not implemented as a hard-coded debugging workflow. The model chooses its next action from a constrained set of tools based on the current state of the investigation.

## Architecture

```text
Bug Report
    |
    v
Agent Decision Model
    |
    v
Validated AgentAction
    |
    v
Tool Executor
    |
    +--> Repository Inspection
    |      ├── list_directory
    |      ├── read_file
    |      └── search_code
    |
    +--> Test Execution
    |      └── run_tests
    |
    +--> Code Modification
    |      └── apply_patch
    |
    +--> finish
    |
    v
Structured Observation
    |
    v
Agent State
    |
    +------> Next Decision
    |
    v
Verification / Safety Guards
    |
    v
Final Diagnosis
```

The decision model and tool execution layer are intentionally separated. The LLM chooses an action, but deterministic application code validates and executes that action.

## Agent State

The agent maintains structured state throughout a run, including:

- bug report
- iteration count
- tool calls
- tool observations
- inspected files
- current investigation evidence
- patch attempts
- test executions
- latest patch step
- latest successful test step
- final diagnosis
- completion status

Tool observations are returned to the model so later decisions can react to actual repository and test results.

## Available Tools

### Repository inspection

The agent can safely:

- list repository directories
- read UTF-8 text files
- search source code

Repository paths are resolved through a workspace abstraction that prevents access outside the repository.

### Test execution

The agent can execute approved pytest commands.

Test execution uses:

```text
sys.executable -m pytest
```

with:

- no shell execution
- repository-scoped working directory
- command allowlisting
- execution timeout
- captured stdout and stderr

Arbitrary shell commands are not exposed to the model.

### Code modification

The agent can apply targeted text replacements.

A patch is rejected when:

- the target file does not exist
- the path escapes the repository
- the file is not valid UTF-8
- the expected text does not exist
- the expected text appears multiple times

This deliberately gives the agent less authority than an unrestricted file-writing tool.

## Autonomous Debugging Loop

A typical successful run looks like:

```text
Inspect repository
      ↓
Read relevant code
      ↓
Inspect tests
      ↓
Identify likely root cause
      ↓
Apply patch
      ↓
Run tests
      ↓
Tests fail
      ↓
Use failure as new evidence
      ↓
Revise patch
      ↓
Run tests again
      ↓
Tests pass
      ↓
Finish
```

The agent has demonstrated this behavior during the seeded refresh-token bug, where its first modification was incomplete. It observed the failed test, made another modification, reran the tests, and successfully verified the final fix.

## Safety Boundaries

The agent operates under deterministic safety controls.

### Workspace isolation

Repository operations cannot escape the configured workspace through absolute paths or parent traversal.

### Restricted execution

The model cannot execute arbitrary shell commands.

Test execution is exposed through a dedicated allowlisted tool.

### Bounded autonomy

Runs have configurable limits for:

- maximum iterations
- maximum patch attempts
- test execution timeouts

### Verification requirement

After modifying code, the agent cannot successfully finish until a passing test execution occurs after the latest successful patch.

This requirement is enforced by application code rather than relying only on the LLM prompt.

### Untrusted repository content

Repository files are treated as untrusted input.

The agent's system instructions explicitly prevent comments, documentation, source files, or other repository content from overriding the agent's system-level instructions.

## Evaluation

The project includes an evaluation harness using seeded buggy repositories.

Each evaluation case is copied into a temporary workspace before execution so the original fixture remains unchanged.

Current benchmark cases cover:

| Case | Bug Type |
|---|---|
| Refresh token validator | Incorrect function usage |
| Email normalization | Incorrect data transformation |
| Request quota | Boundary-condition error |

### Latest measured run

```text
TOTAL CASES: 3
DIAGNOSED: 3
SUCCESSFUL FIXES: 3
VERIFIED FIXES: 3

FIX RATE: 100.0%
VERIFICATION RATE: 100.0%

AVG ITERATIONS: 8.67
AVG PATCH ATTEMPTS: 1.33
AVG TEST RUNS: 1.00
```

These numbers are generated from actual autonomous agent runs rather than manually assigned scores.

The benchmark is intentionally small and should not be interpreted as a general 100% debugging success rate. Its purpose is to provide a reproducible framework for measuring the agent as additional debugging cases are added.

## Observability

Every autonomous evaluation produces a structured trace.

Example:

```text
traces/
├── <trace-id>.json
├── <trace-id>.json
└── <trace-id>.json
```

Each trace records information such as:

```json
{
  "trace_id": "...",
  "bug_report": "...",
  "model": "...",
  "steps": [
    {
      "step": 1,
      "action": "list_directory",
      "arguments": {
        "path": "."
      },
      "success": true,
      "summary": "...",
      "error_type": null,
      "duration_ms": 1.4
    }
  ],
  "completion_status": "diagnosed",
  "final_diagnosis": "...",
  "total_duration_ms": 12345.6
}
```

This makes agent behavior inspectable instead of treating the LLM as a black box.

## Project Structure

```text
src/debugger_agent/
├── agent/
│   ├── actions.py
│   ├── decision.py
│   ├── executor.py
│   ├── runner.py
│   ├── state.py
│   └── state_updates.py
│
├── evaluation/
│   ├── models.py
│   └── runner.py
│
├── llm/
│   └── openai.py
│
├── observability/
│   ├── models.py
│   ├── storage.py
│   └── tracer.py
│
├── repository/
│   ├── models.py
│   └── workspace.py
│
└── tools/
    ├── filesystem.py
    ├── patching.py
    ├── search.py
    └── testing.py
```

## Running the Tests

Install the project:

```bash
pip install -e .
```

Run the complete test suite:

```bash
pytest -q
```

The current test suite contains 69+ automated tests covering repository isolation, filesystem operations, agent actions, decision handling, state transitions, execution, testing, patching, evaluation, tracing, and safety behavior.

## Running the Evaluation

Configure the model:

```env
OPENAI_API_KEY=your-key
OPENAI_MODEL=your-model
```

Then run:

```bash
python scripts/run_evaluation.py
```

The evaluation runner executes the seeded debugging cases, prints aggregate metrics, and saves structured traces under:

```text
traces/
```

## Design Decisions

### Why not give the model shell access?

Unrestricted shell access would make the agent significantly harder to control. Instead, capabilities are exposed as narrow tools with explicit schemas and validation.

### Why exact text replacement?

The patching mechanism is intentionally conservative. Exact replacements are easier to validate and constrain than unrestricted file writes.

A production version could move to structured diff application while preserving the same safety boundaries.

### Why use an LLM for decisions?

The purpose of the project is to test autonomous debugging behavior. Repository inspection, testing, and modification are deterministic tools, while the model decides which tool to use and how to react to observations.

### Why not use a vector database?

The current repository search problem does not require one. Adding a vector database would increase complexity without solving a demonstrated limitation.

The architecture can support more advanced retrieval later if evaluation results show that repository scale requires it.

## Limitations

The current implementation intentionally has several limitations:

- evaluation currently contains only a small number of seeded bugs
- patching uses exact text replacement rather than structured diffs
- only approved pytest execution is supported
- the system has primarily been evaluated on small Python repositories
- benchmark results should not be generalized beyond the included cases
- token and monetary cost tracking are not yet included in traces
- repository prompt-injection resistance is enforced through boundaries and instructions but has not yet been extensively adversarially evaluated

## Future Improvements

Potential extensions include:

- larger benchmark suites
- structured unified-diff patching
- token and cost accounting
- adversarial prompt-injection evaluations
- larger repository evaluation
- regression-specific metrics
- failure taxonomy reporting
- container-level repository isolation
- additional language and test-framework support

## Why I Built This

The goal of this project was to explore what makes an AI coding system an actual agent rather than an LLM call wrapped in an application.

The main engineering problems were not only generating code. They included controlling what the model is allowed to do, maintaining state across decisions, feeding real tool observations back into the model, recovering from failed fixes, enforcing deterministic verification, evaluating behavior, and making autonomous runs observable.

The result is a bounded debugging agent that can independently investigate a bug, modify code, observe the result, revise its approach, and verify a solution.