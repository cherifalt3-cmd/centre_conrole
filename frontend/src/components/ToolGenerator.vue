<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { authToken } from '../auth'

const tools = ref([])
const presets = ref([])
const activeCategory = ref(null)
const activeMetasploitService = ref(null)
const activeTab = ref('suggestions')
const phase = ref(null)
const selectedToolId = ref('')
const toolSearch = ref('')
const openToolDropdown = ref(false)
const address = ref('')
const domain = ref('')
const optionValues = reactive({})

const customCommand = ref('')
const presetCopied = ref(false)

const openCatalogFor = ref(null)

function closeCatalogSoon(optionId) {
  setTimeout(() => {
    if (openCatalogFor.value === optionId) openCatalogFor.value = null
  }, 150)
}

function filterCatalogEntries(option) {
  if (!option.catalog) return []
  const query = (optionValues[option.id] || '').toLowerCase()
  const entries = option.catalog.entries
  if (!query) return entries.slice(0, 8)
  return entries
    .filter((e) => e.value.toLowerCase().includes(query) || e.description.toLowerCase().includes(query))
    .slice(0, 8)
}

function selectCatalogEntry(optionId, value) {
  optionValues[optionId] = value
  openCatalogFor.value = null
}

async function fetchTools() {
  const response = await fetch('http://127.0.0.1:8000/api/recon/tools/', {
    headers: { Authorization: `Token ${authToken.value}` },
  })
  tools.value = await response.json()
}

async function fetchPresets() {
  const response = await fetch('http://127.0.0.1:8000/api/recon/command-presets/', {
    headers: { Authorization: `Token ${authToken.value}` },
  })
  presets.value = await response.json()
}

onMounted(() => {
  fetchTools()
  fetchPresets()
})

function applyPreset(preset) {
  customCommand.value = preset.template
    .replaceAll('{address}', address.value || '<adresse>')
    .replaceAll('{domain}', domain.value || '<domaine>')
  presetCopied.value = false
}

const CATEGORY_CLASSES = {
  SMB: 'badge-smb',
  FTP: 'badge-ftp',
  SSH: 'badge-ssh',
  HTTP: 'badge-http',
  SMTP: 'badge-smtp',
  SQL: 'badge-sql',
  Général: 'badge-general',
  'DNS / OSINT': 'badge-dns',
  Metasploit: 'badge-metasploit',
  'DNS / SNMP / TFTP': 'badge-snmp',
}

function categoryClass(category) {
  return CATEGORY_CLASSES[category] || 'badge-default'
}

// Liste des catégories présentes dans les suggestions, dans un ordre fixe et lisible
const CATEGORY_ORDER = ['Général', 'DNS / OSINT', 'SMB', 'FTP', 'SSH', 'HTTP', 'SMTP', 'SQL', 'DNS / SNMP / TFTP', 'Metasploit']

const categories = computed(() => {
  const present = new Set(presets.value.map((p) => p.category).filter(Boolean))
  return CATEGORY_ORDER.filter((c) => present.has(c))
})

// Pour Metasploit, le service (HTTP, FTP...) est déduit du préfixe du libellé ("HTTP — Version du serveur")
function presetService(preset) {
  return preset.label.includes(' — ') ? preset.label.split(' — ')[0] : null
}

const metasploitServices = computed(() => {
  const present = new Set(
    presets.value.filter((p) => p.category === 'Metasploit').map((p) => presetService(p)).filter(Boolean),
  )
  return [...present]
})

const filteredPresets = computed(() => {
  let list = presets.value

  if (activeCategory.value) {
    list = list.filter((p) => p.category === activeCategory.value)
  }

  if (activeCategory.value === 'Metasploit' && activeMetasploitService.value) {
    list = list.filter((p) => presetService(p) === activeMetasploitService.value)
  }

  return list
})

// Découpe une commande en mots colorables : commande de base / flags / adresse cible
function tokenizeCommand(command) {
  if (!command) return []
  const tokens = command.trim().split(/\s+/)

  return tokens.map((text, index) => {
    let type = 'value'
    if (index === 0) type = 'base'
    else if (text.startsWith('-')) type = 'flag'
    else if (index === tokens.length - 1) type = 'target'
    return { text, type }
  })
}

async function copyCustomCommand() {
  await navigator.clipboard.writeText(customCommand.value)
  presetCopied.value = true
}

