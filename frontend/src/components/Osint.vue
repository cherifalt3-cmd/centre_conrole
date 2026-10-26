<script setup>
import { ref, computed, onMounted } from 'vue'
import { apiFetch } from '../api'

const query = ref('')
const submitting = ref(false)
const errorMessage = ref('')
const search = ref(null)
const history = ref([])

const SOURCE_LABELS = {
  subdomains: 'Sous-domaines',
  dns: 'DNS',
  ipRanges: 'Plages d\'adresses',
  asPrefixes: 'Espace d\'adressage annoncé',
  whois: 'Enregistrement du domaine',
  wayback: 'Historique des URLs',
}

const WHOIS_LABELS = {
  registrar: 'Registrar',
  registrant: 'Titulaire',
  admin_name: 'Contact admin',
  admin_email: 'Email admin',
  tech_name: 'Contact technique',
  tech_email: 'Email technique',
  created: 'Créé le',
  expires: 'Expire le',
  updated: 'Modifié le',
  statuses: 'Statuts',
  nameservers: 'Serveurs de noms',
  source: 'Source',
}

async function launchSearch() {
  const target = query.value.trim()
  if (!target) return

  submitting.value = true
  errorMessage.value = ''

  try {
    const response = await apiFetch('/api/osint/searches/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: target }),
    })
    const data = await response.json()

    if (!response.ok) {
      errorMessage.value = data.error || "Échec de la recherche."
      return
    }

    search.value = data
    history.value.unshift(data)
  } catch (e) {
    errorMessage.value = "Impossible de contacter le serveur."
  } finally {
    submitting.value = false
  }
}

async function fetchHistory() {
  const response = await apiFetch('/api/osint/searches/')
  const data = await response.json()
  history.value = data
  if (data.length) search.value = data[0]
}

onMounted(fetchHistory)

const findings = computed(() => search.value?.findings || {})
const subdomains = computed(() => findings.value.subdomains || [])
const dns = computed(() => findings.value.dns || {})
const ipRanges = computed(() => findings.value.ip_ranges || [])
const asPrefixes = computed(() => findings.value.as_prefixes || [])
const whois = computed(() => findings.value.whois || null)
const wayback = computed(() => findings.value.wayback || [])

const hasAnything = computed(
  () =>
    subdomains.value.length ||
    Object.keys(dns.value).length ||
    ipRanges.value.length ||
    asPrefixes.value.length ||
    whois.value ||
    wayback.value.length,
)

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('fr-FR', {
    day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit',
  })
}

function whoisValue(value) {
  if (Array.isArray(value)) return value.join(', ')
  if (/^\d{4}-\d{2}-\d{2}T/.test(value)) {
    return new Date(value).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })
  }
  return value
}
</script>

