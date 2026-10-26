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
  try {
    const response = await apiFetch('/api/osint/searches/')
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const data = await response.json()
    history.value = data
    if (data.length) search.value = data[0]
  } catch {
    errorMessage.value = "Impossible de charger l'historique des recherches."
  }
}

onMounted(fetchHistory)

const findings = computed(() => search.value?.findings || {})
const subdomains = computed(() => findings.value.subdomains || [])
const dns = computed(() => findings.value.dns || {})
const ipRanges = computed(() => findings.value.ip_ranges || [])
const asPrefixes = computed(() => findings.value.as_prefixes || [])
const whois = computed(() => findings.value.whois || null)
// Chaque lien pointe vers la copie archivee, jamais vers l'URL d'origine : un clic
// sur le site reel contacterait la cible depuis ton IP et romprait le mode
// passif. Les recherches anterieures ne stockaient que l'URL : on les envoie vers
// le calendrier des captures d'Archive.org, qui reste une page de l'archive.
const wayback = computed(() =>
  (findings.value.wayback || []).map((entry) =>
    typeof entry === 'string'
      ? { url: entry, snapshot: `https://web.archive.org/web/*/${entry}` }
      : entry,
  ),
)

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
      <p id="osint-subtitle" class="osint-subtitle">
        Donne un domaine. L'app interroge des sources tierces qui détiennent déjà
        l'information publique — <strong>la cible n'est jamais contactée</strong> et rien
        n'apparaît dans ses journaux.
      </p>
    </div>

    <form class="osint-form" @submit.prevent="launchSearch">
      <span class="osint-input-wrap">
        <svg aria-hidden="true" focusable="false" class="osint-input-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="2" />
          <line x1="16.5" y1="16.5" x2="21" y2="21" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
        </svg>
        <label for="osint-query" class="visually-hidden">Domaine à analyser</label>
        <input
          id="osint-query"
          v-model="query"
          type="text"
          class="osint-input"
          placeholder="exemple.com"
          aria-describedby="osint-subtitle"
          :disabled="submitting"
        />
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
            Anciens endpoints et fichiers exposés. Chaque lien ouvre la copie archivée :
            le site de la cible n'est jamais contacté.
          </p>
          <div class="url-list">
            <a
              v-for="entry in wayback"
              :key="entry.snapshot"
              :href="entry.snapshot"
              target="_blank"
              rel="noopener noreferrer"
              referrerpolicy="no-referrer"
              class="url-item"
            >
              {{ entry.url }}
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
  margin-bottom: 24px;
}

.osint-title {
  margin: 6px 0 8px;
  font-size: var(--fs-2xl);
  font-weight: 600;
  letter-spacing: -0.02em;
  color: var(--text);
}

.osint-subtitle {
  margin: 0 auto;
  max-width: 580px;
  font-size: var(--fs-base);
  line-height: 1.6;
  color: var(--text-muted);
}

.osint-subtitle strong {
  color: var(--accent-text);
  font-weight: 500;
}

/* ---------- formulaire ---------- */
.osint-form {
  display: flex;
  gap: 10px;
  max-width: 540px;
  margin: 0 auto 24px;
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
  padding: 12px 16px 12px 40px;
  background: var(--glass-1);
  border: 1px solid var(--border-input);
  border-radius: var(--radius-sm);
  color: var(--text);
  font-family: 'IBM Plex Mono', monospace;
  font-size: var(--fs-base);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  transition: border-color 0.16s ease, box-shadow 0.16s ease, background 0.16s ease;
}

.osint-input::placeholder {
  color: var(--text-faint);
}

.osint-input:focus {
  background: var(--glass-2);
  border-color: var(--accent);
}

.osint-submit {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: linear-gradient(135deg, var(--accent-strong), #6355d6);
  color: #fff;
  border: 1px solid var(--accent-line);
  border-radius: var(--radius-sm);
  font-weight: 500;
  font-size: var(--fs-base);
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
  font-size: var(--fs-base);
  margin-bottom: 20px;
}

.osint-warning {
  color: var(--warning);
  font-size: var(--fs-sm);
  margin: 0 0 16px;
}

.empty-hint {
  color: var(--text-muted);
  font-size: var(--fs-base);
  margin: 0 0 16px;
}

/* ---------- entete du resultat ---------- */
.result-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 10px;
  padding-bottom: 12px;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--border);
}

.result-query {
  font-family: 'IBM Plex Mono', monospace;
  font-size: var(--fs-md);
  color: var(--text);
  word-break: break-all;
}

.result-date {
  flex-shrink: 0;
  font-size: var(--fs-xs);
  color: var(--text-faint);
}

/* ---------- panneaux ---------- */
.panels {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 16px;
  align-items: start;
}

.panel {
  background: var(--glass-1);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px 20px;
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
  gap: 10px;
  margin-bottom: 4px;
}

.panel-title {
  font-weight: 600;
  font-size: var(--fs-md);
  color: var(--text);
}

.panel-count {
  font-family: 'IBM Plex Mono', monospace;
  font-size: var(--fs-xs);
  font-weight: 500;
  color: var(--accent-text);
  background: var(--accent-tint);
  border: 1px solid var(--accent-line);
  border-radius: 999px;
  padding: 1px 10px;
}

.panel-note {
  margin: 0 0 16px;
  font-size: var(--fs-xs);
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
  gap: 6px;
}

.chip,
.prefix-chip {
  font-family: 'IBM Plex Mono', monospace;
  font-size: var(--fs-xs);
  padding: 2px 10px;
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
  padding: 8px 0;
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
  font-size: var(--fs-xs);
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
  gap: 4px;
  min-width: 0;
}

.record-value {
  font-family: 'IBM Plex Mono', monospace;
  font-size: var(--fs-xs);
  color: var(--text-muted);
  word-break: break-all;
}

.whois-value {
  font-size: var(--fs-sm);
  color: var(--text);
  word-break: break-word;
}

/* ---------- plages d'adresses ---------- */
.range {
  padding: 12px 0;
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
  margin-bottom: 6px;
}

.range-prefix {
  font-family: 'IBM Plex Mono', monospace;
  font-size: var(--fs-base);
  color: var(--text);
}

.range-asn {
  font-family: 'IBM Plex Mono', monospace;
  font-size: var(--fs-xs);
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
  font-size: var(--fs-xs);
  font-weight: 500;
  color: var(--text-muted);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 1px 8px;
}

.range-org {
  margin: 0 0 4px;
  font-size: var(--fs-sm);
  color: var(--text);
}

.range-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 4px 12px;
  margin: 0;
  font-family: 'IBM Plex Mono', monospace;
  font-size: var(--fs-xs);
  color: var(--text-faint);
}

/* ---------- espace d'adressage annonce ---------- */
.as-block {
  padding-top: 12px;
  margin-top: 12px;
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
  gap: 10px;
  margin-bottom: 10px;
}

.as-block-count {
  font-size: var(--fs-xs);
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
  padding: 8px 12px;
  font-family: 'IBM Plex Mono', monospace;
  font-size: var(--fs-xs);
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
  margin-top: 24px;
}

.history-list {
  list-style: none;
  margin: 10px 0 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.history-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  width: 100%;
  padding: 10px 16px;
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
  font-size: var(--fs-sm);
  color: var(--text);
  word-break: break-all;
}

.history-date {
  flex-shrink: 0;
  font-size: var(--fs-xs);
  color: var(--text-faint);
}
</style>