const filteredTools = computed(() => {
  if (!phase.value) return tools.value
  return tools.value.filter((t) => t.phase === phase.value)
})

const selectedTool = computed(() => tools.value.find((t) => t.id === selectedToolId.value))

// Regroupe les options de l'outil sélectionné par leur "group" (ex: Détection, Scan, Performance...)
const groupedOptions = computed(() => {
  if (!selectedTool.value) return []
  const groups = []
  const byName = {}

  for (const option of selectedTool.value.options) {
    const name = option.group || 'Autres'
    if (!byName[name]) {
      byName[name] = { name, options: [] }
      groups.push(byName[name])
    }
    byName[name].options.push(option)
  }

  return groups
})

const toolResults = computed(() =>
  filteredTools.value.filter((t) => t.name.toLowerCase().includes(toolSearch.value.toLowerCase())),
)

function selectPhase(p) {
  phase.value = p === phase.value ? null : p
}

function selectTool(tool) {
  selectedToolId.value = tool.id
  toolSearch.value = tool.name
  openToolDropdown.value = false
}

function closeToolDropdownSoon() {
  setTimeout(() => {
    openToolDropdown.value = false
  }, 150)
}

function toggleMultiChoice(optionId, value) {
  const current = optionValues[optionId] || []
  const index = current.indexOf(value)
  if (index === -1) current.push(value)
  else current.splice(index, 1)
}

function selectSingleChoice(optionId, value) {
  optionValues[optionId] = optionValues[optionId] === value ? '' : value
}

// Quand on change d'outil, on réinitialise les valeurs de ses options
watch(selectedTool, (tool) => {
  Object.keys(optionValues).forEach((key) => delete optionValues[key])

  if (!tool) return

  for (const option of tool.options) {
    if (option.option_type === 'switch') optionValues[option.id] = false
    else if (option.option_type === 'multi_choice') optionValues[option.id] = []
    else optionValues[option.id] = ''
  }
})

function formatFreeValue(flag, value) {
  if (!flag) return value
  // Certains flags se collent directement à la valeur (--script=, @serveur), d'autres ont besoin d'un espace (-p, -h)
  return /[=@]$/.test(flag) ? `${flag}${value}` : `${flag} ${value}`
}

const generatedCommand = computed(() => {
  if (!selectedTool.value) return ''

  const parts = [selectedTool.value.base_command]

  for (const option of selectedTool.value.options) {
    const value = optionValues[option.id]

    if (option.option_type === 'switch' && value) {
      parts.push(option.flag)
    } else if (option.option_type === 'single_choice' && value) {
      parts.push(value)
    } else if (option.option_type === 'multi_choice' && value?.length) {
      parts.push(...value)
    } else if (option.option_type === 'free_value' && value) {
      parts.push(formatFreeValue(option.flag, value))
    }
  }

  const target = selectedTool.value.target_field === 'domain' ? domain.value : address.value
  if (target) {
    parts.push(
      selectedTool.value.target_flag ? formatFreeValue(selectedTool.value.target_flag, target) : target,
    )
  }

  return parts.join(' ')
})

// Le constructeur alimente en direct la même barre de commande que les suggestions
watch(generatedCommand, (cmd) => {
  if (selectedTool.value) {
    customCommand.value = cmd
    presetCopied.value = false
  }
})
</script>

