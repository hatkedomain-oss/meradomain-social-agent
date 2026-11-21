# MeraDomain Automated AI Social Media Manager

Autonomous multi-platform social media ideation, copywriting, branded visual generation, human-in-the-loop approval, and scheduling engine for **MeraDomain** (`https://meradomain.in` — *Build. Launch. Grow.*).

---

## 🏛️ System Architecture

```
meradomain-social-agent/
├── cpanel-web/                   # PHP/MySQL Web Approval Portal & cPanel Scheduler
│   ├── public/                   # Document root for social.meradomain.in
│   │   ├── index.php             # Mobile-friendly executive approval dashboard
│   │   ├── assets/               # CSS (Dark/Light mode) & reactive JS
│   │   └── uploads/              # Synced branded visual plates
│   ├── api/
│   │   ├── posts.php             # REST API (CRUD, status transitions, due queries)
│   │   └── upload.php            # Secure multipart image ingestion
│   ├── cron/
│   │   └── publisher.php         # cPanel Cron runner (due post processor)
│   ├── src/
│   │   ├── Database.php          # Secure PDO wrapper with prepared statements
│   │   ├── Auth.php              # API Key & session security
│   │   └── Publishers/           # Network-specific API dispatchers
│   ├── schema.sql                # Production MySQL database schema
│   └── .env.example              # Server environment template
│
├── local-worker/                 # Local Python AI & Visual Engine
│   ├── src/
│   │   ├── ideation/             # Portfolio case study mining & business calendar hooks
│   │   ├── copywriters/          # Gemini API platform-tailored prompts
│   │   ├── visuals/              # Pillow luxury visual plate generator (1:1, 4:5, 1.91:1)
│   │   ├── sync/                 # cPanel REST API client
│   │   └── executor/             # Session-based publishing runner
│   ├── config.py                 # Worker settings & brand profile
│   ├── run_worker.py             # Unified CLI entry point
│   └── requirements.txt          # Python dependencies
│
├── .agents/                      # Google Antigravity Rules & Skills
│   ├── rules/
│   │   └── meradomain-brand.md   # Brand rules, design tokens, platform voice guidelines
│   └── skills/
│       └── meradomain-social-manager/
│           └── SKILL.md          # Autonomous agent execution skill
│
└── .github/
    └── workflows/
        └── deploy.yml            # Automated CI/CD deployment to cPanel via FTPS
```

---

## 🚀 Quick Start Guide

### 1. Setting Up the cPanel Web Portal (`social.meradomain.in`)

1. **Create Subdomain**:
   - In cPanel, go to **Domains** ➔ **Create a New Domain**.
   - Set Domain: `social.meradomain.in`
   - Set Document Root: `public_html/social` (or `social.meradomain.in/public`)
2. **Create MySQL Database**:
   - Go to **MySQL Databases** in cPanel.
   - Create database (e.g. `meradomain_social`) and a user with full privileges.
   - Open **phpMyAdmin**, select the database, and import `cpanel-web/schema.sql`.
3. **Configure Environment**:
   - Copy `cpanel-web/.env.example` to `cpanel-web/.env` on your server and update:
     ```env
     APP_URL="https://social.meradomain.in"
     DB_NAME="your_cpanel_dbname"
     DB_USER="your_cpanel_dbuser"
     DB_PASS="your_cpanel_dbpassword"
     API_SECRET_KEY="your_chosen_api_secret_key"
     ```
4. **Setup cPanel Cron Job**:
   - Go to **Cron Jobs** in cPanel.
   - Set frequency to every 10 minutes (`*/10 * * * *`).
   - Command:
     ```bash
     /usr/local/bin/php -q /home/YOUR_CPANEL_USER/public_html/social/cron/publisher.php > /dev/null 2>&1
     ```

---

### 2. Setting Up the Local Python Worker

1. **Install Dependencies**:
   ```powershell
   cd local-worker
   python -m pip install -r requirements.txt
   ```
2. **Configure API Keys**:
   - Create `local-worker/.env` (or copy from parent):
     ```env
     GEMINI_API_KEY="your_google_gemini_api_key"
     CPANEL_API_URL="https://social.meradomain.in/api"
     CPANEL_API_KEY="your_chosen_api_secret_key"
     ```

---

### 3. Operating the AI Worker

#### Generate a Single Multi-Channel Campaign:
```powershell
python local-worker/run_worker.py --generate --sync
```

#### Batch Generate 5 Weekly Campaigns from Portfolio Wins:
```powershell
python local-worker/run_worker.py --batch 5 --sync
```

#### Dry-Run Locally (Preview Output Without Syncing):
```powershell
python local-worker/run_worker.py --generate
```

#### Run Scheduled Publisher (Publishes Approved Posts):
```powershell
python local-worker/run_worker.py --publish
```

---

## 🎨 Dual Publishing Architecture

Because Meta Graph API (`pages_manage_posts`, `instagram_content_publish`) and Google Business Profile API require formal business verification and app review, this system uses a **Dual-Engine Architecture**:
- **Approval & Queue Management**: Centrally managed on `social.meradomain.in`. Review posts, edit captions, and approve from any mobile device or browser.
- **Execution**: The local worker executes approved posts via persistent browser profiles in `data/browser_profiles/`, completely eliminating API permission roadblocks. Direct REST API publishing hooks are also wired for immediate use whenever OAuth developer tokens are provided.

---

## 🔄 CI/CD Automated Deployment

Every push to `main` modifying files in `cpanel-web/` triggers the GitHub Actions workflow (`.github/workflows/deploy.yml`).

Configure these repository secrets in GitHub (`Settings` ➔ `Secrets and variables` ➔ `Actions`):
- `CPANEL_FTP_SERVER` (e.g., `ftp.meradomain.in`)
- `CPANEL_FTP_USERNAME` (e.g., `deployer@meradomain.in`)
- `CPANEL_FTP_PASSWORD` (FTP account password)
- `CPANEL_TARGET_DIR` (e.g., `social.meradomain.in/`)
