<?php
/**
 * MeraDomain Social Agent - Human-in-the-Loop Approval Dashboard
 * Domain: social.meradomain.in
 */

declare(strict_types=1);

if (file_exists(__DIR__ . '/src/Database.php')) {
    require_once __DIR__ . '/src/Database.php';
    require_once __DIR__ . '/src/Auth.php';
} else {
    require_once __DIR__ . '/../src/Database.php';
    require_once __DIR__ . '/../src/Auth.php';
}

use MeraDomain\Auth;

Auth::startSession();
$csrfToken = Auth::getCsrfToken();
?>
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>MeraDomain Social Agent • Executive Approval Studio</title>
    
    <!-- Favicon -->
    <link rel="icon" type="image/png" href="/assets/images/meradomain-favicon.png">
    
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Playfair+Display:ital,wght@0,600;1,600&display=swap" rel="stylesheet">
    
    <!-- Icons & Styling -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="/assets/css/style.css">
</head>
<body class="antialiased selection:bg-yellow-500 selection:text-black pb-24 md:pb-12">

    <!-- Top Executive Navigation Bar -->
    <header class="sticky top-0 z-40 bg-[#0b0f19]/80 backdrop-blur-md border-b border-yellow-500/20 px-4 lg:px-8 py-3.5 transition-colors">
        <div class="max-w-7xl mx-auto flex items-center justify-between">
            
            <!-- Brand Identity -->
            <div class="flex items-center gap-3">
                <img src="/assets/images/meradomain-logo-badge.png" alt="MeraDomain Logo" class="h-9 w-auto drop-shadow-[0_0_8px_rgba(212,175,55,0.4)]">
                <div>
                    <div class="flex items-center gap-2">
                        <span class="font-extrabold text-base tracking-tight gold-gradient-text">MeraDomain</span>
                        <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-yellow-500/10 text-yellow-400 border border-yellow-500/30 uppercase tracking-widest">Social Agent</span>
                    </div>
                    <p class="text-[11px] text-slate-400 font-medium hidden sm:block">meradomain.in • Build. Launch. Grow.</p>
                </div>
            </div>

            <!-- Global Action Controls & KPI Bar -->
            <div class="flex items-center gap-3 sm:gap-4">
                
                <!-- KPI Counters -->
                <div class="hidden md:flex items-center gap-2 text-xs bg-slate-900/60 border border-slate-800 rounded-full px-3 py-1.5 shadow-inner">
                    <span class="flex items-center gap-1.5 text-yellow-400 font-semibold">
                        <span class="w-2 h-2 rounded-full bg-yellow-400 animate-pulse"></span>
                        <span id="kpi-pending">0</span> Pending
                    </span>
                    <span class="text-slate-600">|</span>
                    <span class="text-blue-400 font-semibold">
                        <span id="kpi-approved">0</span> Approved
                    </span>
                    <span class="text-slate-600">|</span>
                    <span class="text-emerald-400 font-semibold">
                        <span id="kpi-published">0</span> Live
                    </span>
                </div>

                <!-- Refresh Button -->
                <button id="refresh-btn" title="Refresh Feed" class="w-9 h-9 rounded-xl bg-slate-800/80 hover:bg-slate-700 border border-slate-700 text-slate-300 flex items-center justify-center transition shadow-sm">
                    <i class="fas fa-sync-alt text-xs"></i>
                </button>

                <!-- Light/Dark Mode Toggle -->
                <button id="theme-toggle-btn" title="Toggle Theme" class="w-9 h-9 rounded-xl bg-slate-800/80 hover:bg-slate-700 border border-slate-700 flex items-center justify-center transition shadow-sm">
                    <i id="theme-icon" class="fas fa-sun text-yellow-400 text-xs"></i>
                </button>

                <!-- Outbound Lead Studio Button -->
                <a href="/leads/index.php?key=MeraDomain@2026!" target="_blank" title="Open Outbound Lead Studio in New Tab" class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-yellow-500/10 hover:bg-yellow-500/20 text-yellow-400 border border-yellow-500/30 text-xs font-semibold transition shadow-sm">
                    <i class="fas fa-crosshairs text-xs"></i>
                    <span class="hidden sm:inline">Lead Studio ↗</span>
                </a>
            </div>
        </div>
    </header>

    <!-- Main Workspace Container -->
    <main class="max-w-7xl mx-auto px-4 lg:px-8 pt-6">

        <!-- Filter Subnav & Controls -->
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-800/80">
            
            <!-- Platform Pills -->
            <div class="flex items-center gap-1.5 overflow-x-auto pb-2 md:pb-0 scrollbar-none">
                <button class="platform-btn px-3.5 py-1.5 rounded-full text-xs transition whitespace-nowrap bg-yellow-500 text-black font-bold" data-platform="all">
                    <i class="fas fa-layer-group mr-1.5"></i> All Channels
                </button>
                <button class="platform-btn px-3.5 py-1.5 rounded-full text-xs transition whitespace-nowrap bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300" data-platform="linkedin">
                    <i class="fab fa-linkedin text-sky-400 mr-1.5"></i> LinkedIn
                </button>
                <button class="platform-btn px-3.5 py-1.5 rounded-full text-xs transition whitespace-nowrap bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300" data-platform="instagram">
                    <i class="fab fa-instagram text-pink-400 mr-1.5"></i> Instagram
                </button>
                <button class="platform-btn px-3.5 py-1.5 rounded-full text-xs transition whitespace-nowrap bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300" data-platform="facebook">
                    <i class="fab fa-facebook text-blue-400 mr-1.5"></i> Facebook
                </button>
                <button class="platform-btn px-3.5 py-1.5 rounded-full text-xs transition whitespace-nowrap bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300" data-platform="gmb">
                    <i class="fab fa-google text-emerald-400 mr-1.5"></i> Google Business
                </button>
            </div>

            <!-- Status Tabs -->
            <div class="flex items-center gap-4 text-xs font-medium border-b md:border-b-0 border-slate-800 pb-2 md:pb-0">
                <button class="status-tab pb-1 transition border-b-2 border-yellow-500 text-yellow-400 font-bold" data-status="PENDING_REVIEW">
                    Pending Review
                </button>
                <button class="status-tab pb-1 transition border-b-2 border-transparent text-slate-400 hover:text-slate-200" data-status="APPROVED">
                    Approved & Scheduled
                </button>
                <button class="status-tab pb-1 transition border-b-2 border-transparent text-slate-400 hover:text-slate-200" data-status="PUBLISHED">
                    Live Published
                </button>
                <button class="status-tab pb-1 transition border-b-2 border-transparent text-slate-400 hover:text-slate-200" data-status="REJECTED">
                    Rejected
                </button>
            </div>
        </div>

        <!-- Loading Spinner -->
        <div id="loading-indicator" class="flex flex-col items-center justify-center py-20 gap-3">
            <div class="w-9 h-9 border-3 border-yellow-500/20 border-t-yellow-500 rounded-full animate-spin"></div>
            <p class="text-xs text-slate-400 font-mono tracking-wide">Syncing approval queue with cPanel API...</p>
        </div>

        <!-- Empty State -->
        <div id="empty-state" class="hidden flex flex-col items-center justify-center py-24 text-center">
            <div class="w-16 h-16 rounded-2xl bg-yellow-500/10 border border-yellow-500/20 flex items-center justify-center mb-4 text-yellow-400 text-2xl">
                <i class="fas fa-check-double"></i>
            </div>
            <h3 class="text-base font-bold text-slate-200">All Caught Up!</h3>
            <p class="text-xs text-slate-400 max-w-sm mt-1">No posts match the selected filter. Run the local AI worker to synthesize fresh campaigns from portfolio wins.</p>
        </div>

        <!-- Posts Responsive Grid -->
        <div id="posts-container" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 pt-6">
            <!-- Dynamically populated via app.js -->
        </div>

    </main>

    <!-- Inline Edit Modal -->
    <div id="edit-modal" class="hidden fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
        <div class="glass-panel w-full max-w-xl p-6 relative border border-yellow-500/30">
            <div class="flex items-center justify-between pb-4 border-b border-slate-800">
                <div class="flex items-center gap-2">
                    <i class="fas fa-edit text-yellow-400"></i>
                    <h3 class="text-sm font-bold text-slate-200">Refine Post Content & Schedule</h3>
                </div>
                <button onclick="closeEditModal()" class="text-slate-400 hover:text-slate-200">
                    <i class="fas fa-times"></i>
                </button>
            </div>

            <form id="edit-post-form" class="mt-4 space-y-4">
                <input type="hidden" id="edit-post-id">
                
                <div>
                    <label class="block text-xs font-semibold text-slate-300 mb-1">Post Copy</label>
                    <textarea id="edit-post-text" rows="6" class="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-xs text-slate-100 focus:outline-none focus:border-yellow-500" required></textarea>
                </div>

                <div>
                    <label class="block text-xs font-semibold text-slate-300 mb-1">Hashtags</label>
                    <input type="text" id="edit-hashtags" class="w-full bg-slate-900 border border-slate-700 rounded-xl p-2.5 text-xs text-slate-100 focus:outline-none focus:border-yellow-500">
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-xs font-semibold text-slate-300 mb-1">Scheduled Time</label>
                        <input type="datetime-local" id="edit-scheduled-at" class="w-full bg-slate-900 border border-slate-700 rounded-xl p-2.5 text-xs text-slate-100 focus:outline-none focus:border-yellow-500">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-300 mb-1">CTA Destination Link</label>
                        <input type="url" id="edit-cta-link" class="w-full bg-slate-900 border border-slate-700 rounded-xl p-2.5 text-xs text-slate-100 focus:outline-none focus:border-yellow-500">
                    </div>
                </div>

                <div class="pt-4 border-t border-slate-800 flex justify-end gap-2.5">
                    <button type="button" onclick="closeEditModal()" class="px-4 py-2 rounded-xl text-xs font-medium text-slate-400 hover:bg-slate-800 transition">Cancel</button>
                    <button type="submit" class="px-5 py-2 rounded-xl text-xs font-bold bg-yellow-500 hover:bg-yellow-400 text-black transition shadow-md">Save Changes</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Image Lightbox Modal -->
    <div id="lightbox-modal" class="hidden fixed inset-0 z-50 bg-black/90 backdrop-blur-md flex items-center justify-center p-4 cursor-pointer" onclick="closeLightbox()">
        <img id="lightbox-img" src="" alt="High-Res Plate" class="max-w-full max-h-[90vh] rounded-xl shadow-2xl object-contain border border-yellow-500/20">
    </div>

    <!-- Toast Notification Banner -->
    <div id="toast" class="fixed top-5 right-5 z-50 px-4 py-2.5 rounded-xl text-xs font-bold shadow-xl transition-all duration-300 opacity-0 pointer-events-none"></div>

    <script src="/assets/js/app.js"></script>
</body>
</html>
