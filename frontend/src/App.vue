<script setup>
import { ref, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import Login from './components/Login.vue'
import Dashboard from './components/Dashboard.vue'
import TargetList from './components/TargetList.vue'
import ToolGenerator from './components/ToolGenerator.vue'
import Veille from './components/Veille.vue'
import Kanban from './components/Kanban.vue'
import Osint from './components/Osint.vue'
import SpaceBackground from './components/SpaceBackground.vue'
import { authToken, logout } from './auth'
import { apiFetch } from './api'
import { readStored, writeStored } from './storage'
import { ANIMATIONS, enabledAnimations } from './animations'

const VIEW_TITLES = {
  dashboard: 'Accueil',
  targets: 'Carnet de cibles',
  generator: 'Générateur de commandes',
  veille: 'Veille cybersécu & IA',
  kanban: 'Kanban projets',
  osint: 'OSINT automatique',
}

// La vue courante vit dans l'URL (#/veille...) : le bouton Precedent, les favoris
// et le rechargement de page se comportent comme sur n'importe quel site.
function viewFromHash() {
  const view = window.location.hash.replace(/^#\/?/, '')
  return view in VIEW_TITLES ? view : 'dashboard'
}

const currentView = ref(viewFromHash())
const mainEl = ref(null)

function setDocumentTitle(view) {
  document.title = `${VIEW_TITLES[view]} · Centre de contrôle`
}
setDocumentTitle(currentView.value)

function onHashChange() {
  currentView.value = viewFromHash()
}

watch(currentView, async (view) => {
  if (viewFromHash() !== view) window.location.hash = `/${view}`
  setDocumentTitle(view)
  // Place le focus sur le contenu : un lecteur d'ecran annonce la nouvelle page
  // au lieu de rester sur le lien du menu.
  await nextTick()
  mainEl.value?.focus({ preventScroll: true })
})

const sidebarVisible = ref(readStored('sidebarVisible') !== 'false')
watch(sidebarVisible, (value) => writeStored('sidebarVisible', value))

// Animations : desactivables a la main, en plus du reglage systeme
// prefers-reduced-motion. La classe est posee sur <html> pour couvrir aussi
// l'ecran de connexion.
const motionEnabled = ref(readStored('motion') !== 'off')
watch(
  motionEnabled,
  (enabled) => {
    document.documentElement.classList.toggle('motion-off', !enabled)
    writeStored('motion', enabled ? 'on' : 'off')
  },
  { immediate: true },
)

// Etat reel de l'API, verifie periodiquement. L'ancien « systeme en ligne »
// etait ecrit en dur et s'affichait meme serveur eteint.
const STATUS_LABELS = {
  checking: 'vérification…',
  online: 'API en ligne',
  offline: 'API injoignable',
}
const apiStatus = ref('checking')
let healthTimer = null

async function checkHealth() {
  try {
    const response = await apiFetch('/api/health/')
    apiStatus.value = response.ok ? 'online' : 'offline'
  } catch {
    apiStatus.value = 'offline'
  }
}

// Menu des animations : se ferme au clic a l'exterieur et avec Echap
const animMenuOpen = ref(false)
const animMenuEl = ref(null)

function closeAnimMenuOnOutsideClick(event) {
  if (animMenuOpen.value && animMenuEl.value && !animMenuEl.value.contains(event.target)) {
    animMenuOpen.value = false
  }
}

function closeAnimMenuOnEscape(event) {
  if (event.key === 'Escape') animMenuOpen.value = false
}

onMounted(() => {
  window.addEventListener('hashchange', onHashChange)
  document.addEventListener('click', closeAnimMenuOnOutsideClick)
  document.addEventListener('keydown', closeAnimMenuOnEscape)
  checkHealth()
  healthTimer = setInterval(checkHealth, 30000)
})

onBeforeUnmount(() => {
  window.removeEventListener('hashchange', onHashChange)
  document.removeEventListener('click', closeAnimMenuOnOutsideClick)
  document.removeEventListener('keydown', closeAnimMenuOnEscape)
  clearInterval(healthTimer)
})
</script>

<template>
  <Login v-if="!authToken" />

  <div v-else class="app-shell">
    <aside id="sidebar" :class="['sidebar', { collapsed: !sidebarVisible }]" aria-label="Modules">
      <div class="sidebar-brand">
        <img class="sidebar-logo" src="/logo.png" alt="" />
        <span class="sidebar-label">Centre de contrôle</span>
      </div>

      <p class="sidebar-section-label sidebar-label">Modules</p>

      <nav class="sidebar-nav">
        <a
          href="#/dashboard"
          :class="['sidebar-link', { active: currentView === 'dashboard' }]"
          :aria-current="currentView === 'dashboard' ? 'page' : null"
          :title="!sidebarVisible ? 'Accueil' : null"
        >
          <svg aria-hidden="true" focusable="false" class="sidebar-link-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 11L12 4L21 11" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
            <path d="M5 10V19A1 1 0 0 0 6 20H18A1 1 0 0 0 19 19V10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
          <span class="sidebar-label">Accueil</span>
        </a>
        <a
          href="#/targets"
          :class="['sidebar-link', { active: currentView === 'targets' }]"
          :aria-current="currentView === 'targets' ? 'page' : null"
          :title="!sidebarVisible ? 'Carnet de cibles' : null"
        >
          <svg aria-hidden="true" focusable="false" class="sidebar-link-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2" />
            <circle cx="12" cy="12" r="5" stroke="currentColor" stroke-width="2" />
            <circle cx="12" cy="12" r="1.5" fill="currentColor" />
          </svg>
          <span class="sidebar-label">Carnet de cibles</span>
        </a>
        <a
          href="#/generator"
          :class="['sidebar-link', { active: currentView === 'generator' }]"
          :aria-current="currentView === 'generator' ? 'page' : null"
          :title="!sidebarVisible ? 'Générateur de commandes' : null"
        >
          <svg aria-hidden="true" focusable="false" class="sidebar-link-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="2" y="4" width="20" height="16" rx="2" stroke="currentColor" stroke-width="2" />
            <path d="M6 9L10 12L6 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
            <line x1="12" y1="15" x2="17" y2="15" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
          </svg>
          <span class="sidebar-label">Générateur de commandes</span>
        </a>
        <a
          href="#/veille"
          :class="['sidebar-link', { active: currentView === 'veille' }]"
          :aria-current="currentView === 'veille' ? 'page' : null"
          :title="!sidebarVisible ? 'Veille cybersécu & IA' : null"
        >
          <svg aria-hidden="true" focusable="false" class="sidebar-link-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="3" y="4" width="18" height="16" rx="1" stroke="currentColor" stroke-width="2" />
            <line x1="3" y1="9" x2="21" y2="9" stroke="currentColor" stroke-width="2" />
            <line x1="7" y1="13" x2="15" y2="13" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
            <line x1="7" y1="17" x2="12" y2="17" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
          </svg>
          <span class="sidebar-label">Veille cybersécu &amp; IA</span>
        </a>
        <a
          href="#/kanban"
          :class="['sidebar-link', { active: currentView === 'kanban' }]"
          :aria-current="currentView === 'kanban' ? 'page' : null"
          :title="!sidebarVisible ? 'Kanban projets' : null"
        >
          <svg aria-hidden="true" focusable="false" class="sidebar-link-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="3" y="4" width="18" height="16" rx="1" stroke="currentColor" stroke-width="2" />
            <line x1="9" y1="4" x2="9" y2="20" stroke="currentColor" stroke-width="2" />
            <line x1="15" y1="4" x2="15" y2="20" stroke="currentColor" stroke-width="2" />
          </svg>
          <span class="sidebar-label">Kanban projets</span>
        </a>
        <a
          href="#/osint"
          :class="['sidebar-link', { active: currentView === 'osint' }]"
          :aria-current="currentView === 'osint' ? 'page' : null"
          :title="!sidebarVisible ? 'OSINT automatique' : null"
        >
          <svg aria-hidden="true" focusable="false" class="sidebar-link-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="2" />
            <line x1="16.5" y1="16.5" x2="21" y2="21" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
          </svg>
          <span class="sidebar-label">OSINT automatique</span>
        </a>
      </nav>

      <div class="sidebar-doodle">
        <svg aria-hidden="true" focusable="false" width="104" height="104" viewBox="0 0 64 64" shape-rendering="crispEdges" xmlns="http://www.w3.org/2000/svg">
          <!-- mer -->
          <rect x="30" y="44" width="34" height="20" fill="#2c4f8a" />
          <rect x="30" y="44" width="34" height="3" fill="#4f86d6" />

          <!-- ponton -->
          <rect x="0" y="42" width="4" height="6" fill="#b1701f" />
          <rect x="4" y="42" width="4" height="6" fill="#7a4d22" />
          <rect x="8" y="42" width="4" height="6" fill="#b1701f" />
          <rect x="12" y="42" width="4" height="6" fill="#7a4d22" />
          <rect x="16" y="42" width="4" height="6" fill="#b1701f" />
          <rect x="20" y="42" width="4" height="6" fill="#7a4d22" />
          <rect x="24" y="42" width="4" height="6" fill="#b1701f" />
          <rect x="28" y="42" width="4" height="6" fill="#7a4d22" />
          <rect x="2" y="48" width="4" height="10" fill="#5c3a1e" />
          <rect x="24" y="48" width="4" height="10" fill="#5c3a1e" />

          <!-- personnage assis, profil face à la mer -->
          <g class="doodle-figure">
            <!-- casquette -->
            <rect x="14" y="16" width="12" height="4" fill="#6355d6" />
            <rect x="14" y="20" width="12" height="2" fill="#6355d6" />
            <rect x="26" y="20" width="6" height="2" fill="#4a3fae" />
            <!-- visage -->
            <rect x="16" y="22" width="12" height="6" fill="#d9a877" />
            <rect x="24" y="24" width="2" height="2" fill="#20233a" />
            <rect x="28" y="24" width="2" height="2" fill="#d9a877" />
            <!-- veste -->
            <rect x="14" y="28" width="14" height="10" fill="#4f6640" />
            <rect x="14" y="28" width="14" height="2" fill="#5e7a4d" />
            <!-- jambes qui pendent au bord -->
            <rect x="16" y="38" width="14" height="2" fill="#20233a" />
            <rect x="20" y="40" width="4" height="10" fill="#20233a" />
            <rect x="26" y="40" width="4" height="10" fill="#20233a" />
            <rect x="19" y="50" width="6" height="3" fill="#14162a" />
            <rect x="25" y="50" width="6" height="3" fill="#14162a" />
          </g>

          <!-- bras + canne (balance et pique) -->
          <g class="doodle-rod">
            <rect x="26" y="30" width="4" height="3" fill="#4f6640" />
            <rect x="29" y="32" width="4" height="3" fill="#4f6640" />
            <rect x="32" y="33" width="3" height="3" fill="#d9a877" />
            <rect x="35" y="31" width="4" height="3" fill="#7a4d2e" />
            <rect x="39" y="28" width="4" height="3" fill="#7a4d2e" />
            <rect x="43" y="25" width="4" height="3" fill="#7a4d2e" />
            <rect x="47" y="22" width="4" height="3" fill="#8f5e38" />
          </g>

          <!-- ligne -->
          <rect class="doodle-line" x="49" y="25" width="1" height="20" fill="#c3ccdb" />

          <!-- flotteur -->
          <g class="doodle-bobber">
            <rect x="48" y="43" width="3" height="2" fill="#dcdee4" />
            <rect x="48" y="45" width="3" height="2" fill="#c9524e" />
          </g>

          <!-- ondes autour du flotteur -->
          <rect class="doodle-ring doodle-ring-l" x="43" y="47" width="3" height="1" fill="#cfe0ff" />
          <rect class="doodle-ring doodle-ring-r" x="53" y="47" width="3" height="1" fill="#cfe0ff" />

          <!-- vaguelettes -->
          <g class="doodle-water" fill="#cfe0ff">
            <rect x="33" y="53" width="5" height="1" />
            <rect x="57" y="51" width="5" height="1" />
            <rect x="40" y="59" width="5" height="1" />
          </g>
        </svg>
      </div>

      <button class="sidebar-logout" :title="!sidebarVisible ? 'Se déconnecter' : null" @click="logout">
        <svg aria-hidden="true" focusable="false" class="sidebar-logout-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
          <path d="M16 17L21 12L16 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
          <line x1="21" y1="12" x2="9" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
        </svg>
        <span class="sidebar-label">Se déconnecter</span>
      </button>
    </aside>

    <div class="main-area">
      <SpaceBackground />

      <div class="main-topbar">
        <button
          type="button"
          class="sidebar-toggle"
          :title="sidebarVisible ? 'Masquer le menu' : 'Afficher le menu'"
          :aria-label="sidebarVisible ? 'Masquer le menu' : 'Afficher le menu'"
          :aria-expanded="sidebarVisible"
          aria-controls="sidebar"
          @click="sidebarVisible = !sidebarVisible"
        >
          <svg aria-hidden="true" focusable="false" width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <line x1="3" y1="6" x2="21" y2="6" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
            <line x1="3" y1="12" x2="21" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
            <line x1="3" y1="18" x2="21" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
          </svg>
        </button>
        <span class="topbar-status" role="status" aria-live="polite">
          <span :class="['topbar-dot', `topbar-dot-${apiStatus}`]"></span>
          <span class="topbar-status-text">{{ STATUS_LABELS[apiStatus] }}</span>
        </span>
        <div ref="animMenuEl" class="anim-menu">
          <!-- Le libelle dit l'etat actuel : avec un texte fixe, rien n'indiquait
               que les animations (et les vaisseaux) etaient coupees -->
          <button
            type="button"
            class="topbar-motion"
            :aria-expanded="animMenuOpen"
            aria-controls="anim-panel"
            @click="animMenuOpen = !animMenuOpen"
          >
            {{ motionEnabled ? 'Animations : activées' : 'Animations : coupées' }}
            <span aria-hidden="true">▾</span>
          </button>
          <div v-if="animMenuOpen" id="anim-panel" class="anim-panel" role="group" aria-label="Choix des animations">
            <label class="anim-option anim-option-master">
              <input v-model="motionEnabled" type="checkbox" />
              Toutes les animations
            </label>
            <p class="anim-panel-title">Créatures du fond</p>
            <label v-for="animation in ANIMATIONS" :key="animation.key" class="anim-option">
              <input
                v-model="enabledAnimations[animation.key]"
                type="checkbox"
                :disabled="!motionEnabled"
              />
              {{ animation.label }}
            </label>
          </div>
        </div>
      </div>
      <main ref="mainEl" tabindex="-1">
        <Dashboard v-if="currentView === 'dashboard'" @navigate="currentView = $event" />
        <TargetList v-else-if="currentView === 'targets'" />
        <ToolGenerator v-else-if="currentView === 'generator'" />
        <Veille v-else-if="currentView === 'veille'" />
        <Kanban v-else-if="currentView === 'kanban'" />
        <Osint v-else-if="currentView === 'osint'" />
      </main>
      <footer class="app-footer">Centre de contrôle — usage local</footer>
    </div>
  </div>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: flex;
  background: var(--bg-base);
}

/* ---------- sidebar ---------- */
.sidebar {
  width: 268px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  padding: 20px 12px;
  margin: 10px 0 10px 10px;
  background: linear-gradient(170deg, rgba(255, 255, 255, 0.06) 0%, rgba(255, 255, 255, 0.022) 45%, rgba(255, 255, 255, 0.012) 100%);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  box-shadow: var(--shadow-3);
  z-index: 2;
  overflow: hidden;
  transition: width 0.24s cubic-bezier(0.4, 0, 0.2, 1), padding 0.24s ease;
  position: sticky;
  top: 10px;
  align-self: flex-start;
  height: calc(100vh - 20px);
}

/* liseré lumineux sur l'arête gauche */
.sidebar::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  padding: 1px;
  background: linear-gradient(170deg, rgba(124, 108, 245, 0.45), rgba(255, 255, 255, 0) 38%);
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}