<template>
  <div class="generator">
    <div class="terminal-title">
      <div class="terminal-window">
        <div class="terminal-bar">
          <span class="dot dot-red"></span>
          <span class="dot dot-yellow"></span>
          <span class="dot dot-green"></span>
          <span class="terminal-bar-title">bash — recon</span>
        </div>
        <p class="terminal-line">
          <span class="prompt-user">pro@centre-controle</span><span class="prompt-sep">:</span><span class="prompt-path">~</span><span class="prompt-sep">$</span>
          Générateur de commandes<span class="cursor">_</span>
        </p>
      </div>
    </div>

    <div class="top-panel">
      <div class="target-fields">
        <div>
          <label class="step-label">Adresse de la cible</label>
          <input v-model="address" type="text" class="address-input" placeholder="Ex : 192.168.1.10" />
        </div>
        <div>
          <label class="step-label">Nom de domaine</label>
          <input v-model="domain" type="text" class="address-input" placeholder="Ex : exemple.com" />
        </div>
      </div>

      <div class="result sticky-result">
        <label class="step-label">Commande (modifiable)</label>
        <textarea
          v-model="customCommand"
          class="command-edit"
          rows="2"
          placeholder="Choisis une suggestion ou un outil ci-dessous, ou écris ta commande ici..."
        ></textarea>
        <button type="button" class="copy-btn" @click="copyCustomCommand" :disabled="!customCommand">
          {{ presetCopied ? 'Copié !' : 'Copier' }}
        </button>
      </div>
    </div>

    <div class="tabbed-area">
      <div class="tab-content">
        <div v-if="activeTab === 'suggestions'" class="quick-section">
          <div class="category-filters">
            <button
              type="button"
              :class="['filter-btn', { active: activeCategory === null }]"
              @click="activeCategory = null; activeMetasploitService = null"
            >
              Tous
            </button>
            <button
              v-for="category in categories"
              :key="category"
              type="button"
              :class="['filter-btn', { active: activeCategory === category }]"
              @click="activeCategory = category; activeMetasploitService = null"
            >
              {{ category }}
            </button>
          </div>

          <div v-if="activeCategory === 'Metasploit'" class="category-filters sub-filters">
            <button
              type="button"
              :class="['filter-btn', 'filter-btn-sub', { active: activeMetasploitService === null }]"
              @click="activeMetasploitService = null"
            >
              Tous services
            </button>
            <button
              v-for="service in metasploitServices"
              :key="service"
              type="button"
              :class="['filter-btn', 'filter-btn-sub', { active: activeMetasploitService === service }]"
              @click="activeMetasploitService = service"
            >
              {{ service }}
            </button>
          </div>

          <div class="preset-grid-wrap">
            <div class="preset-grid">
              <button
                v-for="preset in filteredPresets"
                :key="preset.id"
                type="button"
                class="preset-card"
                @click="applyPreset(preset)"
              >
                <span v-if="preset.category" :class="['preset-badge', categoryClass(preset.category)]">
                  {{ preset.category }}
                </span>
                <span class="preset-label">{{ preset.label }}</span>
                <code class="preset-preview">
                  <span
                    v-for="(token, index) in tokenizeCommand(preset.template)"
                    :key="index"
                    :class="'tok-' + token.type"
                  >{{ token.text }} </span>
                </code>
              </button>
              <p v-if="filteredPresets.length === 0" class="empty-hint">Aucune suggestion dans cette catégorie.</p>
            </div>
          </div>
        </div>

        <div v-else class="builder-section">
          <div class="builder-row">
            <div class="phase-buttons">
              <button type="button" :class="['phase-btn', { active: phase === null }]" @click="phase = null">
                Tous
              </button>
              <button
                type="button"
                :class="['phase-btn', { active: phase === 'passive' }]"
                @click="selectPhase('passive')"
              >
                Passive
              </button>
              <button
                type="button"
                :class="['phase-btn', { active: phase === 'active' }]"
                @click="selectPhase('active')"
              >
                Active
              </button>
            </div>

            <span class="chip-input-wrap">
              <input
                type="text"
                v-model="toolSearch"
                class="chip-input tool-search"
                placeholder="Chercher un outil..."
                @focus="openToolDropdown = true"
                @blur="closeToolDropdownSoon"
              />
              <div v-if="openToolDropdown" class="catalog-dropdown">
                <button
                  v-for="tool in toolResults"
                  :key="tool.id"
                  type="button"
                  class="catalog-item"
                  @mousedown.prevent="selectTool(tool)"
                >
                  <span class="catalog-value">{{ tool.name }}</span>
                  <span class="catalog-desc">{{ tool.phase === 'active' ? 'Active' : 'Passive' }}</span>
                </button>
                <p v-if="toolResults.length === 0" class="catalog-empty">Aucun outil trouvé.</p>
              </div>
            </span>
          </div>

          <div v-if="selectedTool" class="options-panel">
          <div v-for="grp in groupedOptions" :key="grp.name" class="option-section">
            <p class="option-section-label">{{ grp.name }}</p>
            <div class="option-section-row">
            <div v-for="option in grp.options" :key="option.id" class="option-group">
              <span class="option-tag">{{ option.label }}</span>

              <button
                v-if="option.option_type === 'switch'"
                type="button"
                :class="['chip', { active: optionValues[option.id] }]"
                @click="optionValues[option.id] = !optionValues[option.id]"
              >
                {{ option.flag }}
              </button>

              <template v-else-if="option.option_type === 'single_choice'">
                <button
                  v-for="choice in option.choices"
                  :key="choice.id"
                  type="button"
                  :class="['chip', { active: optionValues[option.id] === choice.value }]"
                  @click="selectSingleChoice(option.id, choice.value)"
                >
                  {{ choice.label }}
                </button>
              </template>

              <template v-else-if="option.option_type === 'multi_choice'">
                <button
                  v-for="choice in option.choices"
                  :key="choice.id"
                  type="button"
                  :class="['chip', { active: optionValues[option.id]?.includes(choice.value) }]"
                  @click="toggleMultiChoice(option.id, choice.value)"
                >
                  {{ choice.label }}
                </button>
              </template>

              <span v-else-if="option.option_type === 'free_value'" class="chip-input-wrap">
                <input
                  type="text"
                  v-model="optionValues[option.id]"
                  class="chip-input"
                  placeholder="Valeur..."
                  @focus="openCatalogFor = option.catalog ? option.id : null"
                  @blur="closeCatalogSoon(option.id)"
                />
                <div v-if="option.catalog && openCatalogFor === option.id" class="catalog-dropdown">
                  <button
                    v-for="entry in filterCatalogEntries(option)"
                    :key="entry.id"
                    type="button"
                    class="catalog-item"
                    @mousedown.prevent="selectCatalogEntry(option.id, entry.value)"
                  >
                    <span class="catalog-value">{{ entry.value }}</span>
                    <span class="catalog-desc">{{ entry.description }}</span>
                  </button>
                  <p v-if="filterCatalogEntries(option).length === 0" class="catalog-empty">Aucun résultat.</p>
                </div>
              </span>
            </div>
            </div>
          </div>
          </div>
        </div>
      </div>

      <div class="tab-sidebar">
        <button
          type="button"
          :class="['tab-btn', { active: activeTab === 'suggestions' }]"
          @click="activeTab = 'suggestions'"
        >
          <span class="tab-btn-label">Suggestions</span>
          <span class="tab-btn-sub">Commandes prêtes</span>
        </button>
        <button
          type="button"
          :class="['tab-btn', { active: activeTab === 'builder' }]"
          @click="activeTab = 'builder'"
        >
          <span class="tab-btn-label">Construire</span>
          <span class="tab-btn-sub">Outil par outil</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.generator {
  max-width: 900px;
  margin: 0 auto;
}

