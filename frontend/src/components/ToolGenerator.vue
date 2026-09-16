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
}

function categoryClass(category) {
  return CATEGORY_CLASSES[category] || 'badge-default'
}

// Liste des catégories présentes dans les suggestions, dans un ordre fixe et lisible
const CATEGORY_ORDER = ['Général', 'DNS / OSINT', 'SMB', 'FTP', 'SSH', 'HTTP', 'SMTP', 'SQL', 'Metasploit']

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
  padding: 12px 16px;
  border: 1px solid #d7e0de;
  background: #fff;
  border-radius: 10px;
  cursor: pointer;
  text-align: left;
  transition: border-color 0.15s ease, background 0.15s ease, box-shadow 0.15s ease;
}

.tab-btn:hover {
  border-color: #0f6d63;
}

.tab-btn-label {
  font-size: 0.92rem;
  font-weight: 600;
  color: #14201e;
}

.tab-btn-sub {
  font-size: 0.75rem;
  color: #8a9895;
}

.tab-btn.active {
  background: #0f6d63;
  border-color: #0f6d63;
  box-shadow: 0 4px 12px rgba(15, 109, 99, 0.25);
}

.tab-btn.active .tab-btn-label {
  color: #fff;
}

.tab-btn.active .tab-btn-sub {
  color: #cfe8e3;
}

.tab-content {
  flex: 1;
  min-width: 0;
}

.quick-section,
.builder-section {
  background: #fff;
  border: 1px solid #d7e0de;
  border-radius: 12px;
  padding: 18px 20px;
  box-shadow: 0 1px 2px rgba(20, 32, 30, 0.05), 0 6px 18px rgba(20, 32, 30, 0.05);
}

.category-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
}

.filter-btn {
  padding: 5px 12px;
  border: 1px solid #c3d0cd;
  background: #fff;
  color: #5b6b68;
  border-radius: 999px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
}

.filter-btn.active {
  background: #0f6d63;
  border-color: #0f6d63;
  color: #fff;
}

.sub-filters {
  margin: -4px 0 12px 4px;
}

.filter-btn-sub {
  padding: 3px 10px;
  font-size: 0.74rem;
  border-color: #e5eaea;
  color: #8a9895;
}

.filter-btn-sub.active {
  background: #3d3d8f;
  border-color: #3d3d8f;
}

.preset-grid-wrap {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #d7e0de;
  border-radius: 10px;
  padding: 12px;
  background: #f6f9f8;
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
  gap: 5px;
  text-align: left;
  padding: 12px 14px;
  border: 1px solid #d7e0de;
  background: #fff;
  border-radius: 10px;
  cursor: pointer;
  transition: border-color 0.15s ease, background 0.15s ease, box-shadow 0.15s ease;
}

.preset-card:hover {
  border-color: #0f6d63;
  background: #f6f9f8;
  box-shadow: 0 2px 8px rgba(20, 32, 30, 0.06);
}

.preset-badge {
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  padding: 2px 8px;
  border-radius: 999px;
  background: #eef2f1;
  color: #5b6b68;
}

.badge-smb {
  background: #e5eff5;
  color: #2b6a8f;
}

.badge-ftp {
  background: #f6ece0;
  color: #a85a17;
}

.badge-ssh {
  background: #eef2f1;
  color: #0f6d63;
}

.badge-http {
  background: #f3e8f5;
  color: #7a3d8f;
}

.badge-smtp {
  background: #fdecec;
  color: #b3413a;
}

.badge-sql {
  background: #eef2e0;
  color: #5f7a1f;
}

.badge-general,
.badge-default {
  background: #eef2f1;
  color: #5b6b68;
}

.badge-dns {
  background: #e6f0e9;
  color: #2f7d54;
}

.badge-metasploit {
  background: #e6e6f7;
  color: #3d3d8f;
}

.preset-label {
  font-weight: 600;
  font-size: 0.9rem;
  color: #14201e;
}

