# MeraDomain Lead Studio — cPanel installation

This is a single-owner PHP application. It researches public businesses using OpenAI web search, stores prospects, prepares editable outreach, tracks follow-ups and exports CSV. It does not access Sales Navigator, scrape LinkedIn, find private email addresses, or send messages. A fit score is not buying intent. AI research must be verified.

## Requirements

- PHP 8.1 or newer; PDO MySQL, cURL, mbstring, OpenSSL and sessions enabled.
- MySQL 5.7+ or MariaDB with CREATE, SELECT, INSERT, UPDATE and DELETE permissions.
- HTTPS enabled for the app subdomain or directory.
- Outbound HTTPS to api.openai.com. Research requests can take 110 seconds; request a PHP/proxy timeout of at least 120 seconds. If your shared host cannot allow this, live research may require a different host.
- No Composer, Node.js, paid LinkedIn plan, cron or build command required.

## Upload

1. In cPanel, create a MySQL database and database user. Add the user to the database with the permissions above. Note the full names, including the cPanel prefix.
2. In File Manager, create `public_html/leads`. Upload the ZIP and extract the app files into that folder. If extraction creates an extra `meradomain-leads` folder, move its contents so `index.php` is directly in `public_html/leads`. Do not replace your main website.
3. Copy `config.example.php` into your account HOME directory, outside `public_html`, naming it `meradomain-leads-config.php`. Example: `/home/YOURACCOUNT/meradomain-leads-config.php`. The app default assumes `/home/YOURACCOUNT/public_html/leads`. For another location, change only `$configPath` in bootstrap.php to the absolute private config path.
4. Edit that private file in cPanel. Enter the database host, database name, username and password. Keep `charset=utf8mb4` in the DSN.
5. Create a NEW app password with at least 12 characters. In cPanel Terminal run `php public_html/leads/password-hash.php`, type the new password, then copy the returned hash into `password_hash` in the private configuration. Input is visible in Terminal; do not reuse another password. If Terminal is unavailable, ask your host to run this helper or use a trusted LOCAL PHP installation. Do not use an online password-hash website.
6. Keep `openai_key` blank to start without paid AI. Open `https://YOURDOMAIN/leads/` and log in. Database tables are created automatically. Add a test business manually and confirm that it survives signing out and back in.
7. To enable research, create a dedicated OpenAI API project and key, configure billing, and paste the key only in the private server configuration. ChatGPT Plus is separately billed. Never put the key in JavaScript, a public file, a lead note or a chat message. Suggested initial model: `gpt-4.1-mini`; if your account does not support it with web search, choose a currently compatible Responses API model.
8. Set `monthly_run_limit` (default 30). Every attempt reserves one run BEFORE calling the API, including errors. A call allows up to 3 tool calls and 3,500 output tokens. This is a request-volume limit, NOT a guaranteed INR spending ceiling. Review OpenAI usage/billing and account controls as well. No automatic runs are enabled.
9. Run one discovery search and inspect the source links. A paid live search has NOT been tested with your account: no API credentials were supplied during development.

## Recommended permissions and checks

- Private configuration: permissions 600 if PHP can read it; ask the host if your setup requires a different owner/group. App directories normally 755 and files 644.
- Confirm `https://YOURDOMAIN/leads/config.example.php` returns 403 and directory listing is disabled. The example contains no real key. Never upload the real config under public_html.
- Use a dedicated database. Back up that database and the private configuration before upgrades. CSV is a convenient data export, not a complete configuration backup.
- All business notes stay in your database. Search filters are sent to OpenAI; business research queries are sent through web search. Manual notes are not sent to AI by this version. API requests set `store:false`; provider retention policies still apply.
- Dates are UTC. No real contacts, sample companies or preloaded prospects are included.

## Use

Choose a market, an industry and a service, then click Find prospects. Research saves up to five businesses, with source links and a fit score. Existing website hosts are skipped; do-not-contact records remain excluded by this same domain check. Subsidiaries sharing one host are treated as one company.

Review evidence, open sources and check the proposed opportunity. Employee count, budget and intent remain unknown unless you verify them. Expand a prospect to change its stage, add notes, set a follow-up date and edit/copy a conversation starter. The message is a local template, not a separately AI-generated draft. The LinkedIn button opens a normal people search for you to use manually.

Follow-ups are dashboard reminders only: there are no email notifications or automatic sending. Search filtering runs locally on the saved records. CSV export includes all prospects and protects leading spreadsheet formula characters.

## Troubleshooting

- Setup needed: configuration file is not in the expected private location.
- Database unavailable: verify the full prefixed database names, password, host and user permissions. Enable required PHP extensions.
- HTTP 401/403 from research: check the API key and model/project access.
- HTTP 429: check provider billing and quotas; the application run cap can also return 429 with its own message.
- Timeout or non-JSON response: check hosting time limits, then API usage before retrying. The request may already have incurred charges. Completed-but-unsaved results are not recovered automatically.
- Zero saved: sources may be insufficient, or returned domains already exist. This is not a guarantee of five leads per call.

## Validation scope

Local checks cover PHP syntax, sign-in, CSRF, manual lead persistence, domain deduplication, stage updates, CSV export, output escaping, API authentication and missing-key handling, plus monthly quota enforcement with a local dummy key and zero quota. Local tests use SQLite; the same PDO statements support the configured MySQL path, but a live cPanel/MySQL deployment and paid API search still need verification after upload.