.sidebar.collapsed {
  width: 68px;
  padding-inline: 10px;
}

.sidebar.collapsed .sidebar-label {
  opacity: 0;
  width: 0;
  overflow: hidden;
  white-space: nowrap;
}

.sidebar.collapsed .sidebar-section-label {
  height: 0;
  padding: 8px 0 0;
}

.sidebar.collapsed .sidebar-doodle {
  opacity: 0;
  pointer-events: none;
}

.sidebar.collapsed .sidebar-brand,
.sidebar.collapsed .sidebar-link,
.sidebar.collapsed .sidebar-logout {
  justify-content: center;
  padding-inline: 0;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
  overflow: hidden;
  color: var(--text);
  font-weight: 600;
  font-size: var(--fs-md);
  letter-spacing: -0.01em;
  padding: 4px 10px 20px;
  border-bottom: 1px solid var(--border);
}

.sidebar-logo {
  width: 36px;
  height: 36px;
  object-fit: contain;
  flex-shrink: 0;
  /* l'embleme est circulaire : le halo suit le cercle, un cadre carre laisserait
     voir ses coins vides */
  border-radius: 50%;
  box-shadow: 0 2px 14px rgba(124, 108, 245, 0.3);
}

/* garde-fou : un libellé long est tronqué au lieu de déborder du panneau */
.sidebar-label {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  transition: opacity 0.18s ease;
}

