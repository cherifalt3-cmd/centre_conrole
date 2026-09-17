<script setup>
import { ref, computed, onMounted } from 'vue'
import { authToken } from '../auth'
import Kanban from './Kanban.vue'

const emit = defineEmits(['navigate'])

const targets = ref([])
const loaded = ref(false)

const articles = ref([])
const articlesLoaded = ref(false)

const kanbanBoard = ref(null)
const kanbanLoaded = ref(false)

async function fetchTargets() {
  const response = await fetch('http://127.0.0.1:8000/api/recon/targets/', {
    headers: { Authorization: `Token ${authToken.value}` },
  })
  targets.value = await response.json()
  loaded.value = true
}

async function fetchArticles() {
  const response = await fetch('http://127.0.0.1:8000/api/veille/articles/', {
    headers: { Authorization: `Token ${authToken.value}` },
  })
  articles.value = await response.json()
  articlesLoaded.value = true
}

async function fetchKanban() {
  const response = await fetch('http://127.0.0.1:8000/api/kanban/boards/', {
    headers: { Authorization: `Token ${authToken.value}` },
  })
  const boards = await response.json()
  kanbanBoard.value = boards.length ? boards[0] : null
  kanbanLoaded.value = true
}

onMounted(() => {
  fetchTargets()
  fetchArticles()
  fetchKanban()
})

const targetCount = computed(() => targets.value.length)
const lastTarget = computed(() => (targets.value.length ? targets.value[0] : null))

const articleCount = computed(() => articles.value.length)
const lastArticle = computed(() => (articles.value.length ? articles.value[0] : null))
const criticalCount = computed(() => articles.value.filter((a) => a.severity === 'critical').length)

const kanbanCardCount = computed(() => {
  if (!kanbanBoard.value) return 0
  return kanbanBoard.value.columns.reduce((sum, col) => sum + col.cards.length, 0)
})

const kanbanInProgressCount = computed(() => {
  if (!kanbanBoard.value) return 0
  const col = kanbanBoard.value.columns.find((c) => c.name === 'En cours')
  return col ? col.cards.length : 0
})
</script>

