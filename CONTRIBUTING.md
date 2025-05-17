# Contributing to `pan-scm-sdk`

We welcome contributions to `pan-scm-sdk`! This document provides guidelines and instructions on how to contribute effectively.

## How to Contribute

- **Reporting Bugs**: If you find a bug, please open an issue with a clear description and steps to reproduce.
- **Suggesting Enhancements**: For feature requests or suggestions, open an issue with a detailed explanation.
- **Pull Requests**: Before submitting a pull request, ensure it does not duplicate existing work.

## Pull Request Process

1. Fork the repository and create your branch from `main`.
2. Make your changes, ensuring they adhere to the project's coding conventions:
   - Review `SDK_STYLING_GUIDE.md` for service file standards
   - Follow `CLAUDE_MODELS.md` for model creation
   - Use `SDK_SERVICE_TEMPLATE.py` as a starting point for new services
   - Adhere to `WINDSURF_RULES.md` for overall project standards
3. Write clear, concise commit messages and ensure your code passes all tests:
   - Run `make quality` to check linting and formatting
   - Run `make test` to execute all tests
   - Ensure test coverage exceeds 80%
4. Open a pull request with a comprehensive description of changes.

## Code of Conduct

Please adhere to the Code of Conduct to maintain a respectful and collaborative environment.

## Questions?

If you have any questions or need further clarification, feel free to open an issue or contact the project maintainers directly.

Thank you for contributing to `pan-scm-sdk`!