.sidebar-section-label {
  font-family: 'IBM Plex Mono', monospace;
  font-size: var(--fs-xs);
  font-weight: 500;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--text-faint);
  padding: 20px 12px 10px;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.sidebar-link {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: none;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: var(--fs-base);
  color: var(--text-muted);
  text-align: left;
  text-decoration: none;
  min-width: 0;
  overflow: hidden;
  transition: background 0.16s ease, color 0.16s ease;
}

.sidebar-link-icon {
  flex-shrink: 0;
  color: var(--text-faint);
  transition: color 0.16s ease;
}

.sidebar-link:hover {
  background: var(--glass-2);
  color: var(--text);
}

.sidebar-link:hover .sidebar-link-icon {
  color: var(--text-muted);
}

.sidebar-link.active {
  background: linear-gradient(90deg, var(--accent-soft), rgba(124, 108, 245, 0.04));
  color: #fff;
  font-weight: 500;
  box-shadow: inset 0 0 0 1px var(--accent-line);
}

.sidebar-link.active .sidebar-link-icon {
  color: var(--accent-text);
  filter: drop-shadow(0 0 6px rgba(124, 108, 245, 0.7));
}

.sidebar-doodle {
  display: flex;
  justify-content: center;
  padding-top: 10px;
  opacity: 0.85;
  transition: opacity 0.2s ease;
}

