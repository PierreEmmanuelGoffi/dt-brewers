# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build and Run Commands
- Run app: `streamlit run app.py`
- Install dependencies: `pip install -r requirements.txt` 
- Lint: `pylint app.py api/*.py`

## Code Style Guidelines
- **Imports**: Standard library first, then third-party, then local modules
- **Formatting**: 4 spaces for indentation
- **Docstrings**: Use triple quotes for all functions/classes/modules
- **Naming**: snake_case for variables/functions, PascalCase for classes
- **Error Handling**: Use try/except with specific exceptions
- **Type Hints**: Not currently used but encouraged for new code
- **Comments**: Prefer self-explanatory code, add comments for complex logic
- **API Pattern**: Continue using the existing module-level `api` instance
- **Streamlit Practices**: Use session_state for persistent variables
- **Safety Features**: Always maintain safety checks for critical operations