.terminal-title {
  display: flex;
  justify-content: center;
  margin-bottom: 32px;
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

.dot-red {
  background: #ff5f57;
}

.dot-yellow {
  background: #febc2e;
}

.dot-green {
  background: #28c840;
}

.terminal-bar-title {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.7rem;
  color: var(--text-faint);
  font-family: 'IBM Plex Mono', monospace;
  white-space: nowrap;
}

.terminal-line {
  background: rgba(7, 8, 12, 0.72);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  color: var(--success);
  text-shadow: 0 0 14px rgba(61, 220, 151, 0.45);
  font-family: 'IBM Plex Mono', monospace;
  font-size: 1.02rem;
  padding: 18px 26px 22px;
  margin: 0;
  white-space: normal;
}

.prompt-user {
  color: var(--accent-2);
}

.prompt-path {
  color: var(--warning);
}

.prompt-sep {
  color: var(--text-faint);
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

.top-panel {
  margin-bottom: 20px;
}

.target-fields {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

@media (max-width: 520px) {
  .target-fields {
    grid-template-columns: 1fr;
  }
}

.tabbed-area {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.tab-sidebar {
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex-shrink: 0;
  width: 168px;
}

.tab-btn {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
  padding: 13px 16px;
  border: 1px solid var(--border);
  background: var(--glass-1);
  border-radius: var(--radius);
  cursor: pointer;
  text-align: left;
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  transition: border-color 0.16s ease, background 0.16s ease, box-shadow 0.16s ease;
}

.tab-btn:hover {
  background: var(--glass-2);
  border-color: var(--border-strong);
}

.tab-btn-label {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text);
}

.tab-btn-sub {
  font-size: 0.73rem;
  color: var(--text-faint);
}

.tab-btn.active {
  background: var(--accent-soft);
  border-color: var(--accent-line);
  box-shadow: var(--ring-accent);
}

.tab-btn.active .tab-btn-label {
  color: #fff;
}

.tab-btn.active .tab-btn-sub {
  color: #a396ff;
}

.tab-content {
  flex: 1;
  min-width: 0;
}

.quick-section,
.builder-section {
  background: var(--glass-1);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 18px 20px;
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  box-shadow: var(--shadow-2);
}

.category-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
}

.filter-btn {
  padding: 5px 13px;
  border: 1px solid var(--border);
  background: var(--glass-1);
  color: var(--text-muted);
  border-radius: 999px;
  cursor: pointer;
  font-size: 0.79rem;
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

.sub-filters {
  margin: -4px 0 12px 4px;
}

.filter-btn-sub {
  padding: 3px 10px;
  font-size: 0.73rem;
}

.preset-grid-wrap {
  max-height: 420px;
  overflow-y: auto;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 12px;
  background: rgba(0, 0, 0, 0.18);
}

.preset-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 10px;
}

.preset-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
  text-align: left;
  padding: 13px 15px;
  border: 1px solid var(--border);
  background: var(--glass-1);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: border-color 0.16s ease, background 0.16s ease, box-shadow 0.16s ease, transform 0.16s ease;
}

.preset-card:hover {
  border-color: var(--accent-line);
  background: var(--glass-2);
  box-shadow: var(--ring-accent);
  transform: translateY(-2px);
}

.preset-badge {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.63rem;
  font-weight: 500;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  padding: 2px 9px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: var(--glass-2);
  color: var(--text-muted);
}

.badge-smb {
  background: var(--info-soft);
  border-color: rgba(106, 184, 245, 0.25);
  color: var(--info);
}

.badge-ftp {
  background: var(--sev-high-soft);
  border-color: rgba(255, 160, 87, 0.25);
  color: var(--sev-high);
}

.badge-ssh {
  background: var(--glass-3);
  border-color: var(--border-strong);
  color: #b9c2d6;
}

.badge-http {
  background: var(--accent-soft);
  border-color: var(--accent-line);
  color: #a396ff;
}

.badge-smtp {
  background: var(--danger-soft);
  border-color: rgba(245, 118, 107, 0.25);
  color: var(--danger);
}

.badge-sql {
  background: rgba(154, 214, 100, 0.12);
  border-color: rgba(154, 214, 100, 0.25);
  color: #9ad664;
}

.badge-general,
.badge-default {
  background: var(--glass-2);
  border-color: var(--border);
  color: var(--text-muted);
}

.badge-dns {
  background: var(--success-soft);
  border-color: rgba(61, 220, 151, 0.25);
  color: var(--success);
}

.badge-metasploit {
  background: rgba(160, 130, 255, 0.14);
  border-color: rgba(160, 130, 255, 0.3);
  color: #b39dff;
}

.badge-snmp {
  background: var(--sev-medium-soft);
  border-color: rgba(245, 194, 107, 0.25);
  color: var(--sev-medium);
}

.preset-label {
  font-weight: 600;
  font-size: 0.88rem;
  color: var(--text);
}

.preset-preview {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.75rem;
  color: var(--text-muted);
  word-break: break-all;
  line-height: 1.5;
}

.command-edit {
  width: 100%;
  padding: 11px 13px;
  background: rgba(7, 8, 12, 0.6);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--success);
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.87rem;
  line-height: 1.6;
  resize: vertical;
  margin-bottom: 10px;
  transition: border-color 0.16s ease, box-shadow 0.16s ease;
}