.doodle-figure {
  transform-box: fill-box;
  transform-origin: bottom center;
  animation: doodle-bob 3.6s ease-in-out infinite;
}

.doodle-rod {
  transform-box: fill-box;
  transform-origin: 12% 90%;
  animation: doodle-cast 3.6s ease-in-out infinite;
}

.doodle-bobber {
  transform-box: fill-box;
  transform-origin: center;
  animation: doodle-dip 3.6s ease-in-out infinite;
}

.doodle-line {
  transform-box: fill-box;
  transform-origin: top center;
  animation: doodle-line 3.6s ease-in-out infinite;
}

.doodle-ring {
  transform-box: fill-box;
  transform-origin: center;
  opacity: 0;
}

.doodle-ring-l {
  animation: doodle-ring-l 3.6s ease-out infinite;
}

.doodle-ring-r {
  animation: doodle-ring-r 3.6s ease-out infinite;
}

.doodle-water rect:nth-child(odd) {
  animation: doodle-ripple 1.8s steps(1, jump-none) infinite;
}

.doodle-water rect:nth-child(even) {
  animation: doodle-ripple 1.8s steps(1, jump-none) infinite reverse;
}

@keyframes doodle-cast {
  0%, 55% { transform: rotate(0deg); }
  40% { transform: rotate(-2deg); }
  65% { transform: rotate(7deg); }
  72% { transform: rotate(-5deg); }
  82% { transform: rotate(2deg); }
  100% { transform: rotate(0deg); }
}

