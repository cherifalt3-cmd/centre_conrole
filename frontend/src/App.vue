<script setup>
import { ref, watch } from 'vue'
import Login from './components/Login.vue'
import Dashboard from './components/Dashboard.vue'
import TargetList from './components/TargetList.vue'
import ToolGenerator from './components/ToolGenerator.vue'
import Veille from './components/Veille.vue'
import Kanban from './components/Kanban.vue'
import Osint from './components/Osint.vue'
import { authToken, logout } from './auth'

const currentView = ref('dashboard')

let storedVisible = true
try {
  const stored = localStorage.getItem('sidebarVisible')
  storedVisible = stored === null ? true : stored === 'true'
} catch (e) {
  storedVisible = true
}
const sidebarVisible = ref(storedVisible)

watch(sidebarVisible, (value) => {
  try {
    localStorage.setItem('sidebarVisible', value)
  } catch (e) {
    // localStorage indisponible (navigation privée...) - pas grave, juste pas de mémorisation
  }
})
</script>

<template>
  <Login v-if="!authToken" />

  <div v-else class="app-shell">
    <aside :class="['sidebar', { collapsed: !sidebarVisible }]">
      <div class="sidebar-brand">
        <img class="sidebar-logo" src="/logo.png" alt="" />
        <span class="sidebar-label">Centre de contrôle</span>
      </div>

      <p class="sidebar-section-label sidebar-label">Modules</p>

      <nav class="sidebar-nav">
        <button
          type="button"
          :class="['sidebar-link', { active: currentView === 'dashboard' }]"
          :title="!sidebarVisible ? 'Accueil' : null"
          @click="currentView = 'dashboard'"
        >
          <svg class="sidebar-link-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 11L12 4L21 11" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
            <path d="M5 10V19A1 1 0 0 0 6 20H18A1 1 0 0 0 19 19V10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
          <span class="sidebar-label">Accueil</span>
        </button>
        <button
          type="button"
          :class="['sidebar-link', { active: currentView === 'targets' }]"
          :title="!sidebarVisible ? 'Carnet de cibles' : null"
          @click="currentView = 'targets'"
        >
          <svg class="sidebar-link-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2" />
            <circle cx="12" cy="12" r="5" stroke="currentColor" stroke-width="2" />
            <circle cx="12" cy="12" r="1.5" fill="currentColor" />
          </svg>
          <span class="sidebar-label">Carnet de cibles</span>
        </button>
        <button
          type="button"
          :class="['sidebar-link', { active: currentView === 'generator' }]"
          :title="!sidebarVisible ? 'Générateur de commandes' : null"
          @click="currentView = 'generator'"
        >
          <svg class="sidebar-link-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="2" y="4" width="20" height="16" rx="2" stroke="currentColor" stroke-width="2" />
            <path d="M6 9L10 12L6 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
            <line x1="12" y1="15" x2="17" y2="15" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
          </svg>
          <span class="sidebar-label">Générateur de commandes</span>
        </button>
        <button
          type="button"
          :class="['sidebar-link', { active: currentView === 'veille' }]"
          :title="!sidebarVisible ? 'Veille cybersécu & IA' : null"
          @click="currentView = 'veille'"
        >
          <svg class="sidebar-link-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="3" y="4" width="18" height="16" rx="1" stroke="currentColor" stroke-width="2" />
            <line x1="3" y1="9" x2="21" y2="9" stroke="currentColor" stroke-width="2" />
            <line x1="7" y1="13" x2="15" y2="13" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
            <line x1="7" y1="17" x2="12" y2="17" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
          </svg>
          <span class="sidebar-label">Veille cybersécu &amp; IA</span>
        </button>
        <button
          type="button"
          :class="['sidebar-link', { active: currentView === 'kanban' }]"
          :title="!sidebarVisible ? 'Kanban projets' : null"
          @click="currentView = 'kanban'"
        >
          <svg class="sidebar-link-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="3" y="4" width="18" height="16" rx="1" stroke="currentColor" stroke-width="2" />
            <line x1="9" y1="4" x2="9" y2="20" stroke="currentColor" stroke-width="2" />
            <line x1="15" y1="4" x2="15" y2="20" stroke="currentColor" stroke-width="2" />
          </svg>
          <span class="sidebar-label">Kanban projets</span>
        </button>
        <button
          type="button"
          :class="['sidebar-link', { active: currentView === 'osint' }]"
          :title="!sidebarVisible ? 'OSINT automatique' : null"
          @click="currentView = 'osint'"
        >
          <svg class="sidebar-link-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="2" />
            <line x1="16.5" y1="16.5" x2="21" y2="21" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
          </svg>
          <span class="sidebar-label">OSINT automatique</span>
        </button>
      </nav>

      <div class="sidebar-doodle">
        <svg width="104" height="104" viewBox="0 0 64 64" shape-rendering="crispEdges" xmlns="http://www.w3.org/2000/svg">
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
        <svg class="sidebar-logout-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
          <path d="M16 17L21 12L16 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
          <line x1="21" y1="12" x2="9" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
        </svg>
        <span class="sidebar-label">Se déconnecter</span>
      </button>
    </aside>

    <div class="main-area">
      <!-- décor spatial sombre -->
      <div class="space-bg">
        <div class="sky-nebula sky-nebula-a"></div>
        <div class="sky-nebula sky-nebula-b"></div>
        <div class="sky-grid"></div>
        <div class="sky-stars sky-stars-1"></div>
        <div class="sky-stars sky-stars-2"></div>
        <div class="sky-shooting"></div>
        <div class="sky-system">
          <div class="sky-sun"></div>
          <div class="sky-orbit sky-orbit-1"><span class="sky-planet sky-planet-1"></span></div>
          <div class="sky-orbit sky-orbit-2"><span class="sky-planet sky-planet-2"></span></div>
          <div class="sky-orbit sky-orbit-3"><span class="sky-planet sky-planet-3"></span></div>
        </div>
        <div class="sky-vignette"></div>
      </div>

      <div class="main-topbar">
        <button
          type="button"
          class="sidebar-toggle"
          :title="sidebarVisible ? 'Masquer le menu' : 'Afficher le menu'"
          @click="sidebarVisible = !sidebarVisible"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <line x1="3" y1="6" x2="21" y2="6" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
            <line x1="3" y1="12" x2="21" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
            <line x1="3" y1="18" x2="21" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
          </svg>
        </button>
        <span class="topbar-status">
          <span class="topbar-dot"></span>
          <span class="topbar-status-text">système en ligne</span>
        </span>
      </div>
      <main>
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
  font-size: 0.95rem;
  letter-spacing: -0.01em;
  padding: 4px 10px 18px;
  border-bottom: 1px solid var(--border);
}

