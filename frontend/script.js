const API_BASE = '/api';

// DOM Elements
const userSelect = document.getElementById('user-select');
const userProfile = document.getElementById('user-profile');
const profileName = document.getElementById('profile-name');
const profileType = document.getElementById('profile-type');
const profileInterests = document.getElementById('profile-interests');
const recsContainer = document.getElementById('recommendations-container');
const requestMeta = document.getElementById('request-meta');
const reqTime = document.getElementById('req-time');
const reqStrategy = document.getElementById('req-strategy');

// State
let users = [];
let currentUser = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    fetchUsers();
    
    // Event Listeners
    userSelect.addEventListener('change', handleUserChange);
    document.querySelectorAll('input[name="strategy"]').forEach(radio => {
        radio.addEventListener('change', () => {
            if (currentUser) fetchRecommendations(currentUser.id);
        });
    });

    // Start background polling for metrics
    setInterval(fetchMetrics, 5000);
    setInterval(fetchHealth, 10000);
});

// API Calls
async function fetchUsers() {
    try {
        const response = await fetch(`${API_BASE}/users`);
        users = await response.json();
        
        userSelect.innerHTML = '<option value="" disabled selected>Choose a user profile...</option>';
        users.forEach(user => {
            const opt = document.createElement('option');
            opt.value = user.id;
            opt.textContent = `${user.name} ${user.interests.length === 0 ? '(New User)' : ''}`;
            userSelect.appendChild(opt);
        });
    } catch (error) {
        showToast('Error loading users', 'error');
        console.error(error);
    }
}

async function fetchRecommendations(userId) {
    const strategy = document.querySelector('input[name="strategy"]:checked').value;
    
    recsContainer.innerHTML = `
        <div class="empty-state">
            <i class="fa-solid fa-circle-notch fa-spin"></i>
            <p>Running AI Recommendation Engine...</p>
        </div>
    `;

    try {
        const response = await fetch(`${API_BASE}/recommend/${userId}?strategy=${strategy}`);
        if (!response.ok) throw new Error('API Error');
        const data = await response.json();
        
        renderRecommendations(data);
        updateMeta(data.response_time_ms, data.strategy);
    } catch (error) {
        recsContainer.innerHTML = `
            <div class="empty-state">
                <i class="fa-solid fa-triangle-exclamation" style="color: #ef4444;"></i>
                <p>Failed to generate recommendations</p>
            </div>
        `;
        showToast('Failed to fetch recommendations', 'error');
    }
}

async function submitFeedback(userId, contentId, type, rating = null) {
    try {
        await fetch(`${API_BASE}/feedback`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: userId,
                content_id: contentId,
                interaction_type: type,
                rating: rating
            })
        });
        
        showToast(`Feedback recorded: ${type}`);
        // Optionally fetch new recommendations
        // fetchRecommendations(userId);
    } catch (error) {
        showToast('Error recording feedback', 'error');
    }
}

async function fetchMetrics() {
    try {
        const res = await fetch(`${API_BASE}/metrics`);
        const data = await res.json();
        
        document.getElementById('metric-latency').textContent = data.avg_response_time_ms;
        document.getElementById('metric-cache-hit').textContent = `${(data.cache_hit_rate * 100).toFixed(1)}%`;
        document.getElementById('metric-requests').textContent = data.total_requests;
        document.getElementById('metric-cache-size').textContent = data.cache_size;
    } catch (e) {
        // silently fail for background polling
    }
}

async function fetchHealth() {
    try {
        const res = await fetch(`${API_BASE}/health`);
        const data = await res.json();
        const indicator = document.querySelector('.status-indicator');
        const text = document.getElementById('status-text');
        
        if (data.status === 'healthy') {
            indicator.style.backgroundColor = 'var(--accent-green)';
            indicator.style.boxShadow = '0 0 10px var(--accent-green)';
            text.textContent = 'System Live';
        } else {
            indicator.style.backgroundColor = 'var(--accent-pink)';
            indicator.style.boxShadow = '0 0 10px var(--accent-pink)';
            text.textContent = 'Degraded';
        }
    } catch (e) {
        const indicator = document.querySelector('.status-indicator');
        indicator.style.backgroundColor = '#ef4444';
        document.getElementById('status-text').textContent = 'Offline';
    }
}

