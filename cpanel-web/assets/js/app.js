/**
 * MeraDomain Social Agent - Human-in-the-Loop Web Portal Script
 * Target: social.meradomain.in
 */

const AppState = {
    currentStatus: 'PENDING_REVIEW',
    currentPlatform: 'all',
    posts: [],
    summary: {},
    activeEditingPost: null
};

// -----------------------------------------------------------------------------
// DOM Ready & Theme Initialization
// -----------------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    setupEventListeners();
    fetchPosts();
});

function initTheme() {
    const savedTheme = localStorage.getItem('md_theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'dark';
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('md_theme', next);
    updateThemeIcon(next);
}

function updateThemeIcon(theme) {
    const icon = document.getElementById('theme-icon');
    if (icon) {
        icon.className = theme === 'dark' ? 'fas fa-sun text-yellow-400' : 'fas fa-moon text-slate-700';
    }
}

// -----------------------------------------------------------------------------
// Event Listeners
// -----------------------------------------------------------------------------
function setupEventListeners() {
    // Theme toggle button
    const themeBtn = document.getElementById('theme-toggle-btn');
    if (themeBtn) {
        themeBtn.addEventListener('click', toggleTheme);
    }

    // Refresh queue button
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => fetchPosts(true));
    }

    // Status filter tabs
    document.querySelectorAll('.status-tab').forEach(tab => {
        tab.addEventListener('click', (e) => {
            document.querySelectorAll('.status-tab').forEach(t => t.classList.remove('active', 'border-yellow-500', 'text-yellow-400', 'font-bold'));
            e.currentTarget.classList.add('active', 'border-yellow-500', 'text-yellow-400', 'font-bold');
            AppState.currentStatus = e.currentTarget.dataset.status;
            renderPosts();
        });
    });

    // Platform filter buttons
    document.querySelectorAll('.platform-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.platform-btn').forEach(b => b.classList.remove('bg-yellow-500', 'text-black', 'font-bold'));
            e.currentTarget.classList.add('bg-yellow-500', 'text-black', 'font-bold');
            AppState.currentPlatform = e.currentTarget.dataset.platform;
            renderPosts();
        });
    });

    // Edit modal form submission
    const editForm = document.getElementById('edit-post-form');
    if (editForm) {
        editForm.addEventListener('submit', handleSaveEdit);
    }
}

// -----------------------------------------------------------------------------
// API Communications
// -----------------------------------------------------------------------------
async function fetchPosts(showToast = false) {
    const loader = document.getElementById('loading-indicator');
    if (loader) loader.classList.remove('hidden');

    try {
        const response = await fetch('/api/posts.php');
        if (!response.ok) throw new Error('Failed to fetch posts from API');
        const data = await response.json();

        if (data.success) {
            AppState.posts = data.posts || [];
            AppState.summary = data.summary || {};
            updateKpiCounters();
            renderPosts();
            if (showToast) showNotification('Queue refreshed successfully', 'success');
        }
    } catch (err) {
        console.error('API Error:', err);
        showNotification('Unable to connect to cPanel API', 'error');
    } finally {
        if (loader) loader.classList.add('hidden');
    }
}

function updateKpiCounters() {
    const pendingEl = document.getElementById('kpi-pending');
    const approvedEl = document.getElementById('kpi-approved');
    const publishedEl = document.getElementById('kpi-published');

    if (pendingEl) pendingEl.textContent = AppState.summary['PENDING_REVIEW'] || 0;
    if (approvedEl) approvedEl.textContent = (AppState.summary['APPROVED'] || 0) + (AppState.summary['SCHEDULED'] || 0);
    if (publishedEl) publishedEl.textContent = AppState.summary['PUBLISHED'] || 0;
}

