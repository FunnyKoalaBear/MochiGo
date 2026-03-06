"""
evaluate_coder.py – Analyse the coding quality of a contributor
based on their git commit history and source files in this repository.

Usage:
    python evaluate_coder.py [author]

If no author is provided, defaults to "FunnyKoalaBear".

The script produces a structured report covering:
  1. Commit hygiene    – count, message quality, iterative development
  2. Code volume       – lines added/deleted, net contribution
  3. Comment density   – inline comments + docstrings
  4. Structure & OOP   – classes, functions, module organisation
  5. Error handling    – try/except usage
  6. Code duplication  – near-identical file detection
  7. Feature breadth   – variety of subsystems touched

Each dimension is scored 0-10. A weighted average produces a final letter grade.
"""

import ast
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run(cmd: list[str]) -> str:
    """Run a subprocess and return stdout, or "" on error."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return r.stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def _clamp(value: float, lo: float = 0.0, hi: float = 10.0) -> float:
    return max(lo, min(hi, value))


# ---------------------------------------------------------------------------
# 1. Commit hygiene
# ---------------------------------------------------------------------------

def analyse_commits(author: str) -> dict:
    raw = _run(["git", "log", f"--author={author}", "--all", "--format=%s"])
    messages = [m.strip() for m in raw.splitlines() if m.strip()]
    count = len(messages)

    if count == 0:
        return {
            "commit_count": 0,
            "score": 0.0,
            "details": "No commits found for this author.",
        }

    # Message quality heuristics
    descriptive = 0
    for msg in messages:
        words = msg.split()
        # A descriptive message has ≥4 words and is not all caps
        if len(words) >= 4 and not msg.isupper():
            descriptive += 1

    # Iterative commits: look for progressive keywords
    progressive_keywords = re.compile(
        r"\b(fix|update|refactor|improve|add|remove|clean|test|initial|complete|migrat|"
        r"working|setup|track|support|feature|performance|optimis|bug|architecture)\b",
        re.IGNORECASE,
    )
    iterative = sum(1 for m in messages if progressive_keywords.search(m))

    quality_ratio = descriptive / count          # 0-1
    iterative_ratio = iterative / count          # 0-1

    # Score: base from commit count (max 10 at ~30 commits), quality bonus
    volume_score = _clamp(count / 3.0)           # saturates at 30 commits
    quality_score = quality_ratio * 5 + iterative_ratio * 5
    score = _clamp((volume_score + quality_score) / 2)

    return {
        "commit_count": count,
        "descriptive_messages": descriptive,
        "iterative_commits": iterative,
        "quality_ratio": round(quality_ratio, 2),
        "score": round(score, 1),
        "details": (
            f"{count} commits found. "
            f"{descriptive}/{count} messages are descriptive. "
            f"{iterative}/{count} show iterative development."
        ),
    }


# ---------------------------------------------------------------------------
# 2. Code volume
# ---------------------------------------------------------------------------

def analyse_volume(author: str) -> dict:
    raw = _run(["git", "log", f"--author={author}", "--all", "--numstat", "--format="])
    added = deleted = 0
    for line in raw.splitlines():
        parts = line.split("\t")
        if len(parts) == 3 and parts[0].isdigit() and parts[1].isdigit():
            added += int(parts[0])
            deleted += int(parts[1])

    net = added - deleted

    # Score: generous – 500+ net lines earns a solid score
    score = _clamp(net / 150.0)

    return {
        "lines_added": added,
        "lines_deleted": deleted,
        "net_lines": net,
        "score": round(score, 1),
        "details": f"{added} lines added, {deleted} deleted → {net} net lines of code.",
    }


# ---------------------------------------------------------------------------
# 3. Comment density  (inline # comments + docstrings)
# ---------------------------------------------------------------------------

def _count_comment_lines(source: str) -> tuple[int, int]:
    """Return (comment_lines, docstring_lines) for a Python source string."""
    comment_lines = 0
    try:
        tree = ast.parse(source)
    except SyntaxError:
        # Fallback: count raw # lines
        for line in source.splitlines():
            if line.strip().startswith("#"):
                comment_lines += 1
        return comment_lines, 0

    # Count docstrings via AST
    docstring_lines = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
            if (
                node.body
                and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
                and isinstance(node.body[0].value.value, str)
            ):
                docstring_lines += node.body[0].end_lineno - node.body[0].lineno + 1

    for line in source.splitlines():
        if line.strip().startswith("#"):
            comment_lines += 1

    return comment_lines, docstring_lines


def analyse_comments(py_files: list[Path]) -> dict:
    total_lines = comment_lines_total = docstring_lines_total = 0

    for fp in py_files:
        src = fp.read_text(errors="replace")
        lines = src.splitlines()
        total_lines += len(lines)
        c, d = _count_comment_lines(src)
        comment_lines_total += c
        docstring_lines_total += d

    if total_lines == 0:
        return {"score": 0.0, "details": "No Python source files found."}

    comment_ratio = (comment_lines_total + docstring_lines_total) / total_lines

    # Ideal comment ratio 15–30 %. Below 5 % is poor, above 50 % is over-commented.
    if comment_ratio < 0.05:
        score = comment_ratio / 0.05 * 4          # 0 → 4
    elif comment_ratio <= 0.30:
        score = 4 + (comment_ratio - 0.05) / 0.25 * 6  # 4 → 10
    else:
        score = _clamp(10 - (comment_ratio - 0.30) / 0.20 * 3)  # 10 → 7

    has_docstrings = docstring_lines_total > 0
    score = _clamp(score + (1.0 if has_docstrings else 0.0))

    return {
        "total_source_lines": total_lines,
        "comment_lines": comment_lines_total,
        "docstring_lines": docstring_lines_total,
        "comment_ratio": round(comment_ratio, 3),
        "score": round(_clamp(score), 1),
        "details": (
            f"Comment density: {comment_ratio:.1%} "
            f"({comment_lines_total} inline + {docstring_lines_total} docstring lines "
            f"over {total_lines} total lines). "
            f"{'Docstrings present.' if has_docstrings else 'No docstrings found.'}"
        ),
    }


# ---------------------------------------------------------------------------
# 4. Structure & OOP
# ---------------------------------------------------------------------------

def analyse_structure(py_files: list[Path]) -> dict:
    total_functions = total_classes = files_with_classes = 0
    total_func_lines: list[int] = []

    for fp in py_files:
        src = fp.read_text(errors="replace")
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue

        classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        funcs = [
            n for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        total_classes += len(classes)
        total_functions += len(funcs)
        if classes:
            files_with_classes += 1
        for f in funcs:
            length = (f.end_lineno or f.lineno) - f.lineno + 1
            total_func_lines.append(length)

    avg_func_len = (
        sum(total_func_lines) / len(total_func_lines) if total_func_lines else 0
    )
    # Short functions (≤20 lines) are a good sign
    short_func_ratio = (
        sum(1 for l in total_func_lines if l <= 20) / len(total_func_lines)
        if total_func_lines
        else 0
    )

    # Score components
    oop_score = _clamp(total_classes * 1.5)          # max 10 with ~7 classes
    func_score = _clamp(total_functions / 3.0)        # max 10 with ~30 functions
    length_score = short_func_ratio * 10              # 0–10

    score = _clamp((oop_score + func_score + length_score) / 3)

    return {
        "total_classes": total_classes,
        "total_functions": total_functions,
        "files_with_classes": files_with_classes,
        "avg_function_length": round(avg_func_len, 1),
        "short_function_ratio": round(short_func_ratio, 2),
        "score": round(score, 1),
        "details": (
            f"{total_classes} classes across {files_with_classes} files. "
            f"{total_functions} functions, avg length {avg_func_len:.0f} lines. "
            f"{short_func_ratio:.0%} of functions are ≤20 lines."
        ),
    }


# ---------------------------------------------------------------------------
# 5. Error handling
# ---------------------------------------------------------------------------

def analyse_error_handling(py_files: list[Path]) -> dict:
    total_functions = try_blocks = specific_except = bare_except = funcs_with_try = 0

    for fp in py_files:
        src = fp.read_text(errors="replace")
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue

        funcs = [
            n for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        total_functions += len(funcs)

        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                try_blocks += 1
                for handler in node.handlers:
                    if handler.type is None:
                        bare_except += 1
                    else:
                        specific_except += 1

            # Count functions that contain at least one try block
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                has_try = any(
                    isinstance(child, ast.Try) for child in ast.walk(node)
                )
                if has_try:
                    funcs_with_try += 1

    if total_functions == 0:
        return {"score": 0.0, "details": "No functions found."}

    # Coverage: fraction of functions that contain at least one try block
    coverage = funcs_with_try / total_functions
    specificity = (
        specific_except / max(specific_except + bare_except, 1)
        if (specific_except + bare_except) > 0 else 1.0
    )

    # Score: coverage (max 7) + specificity bonus (max 3)
    coverage_score = _clamp(coverage / 0.3 * 7)   # 30 % coverage → 7
    specificity_score = specificity * 3
    score = _clamp(coverage_score + specificity_score)

    return {
        "total_functions": total_functions,
        "functions_with_error_handling": funcs_with_try,
        "try_blocks": try_blocks,
        "specific_except_handlers": specific_except,
        "bare_except_handlers": bare_except,
        "error_coverage": round(coverage, 2),
        "handler_specificity": round(specificity, 2),
        "score": round(score, 1),
        "details": (
            f"{funcs_with_try}/{total_functions} functions contain error handling "
            f"({coverage:.0%} coverage, {try_blocks} try block(s) total). "
            f"{specific_except} specific handlers, {bare_except} bare 'except:' handlers."
        ),
    }


# ---------------------------------------------------------------------------
# 6. Code duplication  (simple line-hash approach)
# ---------------------------------------------------------------------------

def analyse_duplication(py_files: list[Path]) -> dict:
    """Check for blocks of ≥5 identical consecutive non-blank lines across files."""
    BLOCK = 5

    # Build a list of normalised lines per file
    file_lines: list[list[str]] = []
    for fp in py_files:
        lines = [
            l.strip()
            for l in fp.read_text(errors="replace").splitlines()
            if l.strip() and not l.strip().startswith("#")
        ]
        file_lines.append(lines)

    # Map each BLOCK-gram to a list of (file_idx, line_idx)
    ngram_map: dict[tuple, list] = defaultdict(list)
    for fi, lines in enumerate(file_lines):
        for i in range(len(lines) - BLOCK + 1):
            gram = tuple(lines[i : i + BLOCK])
            ngram_map[gram].append((fi, i))

    duplicate_blocks = sum(1 for locs in ngram_map.values() if len(locs) > 1)
    total_possible = sum(
        max(0, len(lines) - BLOCK + 1) for lines in file_lines
    )

    dup_ratio = duplicate_blocks / max(total_possible, 1)

    # Lower duplication is better; < 5 % is great, > 25 % is poor.
    # Score decreases linearly: 10 at 0 % → 0 at 25 %+
    score = _clamp(10 * (1 - dup_ratio / 0.25))

    return {
        "duplicate_blocks": duplicate_blocks,
        "total_code_blocks": total_possible,
        "duplication_ratio": round(dup_ratio, 3),
        "score": round(_clamp(score), 1),
        "details": (
            f"{duplicate_blocks} duplicate code block(s) "
            f"(≥{BLOCK}-line matches) out of {total_possible} possible. "
            f"Duplication ratio: {dup_ratio:.1%}."
        ),
    }


# ---------------------------------------------------------------------------
# 7. Feature breadth
# ---------------------------------------------------------------------------

def analyse_breadth(py_files: list[Path]) -> dict:
    """
    Look for evidence of multiple distinct subsystems or techniques
    (hardware I/O, networking, AI/ML, threading, file I/O, testing, etc.).

    The subsystem patterns are intentionally tailored to this project's
    technology stack. Adapt them for different codebases as needed.
    """
    subsystems = {
        "Hardware I/O":    re.compile(r"\b(pigpio|gpiozero|ssd1306|i2c|spi|sounddevice|pyaudio|aplay)\b"),
        "Networking":      re.compile(r"\b(fastapi|websocket|asyncio|requests|uvicorn)\b"),
        "AI / ML":         re.compile(r"\b(ollama|vosk|KaldiRecognizer|webrtcvad|openai|transformers)\b"),
        "Concurrency":     re.compile(r"\b(threading|Thread|asyncio|async\s+def|await)\b"),
        "File I/O":        re.compile(r"\b(open|write|json\.load|json\.dump|wave\.open|scipy\.io)\b"),
        "Image / Display": re.compile(r"\b(PIL|Image|ImageDraw|luma|canvas)\b"),
        "Logging / Tests": re.compile(r"\b(assert|unittest|pytest|logging\.)\b"),
        "NumPy / Signal":  re.compile(r"\b(numpy|np\.|scipy|frombuffer|astype)\b"),
    }

    detected: list[str] = []
    combined_src = "\n".join(
        fp.read_text(errors="replace") for fp in py_files
    )

    for name, pattern in subsystems.items():
        if pattern.search(combined_src):
            detected.append(name)

    breadth = len(detected)
    score = _clamp(breadth / len(subsystems) * 10)

    return {
        "subsystems_detected": detected,
        "breadth_count": breadth,
        "score": round(score, 1),
        "details": (
            f"{breadth}/{len(subsystems)} distinct subsystem(s) detected: "
            + (", ".join(detected) if detected else "none")
            + "."
        ),
    }


# ---------------------------------------------------------------------------
# Final report
# ---------------------------------------------------------------------------

WEIGHTS = {
    "Commit Hygiene":   0.15,
    "Code Volume":      0.10,
    "Comment Density":  0.15,
    "Structure & OOP":  0.20,
    "Error Handling":   0.20,
    "No Duplication":   0.10,
    "Feature Breadth":  0.10,
}

GRADE_THRESHOLDS = [
    (9.0, "A+"),
    (8.5, "A"),
    (8.0, "A-"),
    (7.5, "B+"),
    (7.0, "B"),
    (6.5, "B-"),
    (6.0, "C+"),
    (5.5, "C"),
    (5.0, "C-"),
    (4.0, "D"),
]


def letter_grade(score: float) -> str:
    for threshold, grade in GRADE_THRESHOLDS:
        if score >= threshold:
            return grade
    return "F"


def main():
    author = sys.argv[1] if len(sys.argv) > 1 else "FunnyKoalaBear"

    # Collect all .py files tracked by git (exclude __pycache__)
    raw = _run(["git", "ls-files", "*.py"])
    py_files = [
        Path(p)
        for p in raw.splitlines()
        if p.strip() and "__pycache__" not in p
    ]

    print(f"\n{'='*62}")
    print(f"  Coding Quality Report  —  Author: {author}")
    print(f"  Repository: {Path.cwd().name}")
    print(f"{'='*62}\n")

    results = {
        "Commit Hygiene":  analyse_commits(author),
        "Code Volume":     analyse_volume(author),
        "Comment Density": analyse_comments(py_files),
        "Structure & OOP": analyse_structure(py_files),
        "Error Handling":  analyse_error_handling(py_files),
        "No Duplication":  analyse_duplication(py_files),
        "Feature Breadth": analyse_breadth(py_files),
    }

    weighted_sum = 0.0
    for dimension, weight in WEIGHTS.items():
        r = results[dimension]
        score = r["score"]
        weighted_sum += score * weight

        bar_len = int(round(score))
        bar = "█" * bar_len + "░" * (10 - bar_len)
        print(f"  {dimension:<18s}  [{bar}]  {score:4.1f}/10")
        print(f"    {r['details']}")
        print()

    grade = letter_grade(weighted_sum)

    print(f"{'─'*62}")
    print(f"  Weighted Score : {weighted_sum:.2f} / 10")
    print(f"  Final Grade    : {grade}")
    print(f"{'='*62}\n")

    # Human-readable verdict
    if weighted_sum >= 8.0:
        verdict = "Excellent coder — clean architecture, good habits, impressive feature breadth."
    elif weighted_sum >= 6.5:
        verdict = "Solid coder — functional, well-structured code with room to grow."
    elif weighted_sum >= 5.0:
        verdict = "Developing coder — shows real capability; more focus on docs and error handling would help."
    else:
        verdict = "Early-stage coder — code works but needs more structure, commenting, and error handling."

    print(f"  Verdict: {verdict}\n")


if __name__ == "__main__":
    main()