.command-edit::placeholder {
  color: var(--text-faint);
}

.command-edit:focus {
  outline: none;
  border-color: var(--accent-line);
  box-shadow: 0 0 0 3px var(--accent-soft);
}

.tok-base {
  color: var(--success);
  font-weight: 600;
}

.tok-flag {
  color: var(--warning);
}

.tok-target {
  color: var(--accent-2);
  font-weight: 600;
}

.tok-value {
  color: var(--text-muted);
}

.step-label {
  display: block;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.68rem;
  font-weight: 500;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--text-faint);
  margin-bottom: 9px;
}

.builder-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  margin-bottom: 18px;
}

.phase-buttons {
  display: flex;
  gap: 8px;
}

.phase-btn {
  padding: 7px 16px;
  border: 1px solid var(--border);
  background: var(--glass-1);
  color: var(--text-muted);
  border-radius: 999px;
  cursor: pointer;
  font-size: 0.83rem;
  transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
}

.phase-btn:hover {
  background: var(--glass-2);
  color: var(--text);
}

.phase-btn.active {
  background: var(--accent-soft);
  border-color: var(--accent-line);
  color: #fff;
  box-shadow: 0 0 16px rgba(124, 108, 245, 0.22);
}

.tool-search {
  min-width: 220px;
}

