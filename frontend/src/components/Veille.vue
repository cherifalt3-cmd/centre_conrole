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
          {{ refreshing ? 'Actualisation...' : 'Actualiser' }}
        </button>
      </div>
    </div>

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
  max-width: 1040px;
  margin: 0 auto;
}

.masthead {
  text-align: center;
  padding-bottom: 18px;
  margin-bottom: 22px;
  border-top: 3px double #14213d;
  border-bottom: 1px solid #14213d;
}

.masthead-kicker {
  margin: 14px 0 6px;
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: #5b6478;
}

.masthead-title {
  margin: 0 0 8px;
  font-family: 'Playfair Display', Georgia, serif;
  font-size: 2rem;
  font-weight: 700;
  color: #14201e;
}

.masthead-meta {
  margin: 0;
  font-size: 0.76rem;
  font-style: italic;
  letter-spacing: 0.04em;
  color: #8a93a3;
}

.veille-header {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 18px;
}

.veille-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.refresh-info {
  font-size: 0.82rem;
  color: #5b6478;
}

.refresh-btn {
  padding: 8px 16px;
  background: #1e3a5f;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.88rem;
  cursor: pointer;
  transition: background 0.15s ease;
}

.refresh-btn:hover:not(:disabled) {
  background: #14213d;
}

.refresh-btn:disabled {
  background: #b8c2d1;
  cursor: not-allowed;
}

.category-filters {
  display: flex;
  gap: 6px;
  margin-bottom: 18px;
}

.filter-btn {
  padding: 5px 14px;
  border: 1px solid #c5cedb;
  background: #fff;
  color: #5b6478;
  border-radius: 999px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
}

.filter-btn.active {
  background: #1e3a5f;
  border-color: #1e3a5f;
  color: #fff;
}

.empty-hint {
  color: #5b6478;
  font-size: 0.9rem;
}

.article-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 12px;
}

.article-card {
  display: flex;
  flex-direction: column;
  background: #fff;
  border: 1px solid #d8deea;
  border-radius: 10px;
  padding: 14px 16px;
  text-decoration: none;
  box-shadow: 0 1px 2px rgba(20, 32, 30, 0.04);
  transition: border-color 0.15s ease, box-shadow 0.15s ease, transform 0.15s ease;
}

.article-card:hover {
  border-color: #1e3a5f;
  transform: translateY(-2px);
  box-shadow: 0 4px 14px rgba(20, 32, 30, 0.07);
}

.article-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px 10px;
  margin-bottom: 6px;
}

.source-badge {
  flex-shrink: 0;
  white-space: nowrap;
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  padding: 2px 8px;
  border-radius: 999px;
}

.badge-cyber {
  background: #e5eff5;
  color: #2b6a8f;
}

.badge-ai {
  background: #f3e8f5;
  color: #7a3d8f;
}

.severity-badge {
  flex-shrink: 0;
  white-space: nowrap;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  padding: 2px 8px;
  border-radius: 999px;
}

.severity-critical {
  background: #fbe2e0;
  color: #a3271b;
}

.severity-high {
  background: #f6ece0;
  color: #a85a17;
}

.severity-medium {
  background: #fdf3d8;
  color: #8a6d1f;
}

.severity-low {
  background: #eef1f6;
  color: #5b6478;
}

.severity-filters {
  margin-top: -6px;
}

.filter-btn-sub {
  padding: 3px 10px;
  font-size: 0.76rem;
  border-color: #e5eaea;
  color: #8a93a3;
}

.filter-btn-critical.active {
  background: #a3271b;
  border-color: #a3271b;
}

.filter-btn-high.active {
  background: #a85a17;
  border-color: #a85a17;
}

.filter-btn-medium.active {
  background: #8a6d1f;
  border-color: #8a6d1f;
}

.filter-btn-low.active {
  background: #5b6478;
  border-color: #5b6478;
}

.article-date {
  white-space: nowrap;
  font-size: 0.78rem;
  color: #8a93a3;
}

.article-title {
  margin: 0 0 6px;
  font-weight: 600;
  font-size: 0.95rem;
  color: #14201e;
}

.article-summary {
  margin: 0;
  font-size: 0.85rem;
  color: #5b6478;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