@keyframes doodle-dip {
  0%, 45% { transform: translateY(0); }
  25% { transform: translateY(1px); }
  60% { transform: translateY(1px); }
  66% { transform: translateY(5px); }
  78% { transform: translateY(0); }
  100% { transform: translateY(0); }
}

@keyframes doodle-line {
  0%, 60% { transform: scaleY(1); }
  66% { transform: scaleY(1.22); }
  78% { transform: scaleY(1); }
  100% { transform: scaleY(1); }
}

@keyframes doodle-ring-l {
  0%, 63% { opacity: 0; transform: translateX(0); }
  70% { opacity: 1; }
  100% { opacity: 0; transform: translateX(-4px); }
}

@keyframes doodle-ring-r {
  0%, 63% { opacity: 0; transform: translateX(0); }
  70% { opacity: 1; }
  100% { opacity: 0; transform: translateX(4px); }
}

@keyframes doodle-ripple {
  0%, 49% { opacity: 1; }
  50%, 100% { opacity: 0.3; }
}

@keyframes doodle-bob {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-1px); }
}

.sidebar-logout {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 12px;
  padding: 12px 12px 6px;
  background: none;
  border: none;
  border-top: 1px solid var(--border);
  border-radius: 0;
  cursor: pointer;
  font-size: var(--fs-sm);
  color: var(--text-faint);
  text-align: left;
  min-width: 0;
  overflow: hidden;
  transition: color 0.16s ease;
}

.sidebar-logout-icon {
  flex-shrink: 0;
}

.sidebar-logout:hover {
  color: var(--danger);
}