.preset-preview {
  font-family: monospace;
  font-size: 0.78rem;
  color: #5b6b68;
  word-break: break-all;
}

.command-edit {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #c3d0cd;
  border-radius: 8px;
  font-family: monospace;
  font-size: 0.88rem;
  box-sizing: border-box;
  resize: vertical;
  margin-bottom: 10px;
}

.tok-base {
  color: #0f6d63;
  font-weight: 700;
}

.tok-flag {
  color: #a85a17;
}

.tok-target {
  color: #2b6a8f;
  font-weight: 700;
}

.tok-value {
  color: #5b6b68;
}

.step-label {
  display: block;
  font-weight: 600;
  color: #14201e;
  margin-bottom: 10px;
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
  border: 1px solid #c3d0cd;
  background: #fff;
  border-radius: 999px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
}

.phase-btn.active {
  background: #0f6d63;
  border-color: #0f6d63;
  color: #fff;
}

.tool-search {
  min-width: 220px;
}

.address-input {
  width: 100%;
  padding: 9px 11px;
  border: 1px solid #c3d0cd;
  border-radius: 8px;
  font-size: 0.9rem;
  box-sizing: border-box;
}

.empty-hint {
  color: #5b6b68;
  font-size: 0.88rem;
  margin-top: 8px;
}

.options-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.option-section-label {
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: #8a9895;
  margin: 0 0 8px;
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
  padding: 6px 10px;
  background: #f6f9f8;
  border: 1px solid #e5eaea;
  border-radius: 10px;
}

.option-tag {
  font-size: 0.78rem;
  color: #5b6b68;
}

.chip {
  padding: 6px 13px;
  border: 1px solid #c3d0cd;
  background: #fff;
  color: #14201e;
  border-radius: 999px;
  cursor: pointer;
  font-size: 0.82rem;
  font-family: monospace;
  transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
}

.chip:hover {
  border-color: #0f6d63;
}

.chip.active {
  background: #0f6d63;
  border-color: #0f6d63;
  color: #fff;
}

.chip-input-wrap {
  position: relative;
  display: inline-flex;
}

.chip-input {
  padding: 6px 12px;
  border: 1px solid #c3d0cd;
  border-radius: 999px;
  font-size: 0.82rem;
  min-width: 160px;
}

.catalog-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 4px;
  background: #fff;
  border: 1px solid #d7e0de;
  border-radius: 8px;
  box-shadow: 0 6px 16px rgba(20, 32, 30, 0.12);
  min-width: 280px;
  max-height: 220px;
  overflow-y: auto;
  z-index: 20;
}

.catalog-item {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
  width: 100%;
  padding: 8px 12px;
  background: none;
  border: none;
  border-bottom: 1px solid #eef2f1;
  text-align: left;
  cursor: pointer;
}

.catalog-item:last-child {
  border-bottom: none;
}

.catalog-item:hover {
  background: #f6f9f8;
}

.catalog-value {
  font-family: monospace;
  font-size: 0.85rem;
  color: #0f6d63;
  font-weight: 600;
}

.catalog-desc {
  font-size: 0.78rem;
  color: #5b6b68;
}

.catalog-empty {
  padding: 10px 12px;
  font-size: 0.82rem;
  color: #5b6b68;
  margin: 0;
}

.result {
  margin-top: 18px;
}

.sticky-result {
  position: sticky;
  top: 12px;
  z-index: 5;
  background: #fff;
  padding: 10px;
  border-radius: 10px;
  box-shadow: 0 1px 2px rgba(20, 32, 30, 0.06), 0 8px 22px rgba(20, 32, 30, 0.1);
}

.copy-btn {
  padding: 8px 16px;
  background: #0f6d63;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}

.copy-btn:hover {
  background: #0a4f48;
}

.copy-btn:disabled {
  background: #b6c4c1;
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
