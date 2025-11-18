# Contributing to OSINT Toolkit

Thank you for your interest in contributing to the OSINT Toolkit! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/OSINT.git`
3. Create a virtual environment: `python3 -m venv venv`
4. Activate the virtual environment: `source venv/bin/activate`
5. Install dependencies: `pip install -r requirements.txt`
6. Install dev dependencies: `pip install pytest pytest-cov black flake8`

## Development Workflow

1. Create a new branch for your feature: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Write tests for your changes
4. Run tests: `pytest`
5. Run code formatter: `black src/`
6. Run linter: `flake8 src/`
7. Commit your changes: `git commit -m "Description of changes"`
8. Push to your fork: `git push origin feature/your-feature-name`
9. Create a Pull Request

## Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write docstrings for all functions, classes, and modules
- Keep functions focused and modular
- Add comments for complex logic

## Testing

- Write unit tests for new features
- Maintain or improve code coverage
- Test edge cases and error conditions
- Use pytest fixtures for common test setup

## Adding a New Module

To add a new intelligence module:

1. Create a new file in `src/osint/modules/`
2. Inherit from `BaseModule` in `src/osint/core/base.py`
3. Implement the `collect()` method
4. Add the module to `src/osint/__init__.py`
5. Update CLI in `src/osint/cli.py`
6. Write tests in `tests/`
7. Update documentation

## Pull Request Guidelines

- Provide a clear description of the changes
- Reference any related issues
- Include tests for new functionality
- Update documentation as needed
- Ensure all tests pass
- Keep PRs focused on a single feature or fix

## Reporting Issues

When reporting issues, please include:

- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Python version and OS
- Relevant error messages or logs

## Questions?

Feel free to open an issue for questions or discussions about contributing.
