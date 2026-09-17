<script setup>
import { ref, computed, onMounted } from 'vue'
import { authToken } from '../auth'

const articles = ref([])
const loading = ref(false)
const refreshing = ref(false)
const activeCategory = ref(null)
const activeSeverity = ref(null)
const lastRefreshInfo = ref('')

const SEVERITY_LABELS = {
  critical: 'Critique',
  high: 'Élevée',
  medium: 'Moyenne',
  low: 'Faible',
}

async function fetchArticles() {
  loading.value = true
  const response = await fetch('http://127.0.0.1:8000/api/veille/articles/', {
    headers: { Authorization: `Token ${authToken.value}` },
  })
  articles.value = await response.json()
  loading.value = false
}

async function refresh() {
  refreshing.value = true
  lastRefreshInfo.value = ''
  try {
    const response = await fetch('http://127.0.0.1:8000/api/veille/refresh/', {
      method: 'POST',
      headers: { Authorization: `Token ${authToken.value}` },
    })
    const data = await response.json()
    let info = `${data.created} nouvel${data.created === 1 ? '' : 'le'}${data.created === 1 ? '' : 's'} article${data.created === 1 ? '' : 's'}`
    if (data.failed_sources?.length) {
      info += ` (échec : ${data.failed_sources.join(', ')})`
    }
    lastRefreshInfo.value = info
    await fetchArticles()
  } catch (e) {
    lastRefreshInfo.value = "Échec de l'actualisation, réessaie."
  } finally {
    refreshing.value = false
  }
}

onMounted(fetchArticles)

const filteredArticles = computed(() => {
  let list = articles.value
  if (activeCategory.value) {
    list = list.filter((a) => a.source_category === activeCategory.value)
  }
  if (activeSeverity.value) {
    list = list.filter((a) => a.severity === activeSeverity.value)
  }
  return list
})

function formatDate(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
}
</script>

<template>
  <div class="veille">
    <div class="masthead">
      <p class="masthead-kicker">Bulletin de veille</p>
      <h2 class="masthead-title">Cybersécurité &amp; Intelligence Artificielle</h2>
      <p class="masthead-meta">Édition mise à jour en continu</p>
    </div>

    <div class="veille-header">
      <div class="veille-actions">
        <span v-if="lastRefreshInfo" class="refresh-info">{{ lastRefreshInfo }}</span>
        <button type="button" class="refresh-btn" :disabled="refreshing" @click="refresh">
          <svg v-if="!refreshing" width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M20 12a8 8 0 1 1-2.3-5.6" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
            <path d="M20 4v5h-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
          {{ refreshing ? 'Actualisation...' : 'Actualiser' }}
        </button>
      </div>
    </div>

    <div class="filter-bar">
      <div class="category-filters">
        <button
          type="button"
          :class="['filter-btn', { active: activeCategory === null }]"
          @click="activeCategory = null"
        >
          Tous
        </button>
        <button
          type="button"
          :class="['filter-btn', { active: activeCategory === 'cybersecurity' }]"
          @click="activeCategory = 'cybersecurity'"
        >
          Cybersécurité
        </button>
        <button
          type="button"
          :class="['filter-btn', { active: activeCategory === 'ai' }]"
          @click="activeCategory = 'ai'"
        >
          IA
        </button>
      </div>

      <div class="category-filters severity-filters">
        <button
          type="button"
          :class="['filter-btn', 'filter-btn-sub', { active: activeSeverity === null }]"
          @click="activeSeverity = null"
        >
          Toutes gravités
        </button>
        <button
          v-for="(label, key) in SEVERITY_LABELS"
          :key="key"
          type="button"
          :class="['filter-btn', 'filter-btn-sub', 'filter-btn-' + key, { active: activeSeverity === key }]"
          @click="activeSeverity = key"
        >
          {{ label }}
        </button>
      </div>
    </div>

    <p v-if="loading" class="empty-hint">Chargement...</p>
    <p v-else-if="filteredArticles.length === 0" class="empty-hint">
      Aucun article pour l'instant — clique "Actualiser" pour aller chercher les derniers.
    </p>

    <div class="article-list">
      <a
        v-for="article in filteredArticles"
        :key="article.id"
        :href="article.link"
        target="_blank"
        rel="noopener noreferrer"
        class="article-card"
      >
        <div class="article-meta">
          <span :class="['source-badge', article.source_category === 'ai' ? 'badge-ai' : 'badge-cyber']">
            {{ article.source_name }}
          </span>
          <span v-if="article.severity" :class="['severity-badge', 'severity-' + article.severity]">
            {{ SEVERITY_LABELS[article.severity] }}
          </span>
          <span class="article-date">{{ formatDate(article.published_at) }}</span>
        </div>
        <p class="article-title">{{ article.title }}</p>
        <p v-if="article.summary" class="article-summary">{{ article.summary }}</p>
      </a>
    </div>
  </div>
</template>

<style scoped>
.veille {
  max-width: 1120px;
  margin: 0 auto;
}

/* ---------- masthead ---------- */
.masthead {
  text-align: center;
  padding: 18px 0 20px;
  margin-bottom: 24px;
  border-top: 1px solid var(--border-strong);
  border-bottom: 1px solid var(--border);
  position: relative;
}

.masthead::before {
  content: '';
  position: absolute;
  top: 3px;
  left: 0;
  right: 0;
  height: 1px;
  background: var(--border);
}

.masthead-kicker {
  margin: 0 0 8px;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.66rem;
  font-weight: 500;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: var(--accent);
}

