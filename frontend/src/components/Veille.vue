<script setup>
import { ref, watch, onMounted } from 'vue'
import { apiFetch } from '../api'

const articles = ref([])
const totalCount = ref(0)
const page = ref(1)
const hasMore = ref(false)
const loading = ref(false)
const loadingMore = ref(false)
const listError = ref('')
const refreshing = ref(false)
const activeCategory = ref(null)
const activeSeverity = ref(null)
const lastRefreshInfo = ref('')
const summarizingId = ref(null)
const summarizeError = ref('')

const SEVERITY_LABELS = {
  critical: 'Critique',
  high: 'Élevée',
  medium: 'Moyenne',
  low: 'Faible',
}

function articlesPath(pageNumber) {
  const params = new URLSearchParams({ page: pageNumber })
  if (activeCategory.value) params.set('category', activeCategory.value)
  if (activeSeverity.value) params.set('severity', activeSeverity.value)
  return `/api/veille/articles/?${params}`
}

// Chaque rechargement de la liste (filtre, actualisation) ouvre une nouvelle
// generation. Toute reponse d'une generation perimee est ignoree : deux clics
// rapides sur les filtres, ou un « Charger plus » lance pendant un rechargement,
// ne peuvent plus melanger les pages de deux filtres differents.
let generation = 0

async function readPage(pageNumber) {
  const response = await apiFetch(articlesPath(pageNumber))
  if (!response.ok) throw new Error(`HTTP ${response.status}`)
  return response.json()
}

async function fetchArticles() {
  const current = ++generation
  loading.value = true
  listError.value = ''
  try {
    const data = await readPage(1)
    if (current !== generation) return
    articles.value = data.results
    totalCount.value = data.count
    hasMore.value = Boolean(data.next)
    page.value = 1
  } catch {
    if (current === generation) listError.value = 'Impossible de charger les articles.'
  } finally {
    if (current === generation) loading.value = false
  }
}

async function loadMore() {
  if (loading.value || loadingMore.value) return

  const current = generation
  // Page memorisee au depart : on enregistre celle-la, pas « page + 1 » calcule
  // apres coup, au cas ou la liste aurait change entre-temps.
  const requested = page.value + 1
  loadingMore.value = true
  listError.value = ''
  try {
    const data = await readPage(requested)
    if (current !== generation) return
    const known = new Set(articles.value.map((article) => article.id))
    articles.value.push(...data.results.filter((article) => !known.has(article.id)))
    hasMore.value = Boolean(data.next)
    page.value = requested
  } catch {
    if (current === generation) listError.value = 'Impossible de charger la suite.'
  } finally {
    loadingMore.value = false
  }
}

// Les filtres sont appliques par le serveur : en changer recharge la premiere page
watch([activeCategory, activeSeverity], fetchArticles)

function describeRefresh(created) {
  if (created === 0) return 'Aucun nouvel article'
  return created === 1 ? '1 nouvel article' : `${created} nouveaux articles`
}