.address-input {
  width: 100%;
  padding: 10px 12px;
  background: var(--glass-1);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text);
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.87rem;
  transition: border-color 0.16s ease, box-shadow 0.16s ease, background 0.16s ease;
}

.address-input::placeholder {
  color: var(--text-faint);
  font-family: 'IBM Plex Sans', sans-serif;
}

.address-input:focus {
  outline: none;
  background: var(--glass-2);
  border-color: var(--accent-line);
  box-shadow: 0 0 0 3px var(--accent-soft);
}

.empty-hint {
  color: var(--text-muted);
  font-size: 0.86rem;
  margin-top: 8px;
}

.options-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.option-section-label {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.66rem;
  font-weight: 500;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--text-faint);
  margin: 0 0 9px;
}

.option-section-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.option-group {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
  padding: 7px 11px;
  background: var(--glass-1);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
}

.option-tag {
  font-size: 0.76rem;
  color: var(--text-muted);
}

.chip {
  padding: 6px 13px;
  border: 1px solid var(--border);
  background: var(--glass-2);
  color: var(--text-muted);
  border-radius: 999px;
  cursor: pointer;
  font-size: 0.8rem;
  font-family: 'IBM Plex Mono', monospace;
  transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
}

.chip:hover {
  background: var(--glass-3);
  border-color: var(--border-strong);
  color: var(--text);
}

.chip.active {
  background: var(--accent-soft);
  border-color: var(--accent-line);
  color: #fff;
  box-shadow: 0 0 16px rgba(124, 108, 245, 0.25);
}

.chip-input-wrap {
  position: relative;
  display: inline-flex;
}

.chip-input {
  padding: 6px 13px;
  background: var(--glass-1);
  border: 1px solid var(--border);
  border-radius: 999px;
  color: var(--text);
  font-size: 0.8rem;
  min-width: 160px;
  transition: border-color 0.16s ease, box-shadow 0.16s ease, background 0.16s ease;
}

.chip-input::placeholder {
  color: var(--text-faint);
}

.chip-input:focus {
  outline: none;
  background: var(--glass-2);
  border-color: var(--accent-line);
  box-shadow: 0 0 0 3px var(--accent-soft);
}

.catalog-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 5px;
  background: rgba(16, 18, 28, 0.96);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-sm);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  box-shadow: var(--shadow-3);
  min-width: 280px;
  max-height: 230px;
  overflow-y: auto;
  z-index: 20;
}

.catalog-item {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
  width: 100%;
  padding: 9px 13px;
  background: none;
  border: none;
  border-bottom: 1px solid var(--border);
  text-align: left;
  cursor: pointer;
  transition: background 0.14s ease;
}

.catalog-item:last-child {
  border-bottom: none;
}

.catalog-item:hover {
  background: var(--accent-soft);
}

.catalog-value {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.83rem;
  color: var(--accent-2);
  font-weight: 500;
}

.catalog-desc {
  font-size: 0.76rem;
  color: var(--text-muted);
}

.catalog-empty {
  padding: 10px 13px;
  font-size: 0.8rem;
  color: var(--text-faint);
  margin: 0;
}

.result {
  margin-top: 18px;
}

.sticky-result {
  position: sticky;
  top: 74px;
  z-index: 5;
  background: rgba(14, 16, 26, 0.86);
  border: 1px solid var(--border-strong);
  padding: 14px 15px;
  border-radius: var(--radius);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  box-shadow: var(--shadow-3);
}

.copy-btn {
  padding: 9px 18px;
  background: linear-gradient(135deg, var(--accent), #6355d6);
  color: #fff;
  border: 1px solid var(--accent-line);
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  box-shadow: 0 6px 22px rgba(124, 108, 245, 0.28);
  transition: filter 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease;
}

.copy-btn:hover:not(:disabled) {
  filter: brightness(1.12);
  box-shadow: 0 8px 30px rgba(124, 108, 245, 0.42);
  transform: translateY(-1px);
}

.copy-btn:disabled {
  background: var(--glass-2);
  border-color: var(--border);
  color: var(--text-faint);
  box-shadow: none;
  cursor: not-allowed;
}

@media (max-width: 640px) {
  .tabbed-area {
    flex-direction: column;
  }

  .tab-sidebar {
    flex-direction: row;
  }
}
</style>