/* ---------- zone principale ---------- */
.main-area {
  position: relative;
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

/* ---------- topbar ---------- */
.main-topbar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 32px;
  position: sticky;
  top: 0;
  z-index: 10;
  background: rgba(5, 5, 7, 0.72);
  border-bottom: 1px solid var(--border);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
}

.sidebar-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  background: var(--glass-1);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  cursor: pointer;
  transition: border-color 0.16s ease, color 0.16s ease, background 0.16s ease;
}

.sidebar-toggle:hover {
  background: var(--glass-2);
  border-color: var(--border-strong);
  color: var(--text);
}

.topbar-status {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: 'IBM Plex Mono', monospace;
  font-size: var(--fs-xs);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--text-faint);
}

.topbar-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--text-faint);
}

/* Seul l'etat « en ligne » pulse : une panne doit se lire d'un coup d'oeil, pas
   ressembler a l'etat normal */
.topbar-dot-online {
  background: var(--success);
  box-shadow: 0 0 8px var(--success);
  animation: pulse-dot 2.4s ease-in-out infinite;
}

.topbar-dot-offline {
  background: var(--danger);
  box-shadow: 0 0 8px var(--danger);
}

.anim-menu {
  position: relative;
  margin-left: auto;
}

.topbar-motion {
  padding: 6px 12px;
  background: var(--glass-1);
  border: 1px solid var(--border);
  border-radius: 999px;
  color: var(--text-muted);
  font-size: var(--fs-xs);
  cursor: pointer;
  transition: background 0.16s ease, border-color 0.16s ease, color 0.16s ease;
}

.topbar-motion:hover {
  background: var(--glass-2);
  color: var(--text);
}

.topbar-motion[aria-expanded='true'] {
  background: var(--accent-soft);
  border-color: var(--accent-line);
  color: var(--text);
}

.anim-panel {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  z-index: 20;
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 220px;
  padding: 10px;
  background: #10121c;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius);
  box-shadow: var(--shadow-3);
}

.anim-panel-title {
  margin: 8px 8px 4px;
  font-family: 'IBM Plex Mono', monospace;
  font-size: var(--fs-xs);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--text-faint);
}

/* toute la ligne est cliquable, pas seulement la petite case */
.anim-option {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 32px;
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  font-size: var(--fs-sm);
  color: var(--text);
  cursor: pointer;
}

.anim-option:hover {
  background: var(--glass-2);
}

.anim-option input {
  width: 16px;
  height: 16px;
  accent-color: var(--accent);
  cursor: pointer;
}

.anim-option:has(input:disabled) {
  color: var(--text-faint);
  cursor: not-allowed;
}

.anim-option-master {
  font-weight: 600;
  border-bottom: 1px solid var(--border);
  border-radius: var(--radius-sm) var(--radius-sm) 0 0;
  padding-bottom: 8px;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.35; }
}

main {
  position: relative;
  z-index: 1;
  flex: 1;
  padding: 32px 32px;
}

/* main ne recoit le focus que par programme, pour annoncer le changement de page :
   ce n'est pas un element interactif, un contour autour de toute la page
   n'aiderait personne. */
main:focus {
  outline: none;
}

.app-footer {
  position: relative;
  z-index: 1;
  padding: 20px 32px 32px;
  text-align: center;
  color: var(--text-faint);
  font-size: var(--fs-xs);
}

@media (max-width: 640px) {
  .app-shell {
    flex-direction: column;
  }

  .sidebar,
  .sidebar.collapsed {
    width: auto;
    height: auto;
    position: static;
    flex-direction: row;
    align-items: center;
    padding: 10px 16px;
    margin: 8px;
  }

  .sidebar-brand {
    padding: 0 12px 0 0;
    border-bottom: none;
    border-right: 1px solid var(--border);
  }

  .sidebar-section-label,
  .sidebar-doodle {
    display: none;
  }

  .sidebar-nav {
    flex-direction: row;
    overflow-x: auto;
  }

  .sidebar-logout {
    margin-top: 0;
    margin-left: auto;
    padding: 6px 10px;
    border-top: none;
  }

  main {
    padding: 24px 16px;
  }

  /* Masque a l'ecran mais reste lu : display:none retirerait aussi l'etat aux
     lecteurs d'ecran, et le point de couleur seul ne dit rien */
  .topbar-status-text {
    position: absolute;
    width: 1px;
    height: 1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
  }
}
</style>
