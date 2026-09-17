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
    <div class="terminal-title">
      <div class="terminal-window">
        <div class="terminal-bar">
          <span class="dot dot-red"></span>
          <span class="dot dot-yellow"></span>
          <span class="dot dot-green"></span>
          <span class="terminal-bar-title">bash — centre-controle</span>
        </div>
        <p class="terminal-line">
          <span class="prompt-user">pro@centre-controle</span><span class="prompt-sep">:</span><span class="prompt-path">~</span><span class="prompt-sep">$</span>
          Bienvenue<span class="cursor">_</span>
        </p>
      </div>
    </div>
    <p class="subtitle">Vue d'ensemble de tes modules</p>

    <div class="dashboard-section dashboard-section-top">
      <Kanban />
    </div>

    <div class="tile-grid">
      <button type="button" class="tile tile-active" @click="emit('navigate', 'targets')">
        <div class="tile-head">
          <svg class="tile-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2" />
            <circle cx="12" cy="12" r="5" stroke="currentColor" stroke-width="2" />
            <circle cx="12" cy="12" r="1.5" fill="currentColor" />
          </svg>
          <span class="tile-title">Carnet de cibles</span>
        </div>
        <p v-if="loaded" class="tile-stat">
          <strong>{{ targetCount }}</strong> cible{{ targetCount === 1 ? '' : 's' }} enregistrée{{ targetCount === 1 ? '' : 's' }}
        </p>
        <p v-else class="tile-stat tile-loading">Chargement...</p>
        <p v-if="lastTarget" class="tile-detail">
          Dernière : {{ lastTarget.name || lastTarget.address }}
        </p>
        <p v-else-if="loaded" class="tile-detail tile-empty">Aucune cible pour l'instant</p>
      </button>

      <button type="button" class="tile tile-active" @click="emit('navigate', 'generator')">
        <div class="tile-head">
          <svg class="tile-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="2" y="4" width="20" height="16" rx="2" stroke="currentColor" stroke-width="2" />
            <path d="M6 9L10 12L6 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
            <line x1="12" y1="15" x2="17" y2="15" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
          </svg>
          <span class="tile-title">Générateur de commandes</span>
        </div>
        <p class="tile-stat">Recon passive &amp; active</p>
        <p class="tile-detail">nmap, whois, dig, theHarvester, Metasploit...</p>
      </button>

      <div class="tile tile-soon">
        <div class="tile-head">
          <svg class="tile-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="2" />
            <line x1="16.5" y1="16.5" x2="21" y2="21" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
          </svg>
          <span class="tile-title">OSINT automatique</span>
        </div>
        <p class="tile-soon-badge">Bientôt disponible</p>
      </div>

      <button type="button" class="tile tile-active" @click="emit('navigate', 'veille')">
        <div class="tile-head">
          <svg class="tile-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="3" y="4" width="18" height="16" rx="1" stroke="currentColor" stroke-width="2" />
            <line x1="3" y1="9" x2="21" y2="9" stroke="currentColor" stroke-width="2" />
            <line x1="7" y1="13" x2="15" y2="13" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
            <line x1="7" y1="17" x2="12" y2="17" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
          </svg>
          <span class="tile-title">Veille cybersécu &amp; IA</span>
        </div>
        <p v-if="articlesLoaded" class="tile-stat">
          <strong>{{ articleCount }}</strong> article{{ articleCount === 1 ? '' : 's' }} en base
        </p>
        <p v-else class="tile-stat tile-loading">Chargement...</p>
        <p v-if="criticalCount > 0" class="tile-detail tile-alert">
          {{ criticalCount }} faille{{ criticalCount === 1 ? '' : 's' }} critique{{ criticalCount === 1 ? '' : 's' }}
        </p>
        <p v-else-if="lastArticle" class="tile-detail">{{ lastArticle.title }}</p>
        <p v-else-if="articlesLoaded" class="tile-detail tile-empty">Clique "Actualiser" pour aller chercher des articles</p>
      </button>

      <button type="button" class="tile tile-active" @click="emit('navigate', 'kanban')">
        <div class="tile-head">
          <svg class="tile-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="3" y="4" width="18" height="16" rx="1" stroke="currentColor" stroke-width="2" />
            <line x1="9" y1="4" x2="9" y2="20" stroke="currentColor" stroke-width="2" />
            <line x1="15" y1="4" x2="15" y2="20" stroke="currentColor" stroke-width="2" />
          </svg>
          <span class="tile-title">Kanban projets</span>
        </div>
        <p v-if="kanbanLoaded" class="tile-stat">
          <strong>{{ kanbanCardCount }}</strong> carte{{ kanbanCardCount === 1 ? '' : 's' }}
        </p>
        <p v-else class="tile-stat tile-loading">Chargement...</p>
        <p v-if="kanbanInProgressCount > 0" class="tile-detail">
          {{ kanbanInProgressCount }} en cours
        </p>
        <p v-else-if="kanbanLoaded" class="tile-detail tile-empty">Aucune carte en cours</p>
      </button>

      <div class="tile tile-soon">
        <div class="tile-head">
          <svg class="tile-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M4 20a8 8 0 1 1 16 0" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
            <line x1="12" y1="20" x2="12" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
            <line x1="12" y1="12" x2="16" y2="9" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
          </svg>
          <span class="tile-title">Suivi de conso</span>
        </div>
        <p class="tile-soon-badge">Bientôt disponible</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  max-width: 1040px;
  margin: 0 auto;
}

