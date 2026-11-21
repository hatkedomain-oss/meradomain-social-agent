-- ==============================================================================
-- MeraDomain AI Social Media Manager
-- Database Schema for cPanel MySQL / MariaDB
-- Target Domain: social.meradomain.in (MeraDomain - Build. Launch. Grow.)
-- ==============================================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ------------------------------------------------------------------------------
-- Table: campaigns
-- High-level content ideation bundles (e.g., "Next.js 15 Case Study", "Diwali Growth Hook")
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `campaigns` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `title` VARCHAR(255) NOT NULL,
  `topic` VARCHAR(255) NULL,
  `source_type` VARCHAR(50) DEFAULT 'PORTFOLIO_WIN', -- PORTFOLIO_WIN, TREND, FESTIVAL, EVERGREEN
  `notes` TEXT NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_created (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- Table: posts
-- Platform-specific queued posts (LinkedIn, Instagram, Facebook, GMB)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `posts` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `campaign_id` INT NULL,
  `platform` ENUM('linkedin', 'instagram', 'facebook', 'gmb') NOT NULL,
  `post_text` MEDIUMTEXT NOT NULL,
  `hashtags` TEXT NULL,
  `cta_link` VARCHAR(500) DEFAULT 'https://meradomain.in',
  `cta_type` VARCHAR(50) DEFAULT 'LEARN_MORE', -- LEARN_MORE, CALL_NOW, VISIT_WEBSITE, BOOK_APPOINTMENT
  `media_url` VARCHAR(500) NOT NULL,
  `media_aspect` ENUM('square', 'portrait', 'landscape') DEFAULT 'square',
  `status` ENUM('DRAFT', 'PENDING_REVIEW', 'APPROVED', 'SCHEDULED', 'PUBLISHED', 'FAILED', 'REJECTED') DEFAULT 'PENDING_REVIEW',
  `scheduled_at` DATETIME NULL,
  `published_at` DATETIME NULL,
  `published_post_id` VARCHAR(255) NULL,
  `published_url` VARCHAR(1000) NULL,
  `error_log` TEXT NULL,
  `feedback_notes` TEXT NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_status_sched (`status`, `scheduled_at`),
  INDEX idx_platform (`platform`),
  INDEX idx_campaign (`campaign_id`),
  CONSTRAINT `fk_posts_campaign` FOREIGN KEY (`campaign_id`) REFERENCES `campaigns` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- Table: audit_logs
-- Tracks approvals, edits, rejections, and publisher dispatches
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `audit_logs` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `post_id` INT NULL,
  `action` VARCHAR(50) NOT NULL, -- CREATED, APPROVED, EDITED, REJECTED, DISPATCHED, PUBLISHED, FAILED
  `actor` VARCHAR(100) DEFAULT 'local-worker', -- local-worker, human-admin, cron-publisher
  `notes` TEXT NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_post (`post_id`),
  CONSTRAINT `fk_audit_post` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- Table: settings
-- Global configuration, security keys, and social channel states
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `settings` (
  `key_name` VARCHAR(100) PRIMARY KEY,
  `key_value` TEXT NULL,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- Seed Default Configuration
-- ------------------------------------------------------------------------------
INSERT INTO `settings` (`key_name`, `key_value`) VALUES
('app_title', 'MeraDomain Social Agent Studio'),
('brand_name', 'MeraDomain'),
('brand_tagline', 'Build. Launch. Grow.'),
('brand_website', 'https://meradomain.in'),
('brand_phone', '+91-9717075888'),
('api_secret_key', 'md_sec_live_9a72df81c8b74635a821038'),
('admin_password_hash', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi'), -- default: 'admin123'
('auto_schedule_interval_hours', '4'),
('timezone', 'Asia/Kolkata')
ON DUPLICATE KEY UPDATE `key_name` = `key_name`;

SET FOREIGN_KEY_CHECKS = 1;