// UI Rendering
function handleUserChange(e) {
    const userId = parseInt(e.target.value);
    currentUser = users.find(u => u.id === userId);
    
    if (currentUser) {
        // Update Profile panel
        profileName.textContent = currentUser.name;
        
        if (currentUser.interests.length === 0) {
            profileType.textContent = 'Cold Start (New)';
            profileType.classList.add('active');
            profileInterests.innerHTML = '<span class="badge">No data yet</span>';
        } else {
            profileType.textContent = 'Active Member';
            profileType.classList.remove('active');
            profileInterests.innerHTML = currentUser.interests.map(i => `<span class="badge active">${i}</span>`).join('');
        }
        
        userProfile.classList.remove('hidden');
        fetchRecommendations(currentUser.id);
    }
}

function renderRecommendations(data) {
    if (!data.recommendations || data.recommendations.length === 0) {
        recsContainer.innerHTML = '<div class="empty-state"><p>No recommendations found.</p></div>';
        return;
    }

    recsContainer.innerHTML = '';
    data.recommendations.forEach((rec, index) => {
        // Randomize stars based on difficulty just for visual appeal
        const diffStars = rec.difficulty === 'beginner' ? '★☆☆' : rec.difficulty === 'intermediate' ? '★★☆' : '★★★';
        
        const card = document.createElement('div');
        card.className = 'rec-card';
        card.style.animationDelay = `${index * 0.1}s`;
        
        // Convert score to percentage
        const scorePct = Math.min(100, Math.max(0, rec.score * 100));
        
        card.innerHTML = `
            <div class="rec-header">
                <span class="rec-category"><i class="fa-solid fa-tag"></i> ${rec.category}</span>
                <span class="rec-difficulty" title="${rec.difficulty}">${diffStars}</span>
            </div>
            <h3 class="rec-title">${rec.title}</h3>
            
            <div class="score-container">
                <div class="score-label">
                    <span>Match Score</span>
                    <span class="mono">${scorePct.toFixed(1)}%</span>
                </div>
                <div class="score-bar-bg">
                    <div class="score-bar-fill" style="width: 0%" data-target="${scorePct}%"></div>
                </div>
                <div class="explanation">
                    <i class="fa-solid fa-lightbulb" style="color: var(--text-muted)"></i> ${rec.explanation}
                </div>
            </div>
            
            <div class="card-actions">
                <button class="btn-action like" onclick="submitFeedback(${data.user_id}, '${rec.item_id}', 'rate', 5)">
                    <i class="fa-regular fa-thumbs-up"></i>
                </button>
                <button class="btn-action dislike" onclick="submitFeedback(${data.user_id}, '${rec.item_id}', 'rate', 1)">
                    <i class="fa-regular fa-thumbs-down"></i>
                </button>
                <button class="btn-action" onclick="submitFeedback(${data.user_id}, '${rec.item_id}', 'click')" title="View Content">
                    <i class="fa-solid fa-arrow-right"></i>
                </button>
            </div>
        `;
        recsContainer.appendChild(card);
    });

    // Trigger score bar animations
    setTimeout(() => {
        document.querySelectorAll('.score-bar-fill').forEach(bar => {
            bar.style.width = bar.getAttribute('data-target');
        });
    }, 100);
}

function updateMeta(time, strategy) {
    requestMeta.classList.remove('hidden');
    reqTime.textContent = `${time}ms`;
    reqStrategy.textContent = strategy.toUpperCase();
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = 'toast';
    
    const icon = type === 'error' ? 'fa-circle-xmark' : 'fa-circle-check';
    toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s forwards';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