.sidebar-logo {
  width: 34px;
  height: 34px;
  object-fit: contain;
  flex-shrink: 0;
  border-radius: 9px;
  box-shadow: 0 0 0 1px var(--border), 0 4px 18px rgba(124, 108, 245, 0.25);
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
  font-size: 0.63rem;
  font-weight: 500;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--text-faint);
  padding: 20px 12px 10px;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 3px;
  flex: 1;
}

.sidebar-link {
  position: relative;
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 9px 12px;
  background: none;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 0.86rem;
  color: var(--text-muted);
  text-align: left;
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
  color: var(--accent);
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
  gap: 11px;
  margin-top: 12px;
  padding: 13px 12px 6px;
  background: none;
  border: none;
  border-top: 1px solid var(--border);
  border-radius: 0;
  cursor: pointer;
  font-size: 0.8rem;
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

.space-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  background:
    radial-gradient(ellipse 80% 60% at 70% -10%, #171a2e 0%, transparent 60%),
    radial-gradient(ellipse 70% 50% at 10% 110%, #141b2c 0%, transparent 60%),
    var(--bg-base);
  overflow: hidden;
  pointer-events: none;
}

.sky-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.022) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.022) 1px, transparent 1px);
  background-size: 64px 64px;
  mask-image: radial-gradient(ellipse 100% 80% at 50% 0%, #000 0%, transparent 75%);
  -webkit-mask-image: radial-gradient(ellipse 100% 80% at 50% 0%, #000 0%, transparent 75%);
}

.sky-vignette {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse 120% 90% at 50% 40%, transparent 40%, rgba(5, 6, 10, 0.75) 100%);
}

.sky-nebula {
  position: absolute;
  border-radius: 50%;
  filter: blur(90px);
  opacity: 0.4;
}

.sky-nebula-a {
  width: 620px;
  height: 620px;
  top: -200px;
  right: 6%;
  background: radial-gradient(circle, rgba(124, 108, 245, 0.55) 0%, transparent 70%);
  animation: sky-drift-a 30s ease-in-out infinite;
}

.sky-nebula-b {
  width: 680px;
  height: 680px;
  bottom: -260px;
  left: 2%;
  background: radial-gradient(circle, rgba(79, 156, 249, 0.42) 0%, transparent 70%);
  animation: sky-drift-b 36s ease-in-out infinite;
}

@keyframes sky-drift-a {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(-34px, 26px); }
}

@keyframes sky-drift-b {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(32px, -22px); }
}

.sky-stars {
  position: absolute;
  inset: 0;
  background-repeat: repeat;
}

.sky-stars-1 {
  background-image:
    radial-gradient(1px 1px at 40px 60px, rgba(220, 228, 255, 0.85), transparent),
    radial-gradient(1px 1px at 160px 120px, rgba(190, 180, 255, 0.7), transparent),
    radial-gradient(1px 1px at 260px 40px, rgba(220, 228, 255, 0.8), transparent),
    radial-gradient(1px 1px at 90px 220px, rgba(200, 215, 255, 0.65), transparent),
    radial-gradient(1px 1px at 320px 180px, rgba(220, 228, 255, 0.8), transparent);
  background-size: 360px 300px;
  animation: sky-twinkle 5s ease-in-out infinite;
}