<template>
  <div class="dashboard">
    <div class="hero">
      <div class="terminal-window">
        <div class="terminal-bar">
          <span class="dot dot-red"></span>
          <span class="dot dot-yellow"></span>
          <span class="dot dot-green"></span>
          <span class="terminal-bar-title">bash — centre-controle</span>
        </div>
        <div class="terminal-body">
          <p class="terminal-line">
            <span class="prompt-user">pro@centre-controle</span><span class="prompt-sep">:</span><span class="prompt-path">~</span><span class="prompt-sep">$</span>
            Bienvenue<span class="cursor">_</span>
          </p>
        </div>
      </div>
      <p class="subtitle">Vue d'ensemble de tes modules</p>
    </div>

    <div class="dashboard-section dashboard-section-top">
      <Kanban />
    </div>

    <p class="eyebrow section-label">Modules</p>

    <div class="tile-grid">
      <button type="button" class="tile tile-active" @click="emit('navigate', 'targets')">
        <div class="tile-head">
          <span class="tile-icon-wrap">
            <svg class="tile-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2" />
              <circle cx="12" cy="12" r="5" stroke="currentColor" stroke-width="2" />
              <circle cx="12" cy="12" r="1.5" fill="currentColor" />
            </svg>
          </span>
          <span class="tile-title">Carnet de cibles</span>
          <svg class="tile-arrow" width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </div>
        <p v-if="loaded" class="tile-stat">
          <strong class="tabular">{{ targetCount }}</strong>
          <span class="tile-unit">cible{{ targetCount === 1 ? '' : 's' }} enregistrée{{ targetCount === 1 ? '' : 's' }}</span>
        </p>
        <p v-else class="tile-stat tile-loading">Chargement...</p>
        <p v-if="lastTarget" class="tile-detail">
          Dernière : {{ lastTarget.name || lastTarget.address }}
        </p>
        <p v-else-if="loaded" class="tile-detail tile-empty">Aucune cible pour l'instant</p>
      </button>

      <button type="button" class="tile tile-active" @click="emit('navigate', 'generator')">
        <div class="tile-head">
          <span class="tile-icon-wrap">
            <svg class="tile-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="2" y="4" width="20" height="16" rx="2" stroke="currentColor" stroke-width="2" />
              <path d="M6 9L10 12L6 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
              <line x1="12" y1="15" x2="17" y2="15" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
            </svg>
          </span>
          <span class="tile-title">Générateur de commandes</span>
          <svg class="tile-arrow" width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </div>
        <p class="tile-stat"><span class="tile-unit">Recon passive &amp; active</span></p>
        <p class="tile-detail tile-mono">nmap · whois · dig · theHarvester</p>
      </button>

      <button type="button" class="tile tile-active" @click="emit('navigate', 'osint')">
        <div class="tile-head">
          <span class="tile-icon-wrap">
            <svg class="tile-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="2" />
              <line x1="16.5" y1="16.5" x2="21" y2="21" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
            </svg>
          </span>
          <span class="tile-title">OSINT automatique</span>
          <svg class="tile-arrow" width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </div>
        <p class="tile-stat"><span class="tile-unit">Domaine → emails &amp; réseaux</span></p>
        <p class="tile-detail">Recherche active via Scrapy Cloud</p>
      </button>

      <button type="button" class="tile tile-active" @click="emit('navigate', 'veille')">
        <div class="tile-head">
          <span class="tile-icon-wrap">
            <svg class="tile-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="3" y="4" width="18" height="16" rx="1" stroke="currentColor" stroke-width="2" />
              <line x1="3" y1="9" x2="21" y2="9" stroke="currentColor" stroke-width="2" />
              <line x1="7" y1="13" x2="15" y2="13" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
              <line x1="7" y1="17" x2="12" y2="17" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
            </svg>
          </span>
          <span class="tile-title">Veille cybersécu &amp; IA</span>
          <svg class="tile-arrow" width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </div>
        <p v-if="articlesLoaded" class="tile-stat">
          <strong class="tabular">{{ articleCount }}</strong>
          <span class="tile-unit">article{{ articleCount === 1 ? '' : 's' }} en base</span>
        </p>
        <p v-else class="tile-stat tile-loading">Chargement...</p>
        <p v-if="criticalCount > 0" class="tile-detail tile-alert">
          <span class="alert-dot"></span>
          {{ criticalCount }} faille{{ criticalCount === 1 ? '' : 's' }} critique{{ criticalCount === 1 ? '' : 's' }}
        </p>
        <p v-else-if="lastArticle" class="tile-detail">{{ lastArticle.title }}</p>
        <p v-else-if="articlesLoaded" class="tile-detail tile-empty">Clique "Actualiser" pour aller chercher des articles</p>
      </button>

      <button type="button" class="tile tile-active" @click="emit('navigate', 'kanban')">
        <div class="tile-head">
          <span class="tile-icon-wrap">
            <svg class="tile-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="3" y="4" width="18" height="16" rx="1" stroke="currentColor" stroke-width="2" />
              <line x1="9" y1="4" x2="9" y2="20" stroke="currentColor" stroke-width="2" />
              <line x1="15" y1="4" x2="15" y2="20" stroke="currentColor" stroke-width="2" />
            </svg>
          </span>
          <span class="tile-title">Kanban projets</span>
          <svg class="tile-arrow" width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </div>
        <p v-if="kanbanLoaded" class="tile-stat">
          <strong class="tabular">{{ kanbanCardCount }}</strong>
          <span class="tile-unit">carte{{ kanbanCardCount === 1 ? '' : 's' }}</span>
        </p>
        <p v-else class="tile-stat tile-loading">Chargement...</p>
        <p v-if="kanbanInProgressCount > 0" class="tile-detail">
          {{ kanbanInProgressCount }} en cours
        </p>
        <p v-else-if="kanbanLoaded" class="tile-detail tile-empty">Aucune carte en cours</p>
      </button>

      <div class="tile tile-soon">
        <div class="tile-head">
          <span class="tile-icon-wrap">
            <svg class="tile-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M4 20a8 8 0 1 1 16 0" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
              <line x1="12" y1="20" x2="12" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
              <line x1="12" y1="12" x2="16" y2="9" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
            </svg>
          </span>
          <span class="tile-title">Suivi de conso</span>
        </div>
        <p class="tile-soon-badge">Bientôt disponible</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  max-width: 1120px;
  margin: 0 auto;
}

/* ---------- héros terminal ---------- */
.hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 34px;
}

.terminal-window {
  width: fit-content;
  max-width: 100%;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius);
  overflow: hidden;
  box-shadow: var(--shadow-3), 0 0 70px rgba(124, 108, 245, 0.12);
}

.terminal-bar {
  position: relative;
  display: flex;
  align-items: center;
  gap: 7px;
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid var(--border);
  padding: 9px 14px;
}

.dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
}

.dot-red { background: #ff5f57; }
.dot-yellow { background: #febc2e; }
.dot-green { background: #28c840; }

.terminal-bar-title {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.7rem;
  color: var(--text-faint);
  white-space: nowrap;
}

.terminal-body {
  background: rgba(7, 8, 12, 0.72);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  padding: 20px 30px 24px;
}

.terminal-line {
  margin: 0;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 1.05rem;
  color: var(--success);
  text-shadow: 0 0 14px rgba(61, 220, 151, 0.45);
  white-space: normal;
}

.prompt-user { color: var(--accent-2); }
.prompt-path { color: var(--warning); }

.prompt-sep {
  color: var(--text-faint);
  margin-right: 2px;
}

.cursor {
  animation: blink 1.1s step-end infinite;
}

@keyframes blink {
  50% { opacity: 0; }
}

.subtitle {
  margin: 16px 0 0;
  color: var(--text-muted);
  font-size: 0.9rem;
  text-align: center;
}

.dashboard-section-top {
  margin-bottom: 38px;
}

.section-label {
  margin-bottom: 14px;
}

/* ---------- tuiles ---------- */
.tile-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(258px, 1fr));
  gap: 14px;
}

.tile {
  position: relative;
  display: flex;
  flex-direction: column;
  text-align: left;
  background: var(--glass-1);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 18px 20px 20px;
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  box-shadow: var(--shadow-2);
  font-family: inherit;
  overflow: hidden;
}

/* halo qui s'allume au survol */
.tile-active::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: radial-gradient(ellipse 70% 100% at 50% 0%, rgba(124, 108, 245, 0.16), transparent 70%);
  opacity: 0;
  transition: opacity 0.22s ease;
  pointer-events: none;
}

.tile-active {
  cursor: pointer;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease, background 0.2s ease;
}

.tile-active:hover {
  background: var(--glass-2);
  border-color: var(--accent-line);
  box-shadow: var(--shadow-3), var(--ring-accent);
  transform: translateY(-3px);
}

.tile-active:hover::after {
  opacity: 1;
}

.tile-soon {
  opacity: 0.5;
}

.tile-head {
  display: flex;
  align-items: center;
  gap: 11px;
  margin-bottom: 16px;
}

.tile-icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  flex-shrink: 0;
  border-radius: 10px;
  background: var(--accent-soft);
  border: 1px solid var(--accent-line);
  color: var(--accent);
  transition: box-shadow 0.2s ease;
}

.tile-active:hover .tile-icon-wrap {
  box-shadow: 0 0 20px rgba(124, 108, 245, 0.35);
}

.tile-soon .tile-icon-wrap {
  background: var(--glass-2);
  border-color: var(--border);
  color: var(--text-faint);
}

.tile-title {
  font-weight: 600;
  font-size: 0.92rem;
  color: var(--text);
  line-height: 1.3;
}

.tile-arrow {
  margin-left: auto;
  flex-shrink: 0;
  color: var(--text-faint);
  opacity: 0;
  transform: translateX(-4px);
  transition: opacity 0.2s ease, transform 0.2s ease, color 0.2s ease;
}

.tile-active:hover .tile-arrow {
  opacity: 1;
  transform: translateX(0);
  color: var(--accent);
}

.tile-stat {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin: 0 0 7px;
  font-size: 0.88rem;
  color: var(--text-muted);
}

.tile-stat strong {
  font-size: 1.85rem;
  font-weight: 600;
  line-height: 1;
  color: var(--text);
  letter-spacing: -0.02em;
}

.tile-unit {
  color: var(--text-muted);
}

.tile-loading {
  color: var(--text-faint);
}

.tile-detail {
  margin: 0;
  font-size: 0.8rem;
  color: var(--text-faint);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tile-mono {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.74rem;
}

.tile-empty {
  font-style: italic;
}

.tile-alert {
  display: flex;
  align-items: center;
  gap: 7px;
  color: var(--sev-critical);
  font-weight: 500;
}

.alert-dot {
  width: 6px;
  height: 6px;
  flex-shrink: 0;
  border-radius: 50%;
  background: var(--sev-critical);
  box-shadow: 0 0 8px var(--sev-critical);
  animation: blink 1.6s ease-in-out infinite;
}

.tile-soon-badge {
  display: inline-block;
  margin: 0;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.66rem;
  font-weight: 500;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--text-faint);
  background: var(--glass-2);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 4px 11px;
  align-self: flex-start;
}
</style>