.masthead-title {
  margin: 0 0 9px;
  font-family: 'Playfair Display', Georgia, serif;
  font-size: 2.05rem;
  font-weight: 700;
  line-height: 1.2;
  color: var(--text);
  text-shadow: 0 2px 30px rgba(124, 108, 245, 0.2);
}

.masthead-meta {
  margin: 0;
  font-size: 0.74rem;
  font-style: italic;
  letter-spacing: 0.04em;
  color: var(--text-faint);
}

/* ---------- actions ---------- */
.veille-header {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 16px;
}

.veille-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.refresh-info {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--accent-soft);
  color: var(--accent);
  border: 1px solid var(--accent-line);
  border-radius: var(--radius-sm);
  font-weight: 500;
  font-size: 0.85rem;
  cursor: pointer;
  transition: background 0.16s ease, box-shadow 0.16s ease, color 0.16s ease;
}

.refresh-btn:hover:not(:disabled) {
  background: rgba(124, 108, 245, 0.24);
  color: #fff;
  box-shadow: 0 0 22px rgba(124, 108, 245, 0.3);
}

.refresh-btn:disabled {
  background: var(--glass-2);
  border-color: var(--border);
  color: var(--text-faint);
  cursor: not-allowed;
}

/* ---------- filtres ---------- */
.filter-bar {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 14px 16px;
  margin-bottom: 20px;
  background: var(--glass-1);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
}

.category-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.filter-btn {
  padding: 5px 14px;
  border: 1px solid var(--border);
  background: var(--glass-1);
  color: var(--text-muted);
  border-radius: 999px;
  cursor: pointer;
  font-size: 0.82rem;
  transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
}

.filter-btn:hover {
  background: var(--glass-2);
  color: var(--text);
}

.filter-btn.active {
  background: var(--accent-soft);
  border-color: var(--accent-line);
  color: #fff;
  box-shadow: 0 0 16px rgba(124, 108, 245, 0.22);
}

.filter-btn-sub {
  padding: 3px 11px;
  font-size: 0.75rem;
}

.filter-btn-critical.active {
  background: var(--sev-critical-soft);
  border-color: var(--sev-critical);
  color: var(--sev-critical);
  box-shadow: 0 0 16px rgba(255, 107, 107, 0.2);
}

.filter-btn-high.active {
  background: var(--sev-high-soft);
  border-color: var(--sev-high);
  color: var(--sev-high);
  box-shadow: 0 0 16px rgba(255, 160, 87, 0.2);
}

.filter-btn-medium.active {
  background: var(--sev-medium-soft);
  border-color: var(--sev-medium);
  color: var(--sev-medium);
  box-shadow: 0 0 16px rgba(245, 194, 107, 0.2);
}

.filter-btn-low.active {
  background: var(--sev-low-soft);
  border-color: var(--sev-low);
  color: var(--sev-low);
  box-shadow: none;
}

.empty-hint {
  color: var(--text-muted);
  font-size: 0.9rem;
}

/* ---------- articles ---------- */
.article-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(258px, 1fr));
  gap: 13px;
}

.article-card {
  position: relative;
  display: flex;
  flex-direction: column;
  background: var(--glass-1);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 15px 17px;
  text-decoration: none;
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  box-shadow: var(--shadow-2);
  overflow: hidden;
  transition: background 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease;
}

.article-card::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: radial-gradient(ellipse 70% 100% at 50% 0%, rgba(124, 108, 245, 0.13), transparent 70%);
  opacity: 0;
  transition: opacity 0.2s ease;
  pointer-events: none;
}

.article-card:hover {
  background: var(--glass-2);
  border-color: var(--accent-line);
  transform: translateY(-3px);
  box-shadow: var(--shadow-3), var(--ring-accent);
}

.article-card:hover::after {
  opacity: 1;
}

.article-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px 9px;
  margin-bottom: 9px;
}

.source-badge,
.severity-badge {
  flex-shrink: 0;
  white-space: nowrap;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.63rem;
  font-weight: 500;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  padding: 2px 9px;
  border-radius: 999px;
  border: 1px solid transparent;
}

.badge-cyber {
  background: var(--info-soft);
  border-color: rgba(106, 184, 245, 0.25);
  color: var(--info);
}

.badge-ai {
  background: var(--accent-soft);
  border-color: var(--accent-line);
  color: #a396ff;
}

.severity-badge {
  font-weight: 600;
}

.severity-critical {
  background: var(--sev-critical-soft);
  border-color: rgba(255, 107, 107, 0.32);
  color: var(--sev-critical);
  box-shadow: 0 0 14px rgba(255, 107, 107, 0.18);
}

.severity-high {
  background: var(--sev-high-soft);
  border-color: rgba(255, 160, 87, 0.3);
  color: var(--sev-high);
}

.severity-medium {
  background: var(--sev-medium-soft);
  border-color: rgba(245, 194, 107, 0.28);
  color: var(--sev-medium);
}

.severity-low {
  background: var(--sev-low-soft);
  border-color: var(--border);
  color: var(--sev-low);
}

.article-date {
  margin-left: auto;
  white-space: nowrap;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.7rem;
  color: var(--text-faint);
}

.article-title {
  margin: 0 0 7px;
  font-weight: 600;
  font-size: 0.93rem;
  line-height: 1.45;
  color: var(--text);
}

.article-summary {
  margin: 0;
  font-size: 0.82rem;
  line-height: 1.55;
  color: var(--text-muted);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
