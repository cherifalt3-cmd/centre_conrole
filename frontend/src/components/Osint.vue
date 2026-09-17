<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { authToken } from '../auth'

const query = ref('')
const submitting = ref(false)
const errorMessage = ref('')
const search = ref(null)
const history = ref([])

let pollTimer = null

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

async function pollSearch(id) {
  const response = await fetch(`http://127.0.0.1:8000/api/osint/searches/${id}/`, {
    headers: { Authorization: `Token ${authToken.value}` },
  })
  const data = await response.json()
  search.value = data

  if (data.status === 'finished' || data.status === 'failed') {
    stopPolling()
    const idx = history.value.findIndex((s) => s.id === data.id)
    if (idx !== -1) history.value[idx] = data
  }
}

async function launchSearch() {
  const target = query.value.trim()
  if (!target) return

  submitting.value = true
  errorMessage.value = ''
  stopPolling()

  try {
    const response = await fetch('http://127.0.0.1:8000/api/osint/searches/', {
      method: 'POST',
      headers: {
        Authorization: `Token ${authToken.value}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query: target }),
    })
    const data = await response.json()

    if (!response.ok) {
      errorMessage.value = data.error || "Échec du lancement de la recherche."
      return
    }

    search.value = data
    history.value.unshift(data)

    if (data.status === 'running') {
      pollTimer = setInterval(() => pollSearch(data.id), 4000)
    }
  } catch (e) {
    errorMessage.value = "Impossible de contacter le serveur."
  } finally {
    submitting.value = false
  }
}

async function fetchHistory() {
  const response = await fetch('http://127.0.0.1:8000/api/osint/searches/', {
    headers: { Authorization: `Token ${authToken.value}` },
  })
  const data = await response.json()
  history.value = data

  if (data.length) {
    search.value = data[0]
    if (data[0].status === 'running') {
      pollTimer = setInterval(() => pollSearch(data[0].id), 4000)
    }
  }
}

onMounted(fetchHistory)
onBeforeUnmount(stopPolling)

const statusLabels = {
  pending: 'En attente',
  running: 'Recherche en cours',
  finished: 'Terminé',
  failed: 'Échec',
}

const resultCount = computed(() => (search.value?.results || []).length)
</script>

<template>
  <div class="osint">
    <div class="osint-header">
      <p class="eyebrow">Reconnaissance active</p>
      <h2 class="osint-title">OSINT automatique</h2>
      <p class="osint-subtitle">
        Donne un domaine — l'app explore le site et remonte emails et liens sociaux trouvés.
      </p>
    </div>

    <form class="osint-form" @submit.prevent="launchSearch">
      <span class="osint-input-wrap">
        <svg class="osint-input-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="2" />
          <line x1="16.5" y1="16.5" x2="21" y2="21" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
        </svg>
        <input
          v-model="query"
          type="text"
          class="osint-input"
          placeholder="exemple.com"
          :disabled="submitting"
        />
      </span>
      <button type="submit" class="osint-submit" :disabled="submitting || !query.trim()">
        {{ submitting ? 'Lancement...' : 'Lancer la recherche' }}
      </button>
    </form>

    <p v-if="errorMessage" class="osint-error">{{ errorMessage }}</p>

    <div v-if="search" class="osint-result">
      <div class="osint-result-head">
        <span class="osint-result-query">{{ search.query }}</span>
        <span :class="['osint-status', 'status-' + search.status]">
          <span v-if="search.status === 'running'" class="status-spinner"></span>
          {{ statusLabels[search.status] }}
        </span>
      </div>

      <p v-if="search.status === 'running'" class="empty-hint">
        Exploration du site en cours, ça peut prendre quelques dizaines de secondes...
      </p>
      <p v-else-if="search.error_message" class="empty-hint osint-error-inline">
        {{ search.error_message }}
      </p>
      <p v-else-if="search.status === 'failed'" class="empty-hint">
        La recherche a échoué. Vérifie le domaine et réessaie.
      </p>
      <p v-else-if="search.status === 'finished' && resultCount === 0" class="empty-hint">
        Aucun email ni lien social trouvé sur ce domaine.
      </p>

      <div v-if="resultCount > 0" class="osint-pages">
        <div v-for="(page, i) in search.results" :key="i" class="osint-page">
          <p class="osint-page-url">{{ page.url }}</p>
          <div v-if="page.emails?.length" class="osint-page-row">
            <span class="osint-tag-label">Emails</span>
            <div class="osint-tags">
              <span v-for="email in page.emails" :key="email" class="osint-tag osint-tag-email">{{ email }}</span>
            </div>
          </div>
          <div v-if="page.social_links?.length" class="osint-page-row">
            <span class="osint-tag-label">Réseaux</span>
            <div class="osint-tags">
              <a
                v-for="link in page.social_links"
                :key="link"
                :href="link"
                target="_blank"
                rel="noopener noreferrer"
                class="osint-tag osint-tag-social"
              >
                {{ link }}
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="history.length > 1" class="osint-history">
      <p class="eyebrow">Recherches précédentes</p>
      <ul class="osint-history-list">
        <li v-for="item in history.slice(1)" :key="item.id" class="osint-history-item">
          <span class="osint-history-query">{{ item.query }}</span>
          <span :class="['osint-status', 'osint-status-sm', 'status-' + item.status]">{{ statusLabels[item.status] }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.osint {
  max-width: 900px;
  margin: 0 auto;
}

.osint-header {
  text-align: center;
  margin-bottom: 26px;
}

.osint-title {
  margin: 6px 0 8px;
  font-size: 1.7rem;
  font-weight: 600;
  letter-spacing: -0.02em;
  color: var(--text);
}

.osint-subtitle {
  margin: 0;
  font-size: 0.88rem;
  color: var(--text-muted);
}

/* ---------- formulaire ---------- */
.osint-form {
  display: flex;
  gap: 10px;
  max-width: 540px;
  margin: 0 auto 26px;
}

.osint-input-wrap {
  position: relative;
  flex: 1;
  display: flex;
  align-items: center;
}

.osint-input-icon {
  position: absolute;
  left: 13px;
  color: var(--text-faint);
  pointer-events: none;
}

.osint-input {
  width: 100%;
  padding: 11px 14px 11px 36px;
  background: var(--glass-1);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text);
  font-size: 0.9rem;
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  transition: border-color 0.16s ease, box-shadow 0.16s ease, background 0.16s ease;
}

.osint-input::placeholder {
  color: var(--text-faint);
}

.osint-input:focus {
  outline: none;
  background: var(--glass-2);
  border-color: var(--accent-line);
  box-shadow: 0 0 0 3px var(--accent-soft);
}

.osint-submit {
  padding: 11px 20px;
  background: linear-gradient(135deg, var(--accent), #6355d6);
  color: #fff;
  border: 1px solid var(--accent-line);
  border-radius: var(--radius-sm);
  font-weight: 500;
  font-size: 0.87rem;
  cursor: pointer;
  white-space: nowrap;
  box-shadow: 0 6px 22px rgba(124, 108, 245, 0.28);
  transition: box-shadow 0.18s ease, transform 0.18s ease, filter 0.18s ease;
}

.osint-submit:hover:not(:disabled) {
  filter: brightness(1.12);
  box-shadow: 0 8px 30px rgba(124, 108, 245, 0.42);
  transform: translateY(-1px);
}

.osint-submit:disabled {
  background: var(--glass-2);
  border-color: var(--border);
  color: var(--text-faint);
  box-shadow: none;
  cursor: not-allowed;
}

.osint-error {
  text-align: center;
  color: var(--danger);
  font-size: 0.86rem;
  margin-bottom: 18px;
}

/* ---------- résultat ---------- */
.osint-result {
  background: var(--glass-1);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px 22px;
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  box-shadow: var(--shadow-2);
}

.osint-result-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
  padding-bottom: 13px;
  margin-bottom: 14px;
  border-bottom: 1px solid var(--border);
}

.osint-result-query {
  font-family: 'IBM Plex Mono', monospace;
  font-weight: 500;
  font-size: 0.95rem;
  color: var(--text);
  word-break: break-all;
}

.osint-status {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  flex-shrink: 0;
  white-space: nowrap;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.66rem;
  font-weight: 500;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  padding: 4px 11px;
  border-radius: 999px;
  border: 1px solid transparent;
}

.status-pending,
.status-running {
  background: var(--warning-soft);
  border-color: rgba(245, 194, 107, 0.3);
  color: var(--warning);
}

.status-finished {
  background: var(--success-soft);
  border-color: rgba(61, 220, 151, 0.3);
  color: var(--success);
}

.status-failed {
  background: var(--danger-soft);
  border-color: rgba(245, 118, 107, 0.3);
  color: var(--danger);
}

.status-spinner {
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

.empty-hint {
  color: var(--text-muted);
  font-size: 0.87rem;
  margin: 0;
}

.osint-error-inline {
  color: var(--danger);
}

.osint-pages {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.osint-page {
  padding: 13px 15px;
  background: var(--glass-2);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
}

.osint-page-url {
  margin: 0 0 10px;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.78rem;
  color: var(--accent-2);
  word-break: break-all;
}

.osint-page-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-top: 8px;
}

.osint-tag-label {
  flex-shrink: 0;
  width: 52px;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.64rem;
  font-weight: 500;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-faint);
  padding-top: 4px;
}

.osint-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.osint-tag {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.74rem;
  padding: 3px 10px;
  border-radius: 999px;
  border: 1px solid transparent;
  text-decoration: none;
  word-break: break-all;
  transition: box-shadow 0.15s ease, border-color 0.15s ease;
}

.osint-tag-email {
  background: var(--info-soft);
  border-color: rgba(106, 184, 245, 0.25);
  color: var(--info);
}

.osint-tag-social {
  background: var(--accent-soft);
  border-color: var(--accent-line);
  color: #a396ff;
}

.osint-tag-social:hover {
  border-color: var(--accent);
  box-shadow: 0 0 16px rgba(124, 108, 245, 0.3);
}

/* ---------- historique ---------- */
.osint-history {
  margin-top: 22px;
}

.osint-history-list {
  list-style: none;
  margin: 10px 0 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.osint-history-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 9px 14px;
  background: var(--glass-1);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 0.84rem;
  color: var(--text-muted);
  transition: background 0.15s ease, border-color 0.15s ease;
}

.osint-history-item:hover {
  background: var(--glass-2);
  border-color: var(--border-strong);
}

.osint-history-query {
  font-family: 'IBM Plex Mono', monospace;
  color: var(--text);
  word-break: break-all;
}

.osint-status-sm {
  font-size: 0.6rem;
  padding: 2px 9px;
}
</style>
