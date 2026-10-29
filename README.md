# Zomi Multilingual Data Collection Bot

A small, open-source Telegram bot for collecting structured entries in **Zomi, Burmese, and English**. It is an early-stage project intended to make community language-data collection more accessible.

> **Status:** Early-stage prototype. The repository does not yet have automated tests or a documented public release process. Its potential community value should not be mistaken for verified widespread adoption.

## Why this project exists

Zomi is an underrepresented language in many digital tools and datasets. A simple Telegram submission workflow can help contributors collect and organize multilingual vocabulary and phrases for future community-led language resources.

The repository currently contains the collection bot, not a published dictionary dataset or a production-ready data platform.

## Current features

- A Telegram `/start` command that explains the submission format.
- Comma-separated submissions with **Zomi** and **Burmese** required.
- Optional **English** translation and **Category** (defaults to `General`).
- Storage of submitted entries in a Supabase table named `zomi_dictionary`.
- Storage of the submitting Telegram user's ID in the `added_by` field.
- A Python Flask webhook endpoint with Vercel routing configuration.

## Example submission

Send this as a normal message to the configured Telegram bot:

```text
Na dam hia?, နေကောင်းလား?, How are you?, Greeting
```

Format:

```text
Zomi, Burmese, English, Category
```

At least the first two comma-separated fields are required. Currently, the implementation splits on commas and does **not** support escaped commas inside a field.

## Technology

| Component | Technology |
| --- | --- |
| Bot | Python, pyTelegramBotAPI |
| Webhook server | Flask |
| Storage | Supabase |
| Deployment configuration | Vercel |

Dependencies are pinned in [`requirements.txt`](requirements.txt), and Vercel routing is defined in [`vercel.json`](vercel.json).

## Setup for maintainers and contributors

1. Clone this repository:

   ```bash
   git clone https://github.com/kimpuwork-design/zomi-telegram-bot.git
   cd zomi-telegram-bot
   ```

2. Use Python 3 and install the dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Create your own Telegram bot with BotFather and provision a Supabase project.

4. Configure these environment variables in your deployment environment:

   | Variable | Purpose |
   | --- | --- |
   | `TELEGRAM_TOKEN` | Telegram bot token |
   | `SUPABASE_URL` | Supabase project URL |
   | `SUPABASE_KEY` | Supabase API key with the permissions needed for inserts |

5. Ensure your Supabase database contains a `zomi_dictionary` table with compatible `zomi_text`, `burmese_text`, `english_text`, `category`, and `added_by` columns, and configure appropriate database access policies.

6. Deploy the Flask application (the repository includes Vercel routing to `/api/index`) and configure the Telegram webhook URL for your deployment.

**Security:** Never commit tokens, service-role keys, database credentials, or contributor data. Keep all secrets in deployment environment variables. The existing implementation is a prototype: review webhook authentication, input validation, rate limiting, database access policies, and error disclosure before using it in a sensitive or large-scale setting.

## Data and privacy

Entries are submitted by Telegram users and stored in Supabase. The current implementation records each submitter's Telegram user ID in `added_by`. Operators should clearly inform contributors about this processing, restrict database access, and establish appropriate retention and deletion procedures.

No collected dataset is distributed in this repository.

## Roadmap

These are **planned improvements**, not current features:

- Improve input validation and error handling.
- Authenticate and protect webhook requests.
- Add automated tests and CI checks.
- Expand deployment and database setup documentation.
- Establish a safe process for reviewing community submissions.
- Introduce transparent release and maintenance practices.

## Contributing

Bug reports, documentation improvements, security hardening, and pull requests are welcome. Open an issue before a substantial change so the design can be discussed.

Please **do not** post API keys, personal information, or unreviewed contributor data in issues or pull requests.

## Maintainer

Maintained by [kimpuwork-design](https://github.com/kimpuwork-design).

## License

This project's source code is available under the [MIT License](LICENSE). This does not automatically grant rights to third-party content or submitted language data.