async function refresh() {
  refreshing.value = true
  lastRefreshInfo.value = ''
  try {
    const response = await apiFetch('/api/veille/refresh/', { method: 'POST' })
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const data = await response.json()
    let info = describeRefresh(data.created)
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

async function summarize(article) {
  summarizingId.value = article.id
  summarizeError.value = ''
  try {
    const response = await apiFetch(`/api/veille/articles/${article.id}/summarize/`, {
      method: 'POST',
    })
    const data = await response.json()

    if (!response.ok) {
      summarizeError.value = data.error || 'Échec du résumé.'
      return
    }

    const index = articles.value.findIndex((a) => a.id === article.id)
    if (index !== -1) articles.value[index] = data
  } catch (e) {
    summarizeError.value = 'Impossible de contacter le serveur.'
  } finally {
    summarizingId.value = null
  }
}

onMounted(fetchArticles)

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
          <svg aria-hidden="true" focusable="false" v-if="!refreshing" width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
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
          :aria-pressed="Boolean(activeCategory === null)"
          @click="activeCategory = null"
        >
          Tous
        </button>
        <button
          type="button"
          :class="['filter-btn', { active: activeCategory === 'cybersecurity' }]"
          :aria-pressed="Boolean(activeCategory === 'cybersecurity')"
          @click="activeCategory = 'cybersecurity'"
        >
          Cybersécurité
        </button>
        <button
          type="button"
          :class="['filter-btn', { active: activeCategory === 'ai' }]"
          :aria-pressed="Boolean(activeCategory === 'ai')"
          @click="activeCategory = 'ai'"
        >
          IA
        </button>
      </div>

      <div class="category-filters severity-filters">
        <button
          type="button"
          :class="['filter-btn', 'filter-btn-sub', { active: activeSeverity === null }]"
          :aria-pressed="Boolean(activeSeverity === null)"
          @click="activeSeverity = null"
        >
          Toutes gravités
        </button>
        <button
          v-for="(label, key) in SEVERITY_LABELS"
          :key="key"
          type="button"
          :class="['filter-btn', 'filter-btn-sub', 'filter-btn-' + key, { active: activeSeverity === key }]"
          :aria-pressed="Boolean(activeSeverity === key)"
          @click="activeSeverity = key"
        >
          {{ label }}
        </button>
      </div>
    </div>

    <p v-if="listError" class="summarize-error" role="alert">{{ listError }}</p>

    <p v-if="loading" class="empty-hint">Chargement...</p>
    <p v-else-if="listError && articles.length === 0" class="empty-hint">
      Réessaie avec le bouton « Actualiser » ou recharge la page.
    </p>
    <p v-else-if="articles.length === 0" class="empty-hint">
      <template v-if="activeCategory || activeSeverity">Aucun article pour ces filtres.</template>
      <template v-else>
        Aucun article pour l'instant — clique "Actualiser" pour aller chercher les derniers.
      </template>
    </p>
    <p v-else class="result-count tabular">
      {{ articles.length }} sur {{ totalCount }} article{{ totalCount === 1 ? '' : 's' }}
    </p>

    <p v-if="summarizeError" class="summarize-error">{{ summarizeError }}</p>

    <div class="article-list">
      <div v-for="article in articles" :key="article.id" class="article-card">
        <div class="article-meta">
          <span :class="['source-badge', article.source_category === 'ai' ? 'badge-ai' : 'badge-cyber']">
            {{ article.source_name }}
          </span>
          <span v-if="article.severity" :class="['severity-badge', 'severity-' + article.severity]">
            {{ SEVERITY_LABELS[article.severity] }}
          </span>
          <span class="article-date">{{ formatDate(article.published_at) }}</span>
        </div>

        <a :href="article.link" target="_blank" rel="noopener noreferrer" class="article-title">
          {{ article.title }}
        </a>

        <p v-if="article.ai_summary" class="article-summary article-summary-ai">
          {{ article.ai_summary }}
        </p>
        <p v-else-if="article.summary" class="article-summary">{{ article.summary }}</p>

        <div class="article-actions">
          <span v-if="article.ai_summary" class="ai-badge">Résumé en français</span>
          <button
            v-else
            type="button"
            class="summarize-btn"
            :disabled="summarizingId === article.id"
            @click="summarize(article)"
          >
            <span v-if="summarizingId === article.id" class="summarize-spinner"></span>
            {{ summarizingId === article.id ? 'Résumé...' : 'Résumer' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="hasMore" class="load-more">
      <button type="button" class="load-more-btn" :disabled="loading || loadingMore" @click="loadMore">
        {{ loadingMore ? 'Chargement...' : 'Charger plus' }}
      </button>
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
  padding: 20px 0 20px;
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
  font-size: var(--fs-xs);
  font-weight: 500;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: var(--accent-text);
}

.masthead-title {
  margin: 0 0 10px;
  font-family: 'Playfair Display', Georgia, serif;
  font-size: var(--fs-3xl);
  font-weight: 700;
  line-height: 1.2;
  color: var(--text);
  text-shadow: 0 2px 30px rgba(124, 108, 245, 0.2);
}

.masthead-meta {
  margin: 0;
  font-size: var(--fs-xs);
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
  font-size: var(--fs-sm);
  color: var(--text-muted);
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--accent-soft);
  color: var(--accent-text);
  border: 1px solid var(--accent-line);
  border-radius: var(--radius-sm);
  font-weight: 500;
  font-size: var(--fs-base);
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
  padding: 16px 16px;
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
  padding: 6px 16px;
  border: 1px solid var(--border);
  background: var(--glass-1);
  color: var(--text-muted);
  border-radius: 999px;
  cursor: pointer;
  font-size: var(--fs-sm);
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
  padding: 4px 12px;
  font-size: var(--fs-xs);
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
  font-size: var(--fs-base);
}

/* ---------- articles ---------- */
.article-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(258px, 1fr));
  gap: 12px;
}

