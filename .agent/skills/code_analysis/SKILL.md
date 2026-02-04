---
name: code_analysis
description: A comprehensive guide and toolkit for analyzing Python code quality, structure, security, and logic.
---

# Code Analysis Skill

This skill provides a systematic approach to analyzing codebases. It includes steps for structural analysis, logic review, security auditing, and refactoring recommendations.

## Usage

When the user asks to "analyze the code", "review the architecture", or "check for bugs", follow this workflow.

## Tools

This skill includes a helper script located at `.agent/skills/code_analysis/scripts/analyze_structure.py`.
You can run it using:
`python .agent/skills/code_analysis/scripts/analyze_structure.py <absolute_path_to_file>`

## Workflow

### 1. Overview & Structure
First, get a high-level understanding of the file(s).
- **Action**: Run the `analyze_structure.py` script on key files.
- **Goal**: Identify classes, functions, dependencies, and high-complexity areas (Complexity > 10 requires attention).

### 2. Static Analysis & Code Style (Manual Review)
Review the code for adherence to Pythonic standards (PEP 8).
- **Naming**: Are variable/function names descriptive and snake_case? Class names CapWords?
- **Docstrings**: Do public modules, classes, and functions have docstrings?
- **Type Hinting**: Are type hints used? Are they accurate?
- **Imports**: Are imports organized? (Standard lib -> Third party -> Local).

### 3. Logic & Correctness
Deep dive into the implementation of complex functions.
- **Edge Cases**: Are empty inputs, None values, or types handled?
- **Error Handling**: Are `try/except` blocks specific (avoid bare `except:`)? Are errors logged?
- **Resource Management**: Are files and connections closed properly (use `with` context managers)?

### 4. Security Audit
Check for common vulnerabilities.
- **Secrets**: Are api keys or passwords hardcoded?
- **Injection**: (If SQL/Web) Are inputs sanitized? Parameterized queries used?
- **Input Validation**: Is all external input validated before use?

### 5. Performance
- **Loops**: Are there nested loops that could be optimized?
- **I/O**: Is I/O blocking the main thread inappropriately (e.g., in GUI apps)?
- **Data Structures**: Are the right data structures used (e.g., set for membership testing)?

### 6. Deliverable
Provide the user with a structured report containing:
1.  **Executive Summary**: Overall health of the code.
2.  **Structural Insights**: Output from the analysis script.
3.  **Critical Issues**: Bugs or security risks (Priority 1).
4.  **Improvement Suggestions**: Refactoring, styling, and optimization tips (Priority 2).
5.  **Refactoring Plan**: If requested, a step-by-step plan to fix the issues.
