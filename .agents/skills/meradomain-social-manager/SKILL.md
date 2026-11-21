---
name: meradomain-social-manager
description: Autonomous social media campaign manager and copy auditor for MeraDomain (meradomain.in). Orchestrates multi-platform content generation, audits brand voice, and manages the cPanel approval queue.
---

# MeraDomain Social Media Manager Skill

This skill guides Google Antigravity agents in managing the social media presence for **MeraDomain** (`https://meradomain.in`).

## Core Responsibilities
1. **Content Ideation & Portfolio Mining**:
   - Extract case studies from `meradomain.in` and portfolio archives.
   - Pair engineering achievements with Indian and global business calendar hooks.
2. **Multi-Channel Copy Generation**:
   - Synthesize tailored copy for all 4 primary channels: LinkedIn, Instagram, Facebook, and Google Business Profile (GMB).
   - Enforce brand rules defined in `.agents/rules/meradomain-brand.md`.
3. **Branded Visual Plate Generation**:
   - Execute the Pillow visual engine (`local-worker/src/visuals/template_engine.py`) to render 1:1, 4:5, and 1.91:1 graphic assets featuring Deep Obsidian `#0B0F19`, Mera Gold `#D4AF37`, and Emerald `#10B981`.
4. **Approval Queue Ingestion & Audit**:
   - Sync drafts to `https://social.meradomain.in/api/posts.php`.
   - Inspect the queue for pending posts, audit readability and hashtag density, and propose improvements.

## Execution Commands

### Generate a Single Campaign:
```powershell
python local-worker/run_worker.py --generate --sync
```

### Batch Generate Weekly Content:
```powershell
python local-worker/run_worker.py --batch 5 --sync
```

### Trigger Publisher for Approved Due Posts:
```powershell
python local-worker/run_worker.py --publish
```

## Quality Checklist
Before marking any campaign ready for human approval, verify:
- [ ] **LinkedIn**: Does it include quantifiable metrics and executive tone?
- [ ] **Instagram**: Is there a scroll-stopping hook within the first 2 lines?
- [ ] **Facebook**: Does it address relatable MSME/founder bottlenecks with a community focus?
- [ ] **GMB**: Are local SEO keywords (Connaught Place, New Delhi, Web Design) included with a direct action button?
- [ ] **Visual Plate**: Are font hierarchy, gold badge, category pill, and domain stamp properly balanced?