.dashboard-section {
  margin-top: 32px;
}

.dashboard-section-top {
  margin-top: 0;
  margin-bottom: 32px;
}

.terminal-title {
  display: flex;
  justify-content: center;
  margin-bottom: 12px;
}

.terminal-window {
  width: fit-content;
  max-width: 100%;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 1px 2px rgba(20, 32, 30, 0.08), 0 16px 36px rgba(10, 24, 22, 0.22);
}

.terminal-bar {
  position: relative;
  display: flex;
  align-items: center;
  gap: 6px;
  background: #182c28;
  padding: 9px 14px;
}

.dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
}

.dot-red {
  background: #e5645a;
}

.dot-yellow {
  background: #e0b04c;
}

.dot-green {
  background: #5fbf7a;
}

.terminal-bar-title {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.72rem;
  color: #6e8b85;
  font-family: 'IBM Plex Mono', monospace;
}

.terminal-line {
  background: #0d1917;
  color: #59c9b6;
  text-shadow: 0 0 10px rgba(89, 201, 182, 0.35);
  font-family: 'IBM Plex Mono', monospace;
  font-size: 1.02rem;
  padding: 16px 22px 20px;
  margin: 0;
  white-space: normal;
}

.prompt-user {
  color: #7ab8e0;
}

.prompt-path {
  color: #e0a15c;
}

.prompt-sep {
  color: #6e8b85;
  margin: 0 2px 0 0;
}

.cursor {
  animation: blink 1s step-end infinite;
}

@keyframes blink {
  50% {
    opacity: 0;
  }
}

.subtitle {
  margin: 0 0 28px;
  color: #5b6478;
  font-size: 0.92rem;
  text-align: center;
}

.tile-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 14px;
}

.tile {
  text-align: left;
  background: #fff;
  border: 1px solid #d8deea;
  border-radius: 12px;
  padding: 18px 20px;
  box-shadow: 0 1px 2px rgba(20, 32, 30, 0.05), 0 6px 18px rgba(20, 32, 30, 0.05);
  font-family: inherit;
}

.tile-active {
  cursor: pointer;
  transition: border-color 0.15s ease, box-shadow 0.15s ease, transform 0.15s ease;
}

.tile-active:hover {
  border-color: #1e3a5f;
  box-shadow: 0 4px 16px rgba(20, 32, 30, 0.1);
  transform: translateY(-2px);
}

.tile-soon {
  opacity: 0.65;
}

.tile-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.tile-icon {
  flex-shrink: 0;
  color: #1e3a5f;
}

.tile-soon .tile-icon {
  color: #8a93a3;
}

.tile-title {
  font-weight: 600;
  font-size: 0.95rem;
  color: #14201e;
}

.tile-stat {
  margin: 0 0 4px;
  font-size: 0.9rem;
  color: #1e3a5f;
}

.tile-stat strong {
  font-size: 1.1rem;
}

.tile-loading {
  color: #8a93a3;
}

.tile-detail {
  margin: 0;
  font-size: 0.82rem;
  color: #5b6478;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tile-empty {
  font-style: italic;
}

.tile-alert {
  color: #a3271b;
  font-weight: 600;
}

.tile-soon-badge {
  display: inline-block;
  margin: 0;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  color: #8a93a3;
  background: #eef1f6;
  border-radius: 999px;
  padding: 4px 10px;
}
</style>
