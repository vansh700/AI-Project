"""Build a sandbox shell script that validates test-case targets inside a container."""


def build_validation_script(test_cases: list[dict], language: str) -> str:
    """Generate a shell script with embedded test cases — no runtime JSON parsing."""
    blocks = [_case_block(i, tc, language) for i, tc in enumerate(test_cases)]
    joined = "\n".join(blocks)

    return f"""#!/bin/sh
set -u
RESULTS="["
FIRST=1
{joined}
RESULTS="$RESULTS]"
echo "$RESULTS"
"""


def _case_block(index: int, test_case: dict, language: str) -> str:
    tc_id = _shell_safe(test_case.get("id", f"TC-{index + 1:03d}"))
    target = _shell_safe(test_case.get("target", ""))
    check = _check_block(language)

    return f"""
# --- {tc_id} ---
if [ "$FIRST" -eq 1 ]; then FIRST=0; else RESULTS="$RESULTS,"; fi
FILE="/repo/{target}"
if [ ! -f "$FILE" ]; then
  RESULTS="$RESULTS{{\\"testCaseId\\":\\"{tc_id}\\",\\"target\\":\\"{target}\\",\\"status\\":\\"failed\\",\\"message\\":\\"Target file not found\\",\\"durationMs\\":0}}"
else
{check}
  RESULTS="$RESULTS{{\\"testCaseId\\":\\"{tc_id}\\",\\"target\\":\\"{target}\\",\\"status\\":\\"$STATUS\\",\\"message\\":\\"$MSG\\",\\"durationMs\\":0}}"
fi
"""


def _check_block(language: str) -> str:
    if language in {"JavaScript", "TypeScript", "JavaScript (React)", "TypeScript (React)"}:
        return """  if node --check "$FILE" >/dev/null 2>&1; then
    STATUS="passed"; MSG="Syntax check passed"
  else
    STATUS="failed"; MSG="Syntax check failed"
  fi"""
    if language == "Python":
        return """  if python3 -m py_compile "$FILE" >/dev/null 2>&1; then
    STATUS="passed"; MSG="Syntax check passed"
  else
    STATUS="failed"; MSG="Syntax check failed"
  fi"""
    return '  STATUS="passed"; MSG="File exists"'


def _shell_safe(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')
