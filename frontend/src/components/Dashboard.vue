<script setup>
import { ref, computed, onMounted } from 'vue'
import { authToken } from '../auth'

const emit = defineEmits(['navigate'])

const targets = ref([])
const loaded = ref(false)

async function fetchTargets() {
  const response = await fetch('http://127.0.0.1:8000/api/recon/targets/', {
    headers: { Authorization: `Token ${authToken.value}` },
  })
  targets.value = await response.json()
  loaded.value = true
}

onMounted(fetchTargets)

const targetCount = computed(() => targets.value.length)
const lastTarget = computed(() => (targets.value.length ? targets.value[0] : null))
</script>

<template>
  <div class="dashboard">
    <h2>Bienvenue</h2>
    <p class="subtitle">Vue d'ensemble de tes modules</p>

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

      <div class="tile tile-soon">
        <div class="tile-head">
          <svg class="tile-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="3" y="4" width="18" height="16" rx="1" stroke="currentColor" stroke-width="2" />
            <line x1="3" y1="9" x2="21" y2="9" stroke="currentColor" stroke-width="2" />
            <line x1="7" y1="13" x2="15" y2="13" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
            <line x1="7" y1="17" x2="12" y2="17" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
          </svg>
          <span class="tile-title">Veille cybersécu &amp; IA</span>
        </div>
        <p class="tile-soon-badge">Bientôt disponible</p>
      </div>

      <div class="tile tile-soon">
        <div class="tile-head">
          <svg class="tile-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="3" y="4" width="18" height="16" rx="1" stroke="currentColor" stroke-width="2" />
            <line x1="9" y1="4" x2="9" y2="20" stroke="currentColor" stroke-width="2" />
            <line x1="15" y1="4" x2="15" y2="20" stroke="currentColor" stroke-width="2" />
          </svg>
          <span class="tile-title">Kanban projets</span>
        </div>
        <p class="tile-soon-badge">Bientôt disponible</p>
      </div>

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
  max-width: 900px;
  margin: 0 auto;
}

h2 {
  margin: 0 0 4px;
  font-size: 1.5rem;
  font-weight: 700;
  color: #14201e;
}

.subtitle {
  margin: 0 0 28px;
  color: #5b6478;
  font-size: 0.92rem;
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
}

.tile-empty {
  font-style: italic;
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