<template>
  <div class="osint">
    <div class="osint-header">
      <p class="eyebrow">Reconnaissance passive</p>
      <h2 class="osint-title">OSINT automatique</h2>
      <p class="osint-subtitle">
        Donne un domaine. L'app interroge des sources tierces qui détiennent déjà
        l'information publique — <strong>la cible n'est jamais contactée</strong> et rien
        n'apparaît dans ses journaux.
      </p>
    </div>

    <form class="osint-form" @submit.prevent="launchSearch">
      <span class="osint-input-wrap">
        <svg class="osint-input-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="2" />
          <line x1="16.5" y1="16.5" x2="21" y2="21" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
        </svg>
        <input v-model="query" type="text" class="osint-input" placeholder="exemple.com" :disabled="submitting" />
      </span>
      <button type="submit" class="osint-submit" :disabled="submitting || !query.trim()">
        <span v-if="submitting" class="spinner"></span>
        {{ submitting ? 'Recherche...' : 'Analyser' }}
      </button>
    </form>

    <p v-if="errorMessage" class="osint-error">{{ errorMessage }}</p>

    <template v-if="search">
      <div class="result-head">
        <span class="result-query">{{ search.query }}</span>
        <span class="result-date">{{ formatDate(search.created_at) }}</span>
      </div>

      <p v-if="search.error_message" class="osint-warning">{{ search.error_message }}</p>
      <p v-if="!hasAnything && !search.error_message" class="empty-hint">
        Aucune information publique trouvée pour ce domaine.
      </p>

      <div class="panels">
        <section v-if="subdomains.length" class="panel">
          <div class="panel-head">
            <span class="panel-title">{{ SOURCE_LABELS.subdomains }}</span>
            <span class="panel-count tabular">{{ subdomains.length }}</span>
          </div>
          <p class="panel-note">Issus des certificats TLS publics (Certificate Transparency)</p>
          <div class="panel-scroll panel-scroll-chips">
            <span v-for="name in subdomains" :key="name" class="chip">{{ name }}</span>
          </div>
        </section>

        <section v-if="Object.keys(dns).length" class="panel">
          <div class="panel-head">
            <span class="panel-title">{{ SOURCE_LABELS.dns }}</span>
          </div>
          <p class="panel-note">Via un résolveur public, pas les serveurs de la cible</p>
          <div class="panel-scroll">
            <div v-for="(values, type) in dns" :key="type" class="record">
              <span class="record-type">{{ type }}</span>
              <div class="record-values">
                <code v-for="value in values" :key="value" class="record-value">{{ value }}</code>
              </div>
            </div>
          </div>
        </section>

        <section v-if="ipRanges.length" class="panel">
          <div class="panel-head">
            <span class="panel-title">{{ SOURCE_LABELS.ipRanges }}</span>
            <span class="panel-count tabular">{{ ipRanges.length }}</span>
          </div>
          <p class="panel-note">
            Préfixes BGP et systèmes autonomes, via Team Cymru — indique si la cible
            a son propre espace d'adressage ou passe par un hébergeur
          </p>
          <div class="panel-scroll">
            <div v-for="block in ipRanges" :key="block.prefix" class="range">
              <div class="range-head">
                <code class="range-prefix">{{ block.prefix }}</code>
                <span class="range-asn">AS{{ block.asn }}</span>
                <span v-if="block.country" class="range-country">{{ block.country }}</span>
              </div>
              <p class="range-org">{{ block.as_name }}</p>
              <p class="range-meta">
                <span v-if="block.registry">{{ block.registry }}</span>
                <span v-if="block.allocated">alloué le {{ block.allocated }}</span>
                <span>{{ block.ips.join(', ') }}</span>
              </p>
            </div>
          </div>
        </section>

        <section v-if="asPrefixes.length" class="panel">
          <div class="panel-head">
            <span class="panel-title">{{ SOURCE_LABELS.asPrefixes }}</span>
          </div>
          <p class="panel-note">
            Tous les préfixes annoncés en BGP par ces AS, via Hurricane Electric —
            l'espace complet de l'organisation, pas seulement le bloc du domaine
          </p>
          <div v-for="block in asPrefixes" :key="block.asn" class="as-block">
            <div class="as-block-head">
              <span class="range-asn">AS{{ block.asn }}</span>
              <span class="as-block-count tabular">
                {{ block.prefixes.length }} préfixe{{ block.prefixes.length === 1 ? '' : 's' }}
              </span>
            </div>
            <div class="panel-scroll panel-scroll-chips">
              <code v-for="prefix in block.prefixes" :key="prefix" class="prefix-chip">
                {{ prefix }}
              </code>
            </div>
          </div>
        </section>

        <section v-if="whois" class="panel">
          <div class="panel-head">
            <span class="panel-title">{{ SOURCE_LABELS.whois }}</span>
          </div>
          <p class="panel-note">RDAP, le WHOIS structuré des registres</p>
          <div class="panel-scroll">
            <template v-for="(label, key) in WHOIS_LABELS" :key="key">
              <div v-if="whois[key] && whois[key].length !== 0" class="record">
                <span class="record-type record-type-wide">{{ label }}</span>
                <div class="record-values">
                  <span class="whois-value">{{ whoisValue(whois[key]) }}</span>
                </div>
              </div>
            </template>
          </div>
        </section>

        <section v-if="wayback.length" class="panel panel-wide">
          <div class="panel-head">
            <span class="panel-title">{{ SOURCE_LABELS.wayback }}</span>
            <span class="panel-count tabular">{{ wayback.length }}</span>
          </div>
          <p class="panel-note">
            URLs archivées par Archive.org — révèle d'anciens endpoints et fichiers exposés
          </p>
          <div class="url-list">
            <a
              v-for="url in wayback"
              :key="url"
              :href="url"
              target="_blank"
              rel="noopener noreferrer"
              class="url-item"
            >
              {{ url }}
            </a>
          </div>
        </section>
      </div>
    </template>

    <div v-if="history.length > 1" class="osint-history">
      <p class="eyebrow">Recherches précédentes</p>
      <ul class="history-list">
        <li v-for="item in history.slice(1)" :key="item.id">
          <button type="button" class="history-item" @click="search = item">
            <span class="history-query">{{ item.query }}</span>
            <span class="history-date">{{ formatDate(item.created_at) }}</span>
          </button>
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.osint {
  max-width: 1040px;
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
  margin: 0 auto;
  max-width: 580px;
  font-size: 0.88rem;
  line-height: 1.6;
  color: var(--text-muted);
}

