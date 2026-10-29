# Security Policy

This is an early-stage open-source project. Security issues are handled on a best-effort basis; there is no guaranteed response time or security support contract.

## Supported versions

Only the current `main` branch is considered for fixes. There are no officially supported releases.

## Reporting a vulnerability

**Do not publish secrets, personal data, reproduction credentials, or an exploitable vulnerability in a public GitHub issue.**

If GitHub's **Report a vulnerability** / private vulnerability reporting feature is enabled, please use it from the repository's **Security** tab. Otherwise, first contact the maintainer privately using contact options on the maintainer's GitHub profile. Do not publish technical details publicly until a safe disclosure channel is agreed.

Please include, when safe to share:
- A concise description of the impact
- Affected file or endpoint
- Minimal reproduction steps using dummy data
- Suggested remediation, if known

## Threat model and deployment guidance

This bot receives user-submitted Telegram messages via a public webhook and stores data in Supabase.

- **Webhook authentication:** A secret-token check is supported by the proposed security hardening change; configure `TELEGRAM_WEBHOOK_SECRET` in the deployment environment and the **same** secret in Telegram's `setWebhook` request. Without this configuration the webhook remains unauthenticated. Apply the change in a coordinated rollout to avoid losing messages.
- **Credentials:** Store Telegram and Supabase keys in deployment secrets, never in source code or issue reports. Rotate any exposed key immediately.
- **Data storage:** Restrict Supabase permissions and database policies to the minimum necessary. Never expose service-role credentials to clients.
- **Privacy:** Submitted entries include a Telegram user ID in the `added_by` field. Inform contributors and define an appropriate retention/deletion procedure.
- **Input:** Validate sizes and formats, monitor abuse, and avoid displaying internal database exceptions to contributors.
- **Dependencies:** Review dependency update pull requests and CI checks before merging.

The repository does not claim a completed independent security audit.
