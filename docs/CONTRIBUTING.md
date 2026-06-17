# Contributing to COMET Framework

Thank you for your interest in contributing to the COMET Framework! This document provides guidelines and procedures for participating in the development of this project. Whether you are reporting a bug, proposing a new model, improving documentation, or extending the simulation framework, your contributions are valued.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Reporting Bugs](#reporting-bugs)
- [Submitting Pull Requests](#submitting-pull-requests)
- [Code Style Guidelines](#code-style-guidelines)
- [Academic Contribution Process](#academic-contribution-process)
- [Development Setup](#development-setup)

---

## Code of Conduct

This project is committed to providing a welcoming and inclusive experience for everyone. Please be respectful, constructive, and professional in all interactions. Discriminatory, harassing, or otherwise unacceptable behavior will not be tolerated.

---

## Reporting Bugs

If you find a bug in the mathematical models, simulation framework, or paper build process, please open a GitHub Issue using the following template:

### Bug Report Template

**Title:** [Brief description of the bug]

**Description:**
A clear and concise description of what the bug is. Include the expected behavior and the actual behavior observed.

**Steps to Reproduce:**
1. List the exact steps or commands used to trigger the bug.
2. Include any relevant configuration files or parameter settings.
3. Provide the full error message or unexpected output.

**Environment:**
- OS: [e.g., Ubuntu 22.04, macOS 14, Windows 11]
- Python version: [e.g., 3.11.5]
- TeX distribution: [e.g., TeX Live 2024, MiKTeX 24.1]
- Git commit hash: [e.g., `abc1234`]

**Additional Context:**
Any other context that might help diagnose the issue, such as screenshots, log files, or reference to relevant model equations.

---

## Submitting Pull Requests

We welcome pull requests from the community. Please follow these steps to ensure a smooth review process:

### 1. Fork and Clone

Fork the repository and clone your fork locally:

```bash
git clone https://github.com/your-username/COMET-Framework.git
cd COMET-Framework
git remote add upstream https://github.com/your-organization/COMET-Framework.git
```

### 2. Create a Feature Branch

Create a descriptive branch name from the latest `main`:

```bash
git fetch upstream
git checkout upstream/main
git checkout -b fix/maturity-index-convergence
# or
git checkout -b feature/agent-based-simulation
# or
git checkout -b docs/troubleshooting-guide
```

Branch naming conventions:
- `fix/<short-description>` — bug fixes
- `feature/<short-description>` — new features or models
- `docs/<short-description>` — documentation changes
- `refactor/<short-description>` — code refactoring without behavior change

### 3. Make Your Changes

- Keep changes focused and atomic. One pull request should address one concern.
- Write clear commit messages. Use the imperative mood:
  ```
  Fix convergence test in maturity index model
  Add parameter sweep to simulation runner
  Update bibliography with recent citations
  ```
- Include tests for any new or modified code.

### 4. Run Tests and Validation

Before submitting, ensure everything passes:

```bash
# Run the test suite
python -m pytest tests/ -v

# Run linting
python -m flake8 models/ simulation/ scripts/

# Build the paper to verify LaTeX integrity
bash scripts/build_paper.sh
```

### 5. Push and Open a Pull Request

Push your branch to your fork:

```bash
git push origin fix/maturity-index-convergence
```

Open a pull request against the upstream `main` branch. In your PR description, include:

- **Summary** of the change and its motivation.
- **Related issues** (e.g., "Fixes #42" or "Closes #15").
- **Testing** performed and results observed.
- **Screenshots or output** if the change affects visual output or paper formatting.

### 6. Address Review Feedback

Maintainers will review your pull request. Be prepared to:
- Respond to questions and clarification requests.
- Make additional changes if requested.
- Keep the PR up to date with the latest `main` branch.

---

## Code Style Guidelines

All Python code in the COMET Framework follows **PEP 8** (Python Enhancement Proposal 8). We use automated linting tools to enforce consistency.

### General Rules

- **Line length:** maximum 88 characters (Black formatter default).
- **Indentation:** 4 spaces per level (no tabs).
- **Imports:** absolute imports, grouped in the order: standard library → third-party → local. Separate groups with a blank line.
- **Naming conventions:**
  - Variables and functions: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`
  - Module-level private symbols: `_leading_underscore`

### Docstrings

All public modules, classes, functions, and methods **must** include docstrings in Google-style format:

```python
def compute_omt(params, timesteps, dt=0.01):
    """Compute the Operations Maturity Trajectory over a given time horizon.

    Solves the logistic growth ODE for the Operations Maturity Index (OMI)
    using forward Euler integration with configurable step size.

    Args:
        params (dict): Dictionary of model parameters containing:
            - carrying_capacity (float): Asymptotic maturity level M*.
            - growth_rate (float): Intrinsic growth rate k.
            - initial_value (float): Initial maturity level OMI(0).
        timesteps (int): Number of discrete time steps to simulate.
        dt (float): Integration step size in arbitrary time units.
            Defaults to 0.01.

    Returns:
        numpy.ndarray: Array of shape (timesteps,) containing the
        maturity index values at each time step.

    Raises:
        ValueError: If params is missing required keys or contains
            non-positive values for growth_rate or carrying_capacity.

    Example:
        >>> params = {"carrying_capacity": 0.95, "growth_rate": 0.12, "initial_value": 0.15}
        >>> trajectory = compute_omt(params, timesteps=1000)
        >>> trajectory[-1]  # should approach carrying_capacity
        0.949...
    """
    ...
```

### Type Annotations

Use type annotations for all function signatures:

```python
from typing import Dict, List, Optional, Tuple
import numpy as np

def run_simulation(
    config_path: str,
    output_dir: str,
    models: Optional[List[str]] = None,
    verbose: bool = False,
) -> Dict[str, np.ndarray]:
    ...
```

### Mathematical Code

- Clearly comment equations with references to the paper (e.g., "Equation (3) in Section 2.2").
- Separate numerical solver logic from model parameter definitions.
- Validate inputs at module boundaries with descriptive error messages.

---

## Academic Contribution Process

The COMET Framework is both a software project and an academic publication. Contributions that introduce new mathematical models, theoretical extensions, or significant analytical results require additional review:

### Adding a New Mathematical Model

1. **Propose the model** by opening a GitHub Issue with the tag `model-proposal`. Include:
   - Mathematical formulation (equations, variables, parameters).
   - Theoretical justification and relation to existing COMET models.
   - Expected use cases and validation approach.

2. **Implement in Python** following the existing model module structure under `models/`:
   - Parameterized constructor with documented defaults.
   - Numerical solver with configurable integration method.
   - Unit tests with known analytical solutions or regression baselines.
   - Example usage in the module docstring.

3. **Update the paper** by adding the model description, equations, and references to the LaTeX source in `paper/`.

4. **Submit a pull request** with all code, tests, documentation, and paper changes. Academic pull requests will undergo review by at least two maintainers with domain expertise.

### Extending the Simulation Framework

Proposals for new simulation modes, coupling strategies, or output formats should follow the same Issue → Implementation → PR workflow. Ensure backward compatibility with existing configuration files.

---

## Development Setup

### Prerequisites

- Python 3.9 or later
- Git
- LaTeX distribution (TeX Live or MiKTeX) for paper builds
- Optional: pandoc for DOCX export

### Initial Setup

```bash
git clone https://github.com/your-organization/COMET-Framework.git
cd COMET-Framework

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt  # linting, testing, type-checking tools

# Verify installation
python -c "import comet; print(comet.__version__)"
```

### Running Tests

```bash
python -m pytest tests/ -v --cov=models --cov=simulation
```

### Code Formatting

```bash
python -m black models/ simulation/ tests/
python -m isort models/ simulation/ tests/
```

---

## Questions?

If you have questions that are not covered by this guide, please open a GitHub Issue with the tag `question`. We will respond as soon as possible.

Thank you for contributing to the COMET Framework!