.osint-subtitle strong {
  color: var(--accent);
  font-weight: 500;
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
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.88rem;
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
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 11px 22px;
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

.spinner {
  width: 11px;
  height: 11px;
  border: 1.5px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.osint-error {
  text-align: center;
  color: var(--danger);
  font-size: 0.86rem;
  margin-bottom: 18px;
}

.osint-warning {
  color: var(--warning);
  font-size: 0.84rem;
  margin: 0 0 16px;
}

.empty-hint {
  color: var(--text-muted);
  font-size: 0.88rem;
  margin: 0 0 16px;
}

/* ---------- entete du resultat ---------- */
.result-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 10px;
  padding-bottom: 12px;
  margin-bottom: 18px;
  border-bottom: 1px solid var(--border);
}

.result-query {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 1.05rem;
  color: var(--text);
  word-break: break-all;
}

.result-date {
  flex-shrink: 0;
  font-size: 0.76rem;
  color: var(--text-faint);
}

/* ---------- panneaux ---------- */
.panels {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 14px;
  align-items: start;
}

.panel {
  background: var(--glass-1);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 17px 19px;
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  box-shadow: var(--shadow-2);
}

.panel-wide {
  grid-column: 1 / -1;
}

.panel-head {
  display: flex;
  align-items: center;
  gap: 9px;
  margin-bottom: 3px;
}

.panel-title {
  font-weight: 600;
  font-size: 0.95rem;
  color: var(--text);
}

.panel-count {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.72rem;
  font-weight: 500;
  color: var(--accent);
  background: var(--accent-soft);
  border: 1px solid var(--accent-line);
  border-radius: 999px;
  padding: 1px 9px;
}

.panel-note {
  margin: 0 0 14px;
  font-size: 0.75rem;
  font-style: italic;
  color: var(--text-faint);
}

/* ---------- sous-domaines ---------- */
/* Tout contenu de panneau defile dans son cadre plutot que d'etirer la page :
   un domaine peut avoir 100 sous-domaines, des centaines de prefixes ou une
   douzaine d'enregistrements TXT. La page garde ainsi une hauteur stable. */
.panel-scroll {
  max-height: 200px;
  overflow-y: auto;
  padding: 10px 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: rgba(0, 0, 0, 0.18);
}

.panel-scroll-chips {
  display: flex;
  flex-wrap: wrap;
  align-content: flex-start;
  gap: 5px;
}

.chip,
.prefix-chip {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.72rem;
  padding: 2px 9px;
  background: var(--glass-2);
  border: 1px solid var(--border);
  border-radius: 999px;
  color: var(--text-muted);
  word-break: break-all;
  height: fit-content;
}

/* ---------- enregistrements DNS / WHOIS ---------- */
.record {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 7px 0;
  border-top: 1px solid var(--border);
}

.record:first-of-type {
  border-top: none;
  padding-top: 0;
}

.record-type {
  flex-shrink: 0;
  width: 48px;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.7rem;
  font-weight: 500;
  letter-spacing: 0.06em;
  color: var(--accent-2);
  padding-top: 2px;
}

.record-type-wide {
  width: 120px;
  letter-spacing: 0;
  text-transform: none;
  color: var(--text-faint);
}

.record-values {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}

.record-value {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.74rem;
  color: var(--text-muted);
  word-break: break-all;
}

.whois-value {
  font-size: 0.82rem;
  color: var(--text);
  word-break: break-word;
}

/* ---------- plages d'adresses ---------- */
.range {
  padding: 11px 0;
  border-top: 1px solid var(--border);
}

.range:first-of-type {
  border-top: none;
  padding-top: 0;
}

.range-head {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 5px;
}

.range-prefix {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.86rem;
  color: var(--text);
}

.range-asn {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.68rem;
  font-weight: 500;
  letter-spacing: 0.04em;
  color: var(--accent-2);
  background: var(--info-soft);
  border: 1px solid rgba(106, 184, 245, 0.25);
  border-radius: 999px;
  padding: 1px 8px;
}

.range-country {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.68rem;
  font-weight: 500;
  color: var(--text-muted);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 1px 8px;
}

.range-org {
  margin: 0 0 4px;
  font-size: 0.82rem;
  color: var(--text);
}

.range-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 4px 12px;
  margin: 0;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.7rem;
  color: var(--text-faint);
}

/* ---------- espace d'adressage annonce ---------- */
.as-block {
  padding-top: 11px;
  margin-top: 11px;
  border-top: 1px solid var(--border);
}

.as-block:first-of-type {
  padding-top: 0;
  margin-top: 0;
  border-top: none;
}

.as-block-head {
  display: flex;
  align-items: center;
  gap: 9px;
  margin-bottom: 9px;
}

.as-block-count {
  font-size: 0.74rem;
  color: var(--text-faint);
}

/* ---------- historique des URLs ---------- */
.url-list {
  display: flex;
  flex-direction: column;
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: rgba(0, 0, 0, 0.18);
}

.url-item {
  padding: 7px 12px;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.72rem;
  color: var(--text-muted);
  text-decoration: none;
  word-break: break-all;
  border-bottom: 1px solid var(--border);
  transition: background 0.14s ease, color 0.14s ease;
}

.url-item:last-child {
  border-bottom: none;
}

.url-item:hover {
  background: var(--accent-soft);
  color: var(--text);
}

/* ---------- historique des recherches ---------- */
.osint-history {
  margin-top: 26px;
}

.history-list {
  list-style: none;
  margin: 10px 0 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.history-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  width: 100%;
  padding: 9px 14px;
  background: var(--glass-1);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  cursor: pointer;
  text-align: left;
  transition: background 0.15s ease, border-color 0.15s ease;
}

.history-item:hover {
  background: var(--glass-2);
  border-color: var(--accent-line);
}

.history-query {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.83rem;
  color: var(--text);
  word-break: break-all;
}

.history-date {
  flex-shrink: 0;
  font-size: 0.74rem;
  color: var(--text-faint);
}
</style>