// -----------------------------------------------------------------------------
// Post Actions (Approve, Reject, Quick Publish)
// -----------------------------------------------------------------------------
async function updatePostStatus(postId, newStatus, feedbackNotes = null, scheduledAt = null) {
    try {
        const payload = {
            id: postId,
            status: newStatus
        };
        if (feedbackNotes) payload.feedback_notes = feedbackNotes;
        if (scheduledAt) payload.scheduled_at = scheduledAt;

        const res = await fetch('/api/posts.php', {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (data.success) {
            showNotification(`Post #${postId} marked as ${newStatus}`, 'success');
            // Update local memory and re-render
            const index = AppState.posts.findIndex(p => p.id === postId);
            if (index !== -1) {
                AppState.posts[index] = data.post;
            }
            await fetchPosts();
        } else {
            showNotification(data.error || 'Failed to update post', 'error');
        }
    } catch (err) {
        console.error('Update Error:', err);
        showNotification('Network error while updating post', 'error');
    }
}

function approvePost(postId) {
    // Default schedule: today in 2 hours or next business window
    const now = new Date();
    now.setHours(now.getHours() + 2);
    const scheduleStr = now.toISOString().slice(0, 19).replace('T', ' ');
    updatePostStatus(postId, 'APPROVED', null, scheduleStr);
}

function rejectPost(postId) {
    const reason = prompt('Please enter rejection feedback for the AI agent (e.g., "Make CTA more direct"):');
    if (reason !== null) {
        updatePostStatus(postId, 'REJECTED', reason.trim() || 'Rejected by reviewer');
    }
}

function publishNow(postId) {
    if (confirm('Publish this post immediately across selected channels?')) {
        updatePostStatus(postId, 'APPROVED', null, new Date().toISOString().slice(0, 19).replace('T', ' '));
    }
}

// -----------------------------------------------------------------------------
// Inline Edit Modal
// -----------------------------------------------------------------------------
function openEditModal(postId) {
    const post = AppState.posts.find(p => p.id === postId);
    if (!post) return;

    AppState.activeEditingPost = post;
    document.getElementById('edit-post-id').value = post.id;
    document.getElementById('edit-post-text').value = post.post_text;
    document.getElementById('edit-hashtags').value = post.hashtags || '';
    document.getElementById('edit-scheduled-at').value = post.scheduled_at ? post.scheduled_at.replace(' ', 'T').slice(0, 16) : '';
    document.getElementById('edit-cta-link').value = post.cta_link || 'https://meradomain.in';

    document.getElementById('edit-modal').classList.remove('hidden');
}

function closeEditModal() {
    document.getElementById('edit-modal').classList.add('hidden');
    AppState.activeEditingPost = null;
}

async function handleSaveEdit(e) {
    e.preventDefault();
    const id = parseInt(document.getElementById('edit-post-id').value, 10);
    const postText = document.getElementById('edit-post-text').value;
    const hashtags = document.getElementById('edit-hashtags').value;
    const scheduledAt = document.getElementById('edit-scheduled-at').value;
    const ctaLink = document.getElementById('edit-cta-link').value;

    try {
        const payload = {
            id,
            post_text: postText,
            hashtags,
            cta_link: ctaLink,
            scheduled_at: scheduledAt ? scheduledAt.replace('T', ' ') + ':00' : null
        };

        const res = await fetch('/api/posts.php', {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (data.success) {
            showNotification('Post edits saved successfully', 'success');
            closeEditModal();
            await fetchPosts();
        } else {
            showNotification(data.error || 'Failed to save edits', 'error');
        }
    } catch (err) {
        console.error('Save Edit Error:', err);
        showNotification('Network error while saving edits', 'error');
    }
}

// -----------------------------------------------------------------------------
// Post Rendering & Social Mockups
// -----------------------------------------------------------------------------
function renderPosts() {
    const container = document.getElementById('posts-container');
    const emptyState = document.getElementById('empty-state');
    if (!container) return;

    // Filter by status & platform
    const filtered = AppState.posts.filter(p => {
        const matchStatus = (AppState.currentStatus === 'ALL') || (p.status === AppState.currentStatus);
        const matchPlatform = (AppState.currentPlatform === 'all') || (p.platform === AppState.currentPlatform);
        return matchStatus && matchPlatform;
    });

    container.innerHTML = '';

    if (filtered.length === 0) {
        if (emptyState) emptyState.classList.remove('hidden');
        return;
    }

    if (emptyState) emptyState.classList.add('hidden');

    filtered.forEach(post => {
        const card = document.createElement('div');
        card.className = 'mockup-card glass-panel p-5 relative border border-slate-800';
        card.innerHTML = generateMockupHtml(post);
        container.appendChild(card);
    });
}

function generateMockupHtml(post) {
    const isPending = post.status === 'PENDING_REVIEW';
    const isApproved = post.status === 'APPROVED' || post.status === 'SCHEDULED';
    const isPublished = post.status === 'PUBLISHED';

    let platformBadgeClass = 'badge-linkedin';
    let platformIcon = 'fab fa-linkedin';
    let platformName = 'LinkedIn Post';

    if (post.platform === 'instagram') {
        platformBadgeClass = 'badge-instagram';
        platformIcon = 'fab fa-instagram';
        platformName = 'Instagram Feed / Reel';
    } else if (post.platform === 'facebook') {
        platformBadgeClass = 'badge-facebook';
        platformIcon = 'fab fa-facebook';
        platformName = 'Facebook Page Post';
    } else if (post.platform === 'gmb') {
        platformBadgeClass = 'badge-gmb';
        platformIcon = 'fab fa-google';
        platformName = 'Google Business Profile';
    }

    // Media element
    const mediaHtml = post.media_url ? `
        <div class="preview-window rounded-xl my-4 overflow-hidden border border-slate-700/50 cursor-pointer" onclick="zoomImage('${post.media_url}')">
            <img src="${post.media_url}" alt="Post Visual Plate" loading="lazy" class="hover:scale-[1.02] transition-transform duration-300">
        </div>
    ` : '';

    // Hashtags chips
    const hashtagsHtml = post.hashtags ? `
        <div class="mt-3 flex flex-wrap gap-1.5 text-xs text-yellow-500/80 font-mono">
            ${post.hashtags.split(' ').filter(h => h.startsWith('#')).map(h => `<span class="bg-yellow-500/10 px-2 py-0.5 rounded-full border border-yellow-500/20">${h}</span>`).join('')}
        </div>
    ` : '';

    // GMB CTA Button Simulation
    const ctaButtonHtml = (post.platform === 'gmb') ? `
        <div class="mt-3 pt-3 border-t border-slate-700/50 flex items-center justify-between">
            <span class="text-xs text-slate-400 font-medium">Action Button:</span>
            <a href="${post.cta_link}" target="_blank" class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 shadow-sm">
                <span>${post.cta_type.replace('_', ' ')}</span>
                <i class="fas fa-external-link-alt text-[10px]"></i>
            </a>
        </div>
    ` : '';

    return `
        <!-- Card Header -->
        <div class="flex items-center justify-between pb-3 border-b border-slate-800">
            <div class="flex items-center gap-2.5">
                <span class="px-2.5 py-1 rounded-full text-xs font-semibold flex items-center gap-1.5 ${platformBadgeClass}">
                    <i class="${platformIcon}"></i>
                    <span>${platformName}</span>
                </span>
                <span class="text-xs text-slate-400">#${post.id}</span>
            </div>
            <div class="flex items-center gap-2">
                <span class="px-2 py-0.5 rounded text-[11px] font-bold ${getStatusBadgeClass(post.status)}">
                    ${post.status}
                </span>
            </div>
        </div>

        <!-- Post Content Simulation -->
        <div class="py-3 flex-1 flex flex-col justify-between">
            <div>
                <p class="post-copy text-sm text-slate-200">${escapeHtml(post.post_text)}</p>
                ${hashtagsHtml}
            </div>
            ${mediaHtml}
            ${ctaButtonHtml}
        </div>

        <!-- Meta info (Schedule / Campaign) -->
        <div class="text-[11px] text-slate-400 py-2 border-t border-slate-800/80 flex items-center justify-between">
            <span><i class="far fa-clock mr-1 text-yellow-400"></i> ${post.scheduled_at ? post.scheduled_at : 'Not Scheduled'}</span>
            ${post.campaign_title ? `<span class="truncate max-w-[150px]"><i class="fas fa-folder text-slate-500 mr-1"></i> ${escapeHtml(post.campaign_title)}</span>` : ''}
        </div>

        <!-- Action Controls -->
        <div class="pt-3 border-t border-slate-800 flex items-center gap-2">
            ${isPending ? `
                <button onclick="approvePost(${post.id})" class="flex-1 bg-yellow-500 hover:bg-yellow-400 text-black py-2 px-3 rounded-lg text-xs font-bold transition flex items-center justify-center gap-1.5 shadow-md">
                    <i class="fas fa-check"></i>
                    <span>Approve</span>
                </button>
                <button onclick="openEditModal(${post.id})" class="bg-slate-800 hover:bg-slate-700 text-slate-200 py-2 px-3 rounded-lg text-xs font-medium transition flex items-center gap-1 border border-slate-700">
                    <i class="fas fa-edit"></i>
                    <span>Edit</span>
                </button>
                <button onclick="rejectPost(${post.id})" class="bg-red-500/10 hover:bg-red-500/20 text-red-400 py-2 px-3 rounded-lg text-xs font-medium transition border border-red-500/20">
                    <i class="fas fa-times"></i>
                </button>
            ` : ''}

            ${isApproved ? `
                <button onclick="publishNow(${post.id})" class="flex-1 bg-blue-600 hover:bg-blue-500 text-white py-2 px-3 rounded-lg text-xs font-bold transition flex items-center justify-center gap-1.5">
                    <i class="fas fa-paper-plane"></i>
                    <span>Publish Now</span>
                </button>
                <button onclick="openEditModal(${post.id})" class="bg-slate-800 hover:bg-slate-700 text-slate-200 py-2 px-3 rounded-lg text-xs font-medium transition border border-slate-700">
                    <i class="fas fa-edit"></i>
                    <span>Reschedule</span>
                </button>
            ` : ''}

            ${isPublished ? `
                <div class="w-full text-center py-1.5 text-xs text-emerald-400 font-semibold bg-emerald-500/10 rounded-lg border border-emerald-500/20 flex items-center justify-center gap-1.5">
                    <i class="fas fa-check-circle"></i>
                    <span>Live Published on ${post.published_at || 'Schedule'}</span>
                </div>
            ` : ''}
        </div>
    `;
}

function getStatusBadgeClass(status) {
    switch (status) {
        case 'PENDING_REVIEW': return 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30';
        case 'APPROVED': return 'bg-blue-500/20 text-blue-400 border border-blue-500/30';
        case 'SCHEDULED': return 'bg-purple-500/20 text-purple-400 border border-purple-500/30';
        case 'PUBLISHED': return 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30';
        case 'REJECTED': return 'bg-red-500/20 text-red-400 border border-red-500/30';
        default: return 'bg-slate-800 text-slate-400';
    }
}

function zoomImage(url) {
    const lightbox = document.getElementById('lightbox-modal');
    const lightboxImg = document.getElementById('lightbox-img');
    if (lightbox && lightboxImg) {
        lightboxImg.src = url;
        lightbox.classList.remove('hidden');
    }
}

function closeLightbox() {
    const lightbox = document.getElementById('lightbox-modal');
    if (lightbox) lightbox.classList.add('hidden');
}

function showNotification(msg, type = 'info') {
    const toast = document.getElementById('toast');
    if (!toast) return;

    toast.textContent = msg;
    toast.className = `fixed top-5 right-5 z-50 px-4 py-2.5 rounded-xl text-xs font-bold shadow-xl transition-all duration-300 transform ${
        type === 'success' ? 'bg-emerald-600 text-white' : 
        type === 'error' ? 'bg-red-600 text-white' : 'bg-slate-800 text-white border border-slate-700'
    }`;
    toast.classList.remove('opacity-0', 'translate-y-[-10px]');
    toast.classList.add('opacity-100', 'translate-y-0');

    setTimeout(() => {
        toast.classList.add('opacity-0', 'translate-y-[-10px]');
        toast.classList.remove('opacity-100', 'translate-y-0');
    }, 3500);
}

function escapeHtml(text) {
    if (!text) return '';
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