.sky-stars-2 {
  background-image:
    radial-gradient(1.6px 1.6px at 120px 90px, rgba(190, 180, 255, 0.75), transparent),
    radial-gradient(1.6px 1.6px at 300px 240px, rgba(220, 228, 255, 0.6), transparent),
    radial-gradient(1.6px 1.6px at 420px 140px, rgba(200, 215, 255, 0.6), transparent);
  background-size: 480px 360px;
  animation: sky-twinkle 7s ease-in-out infinite 1.5s;
}

@keyframes sky-twinkle {
  0%, 100% { opacity: 0.35; }
  50% { opacity: 0.85; }
}

.sky-shooting {
  position: absolute;
  top: 12%;
  left: -140px;
  width: 120px;
  height: 1.5px;
  background: linear-gradient(90deg, rgba(160, 190, 255, 0), rgba(190, 210, 255, 0.95));
  border-radius: 2px;
  opacity: 0;
  animation: sky-shoot 9s ease-in infinite 2s;
}

@keyframes sky-shoot {
  0% { opacity: 0; transform: translate(0, 0) rotate(24deg); }
  4% { opacity: 0.9; }
  16% { opacity: 0.9; }
  26% { opacity: 0; transform: translate(60vw, 34vh) rotate(24deg); }
  100% { opacity: 0; transform: translate(60vw, 34vh) rotate(24deg); }
}

.sky-system {
  position: absolute;
  top: 46%;
  left: 52%;
  width: 0;
  height: 0;
}

.sky-sun {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 30px;
  height: 30px;
  margin: -15px 0 0 -15px;
  border-radius: 50%;
  background: radial-gradient(circle at 40% 35%, #fff0c4, #ffc65c 60%, #ff9d3d 90%);
  opacity: 0.5;
  box-shadow: 0 0 40px 14px rgba(255, 180, 90, 0.22);
  animation: sky-sun-pulse 6s ease-in-out infinite;
}

@keyframes sky-sun-pulse {
  0%, 100% { opacity: 0.42; }
  50% { opacity: 0.62; }
}

.sky-orbit {
  position: absolute;
  top: 50%;
  left: 50%;
  border: 1px solid rgba(180, 190, 255, 0.07);
  border-radius: 50%;
  transform: translate(-50%, -50%);
}

.sky-orbit-1 { width: 280px; height: 280px; animation: sky-spin 22s linear infinite; }
.sky-orbit-2 { width: 480px; height: 480px; animation: sky-spin 38s linear infinite; }
.sky-orbit-3 { width: 720px; height: 720px; animation: sky-spin 64s linear infinite; }

@keyframes sky-spin {
  from { transform: translate(-50%, -50%) rotate(0deg); }
  to { transform: translate(-50%, -50%) rotate(360deg); }
}

.sky-planet {
  position: absolute;
  top: -6px;
  left: 50%;
  transform: translateX(-50%);
  border-radius: 50%;
  opacity: 0.7;
}

.sky-planet-1 {
  width: 11px;
  height: 11px;
  background: radial-gradient(circle at 35% 30%, #ffd6a8, #c97a42);
  box-shadow: 0 0 12px rgba(255, 190, 140, 0.5);
}

.sky-planet-2 {
  width: 15px;
  height: 15px;
  top: -7.5px;
  background: radial-gradient(circle at 35% 30%, #bcdcff, #4f8fd6);
  box-shadow: 0 0 14px rgba(120, 180, 255, 0.5);
}

.sky-planet-3 {
  width: 13px;
  height: 13px;
  top: -6.5px;
  background: radial-gradient(circle at 35% 30%, #d8c8ff, #7c6cf5);
  box-shadow: 0 0 14px rgba(140, 120, 255, 0.55);
}

/* ---------- topbar ---------- */
.main-topbar {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 30px;
  position: sticky;
  top: 0;
  z-index: 10;
  background: rgba(10, 11, 16, 0.72);
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
  gap: 7px;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.68rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--text-faint);
}

.topbar-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--success);
  box-shadow: 0 0 8px var(--success);
  animation: pulse-dot 2.4s ease-in-out infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.35; }
}

main {
  position: relative;
  z-index: 1;
  flex: 1;
  padding: 32px 30px;
}

.app-footer {
  position: relative;
  z-index: 1;
  padding: 18px 30px 30px;
  text-align: center;
  color: var(--text-faint);
  font-size: 0.76rem;
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
    padding: 10px 14px;
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
    padding: 22px 16px;
  }

  .topbar-status-text {
    display: none;
  }
}
</style>