.article-card {
  position: relative;
  display: flex;
  flex-direction: column;
  background: var(--glass-1);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px 16px;
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
  gap: 6px 10px;
  margin-bottom: 10px;
}

.source-badge,
.severity-badge {
  flex-shrink: 0;
  white-space: nowrap;
  font-family: 'IBM Plex Mono', monospace;
  font-size: var(--fs-xs);
  font-weight: 500;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  padding: 2px 10px;
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
  font-size: var(--fs-xs);
  color: var(--text-faint);
}

.article-title {
  display: block;
  margin: 0 0 8px;
  font-weight: 600;
  font-size: var(--fs-base);
  line-height: 1.45;
  color: var(--text);
  text-decoration: none;
  transition: color 0.15s ease;
}

.article-title:hover {
  color: var(--accent-2);
}

.article-summary {
  margin: 0;
  font-size: var(--fs-sm);
  line-height: 1.55;
  color: var(--text-muted);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* le resume genere est l'information utile : pas de troncature, et mis en avant */
.article-summary-ai {
  display: block;
  color: var(--text);
  border-left: 2px solid var(--accent-line);
  padding-left: 10px;
}

.article-actions {
  display: flex;
  align-items: center;
  margin-top: 12px;
}

.summarize-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px;
  background: var(--glass-2);
  border: 1px solid var(--border);
  border-radius: 999px;
  color: var(--text-muted);
  font-size: var(--fs-xs);
  cursor: pointer;
  transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease;
}

.summarize-btn:hover:not(:disabled) {
  background: var(--accent-soft);
  border-color: var(--accent-line);
  color: var(--accent-text);
}

.summarize-btn:disabled {
  cursor: progress;
  color: var(--text-faint);
}

.summarize-spinner {
  width: 9px;
  height: 9px;
  border: 1.5px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.ai-badge {
  font-family: 'IBM Plex Mono', monospace;
  font-size: var(--fs-xs);
  font-weight: 500;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--accent-text);
  background: var(--accent-soft);
  border: 1px solid var(--accent-line);
  border-radius: 999px;
  padding: 2px 10px;
}

.summarize-error {
  color: var(--danger);
  font-size: var(--fs-base);
  margin-bottom: 16px;
}

.result-count {
  margin: 0 0 12px;
  font-size: var(--fs-xs);
  color: var(--text-faint);
}

.load-more {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

.load-more-btn {
  padding: 10px 24px;
  background: var(--glass-1);
  border: 1px solid var(--border);
  border-radius: 999px;
  color: var(--text-muted);
  font-size: var(--fs-sm);
  cursor: pointer;
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease;
}

.load-more-btn:hover:not(:disabled) {
  background: var(--accent-soft);
  border-color: var(--accent-line);
  color: var(--text);
}

.load-more-btn:disabled {
  cursor: progress;
  color: var(--text-faint);
}
</style>
