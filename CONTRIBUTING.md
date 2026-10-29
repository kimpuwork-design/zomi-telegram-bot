# Contributing

Thank you for helping improve this early-stage multilingual data collection project.

## Before you start

- Check existing issues and pull requests.
- Open an issue describing larger feature proposals or behavior changes.
- Do not post API credentials, personal information, or collected contributor data.
- Keep examples and test fixtures synthetic.

## Local development and tests

1. Clone the repository and use Python 3.11.
2. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt pytest
   ```

3. Run tests:

   ```bash
   python -m pytest -q
   ```

Tests use mocked Telegram and Supabase modules and should not require real secrets.

## Pull requests

- Keep changes focused and explain motivation and risk.
- Add or update tests where behavior changes.
- Do not change existing production tokens, deployment settings, or data schemas without discussing migration steps.
- For webhook authentication changes, document how the Telegram `setWebhook` secret and environment variable will be coordinated.
- Never include actual language entries with identifiable contributor information.

## Style

- Follow the existing Python conventions.
- Prefer explicit validation and clear error messages that do not leak sensitive internals.
- Treat GitHub Actions CI as a minimum gate, not a substitute for deployment review.

The project is maintained on a best-effort basis and contributions may take time to review.
