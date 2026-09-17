<script setup>
import { ref, watch } from 'vue'
import Login from './components/Login.vue'
import Dashboard from './components/Dashboard.vue'
import TargetList from './components/TargetList.vue'
import ToolGenerator from './components/ToolGenerator.vue'
import Veille from './components/Veille.vue'
import Kanban from './components/Kanban.vue'
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

      <p class="sidebar-section-label">Modules</p>

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
      </nav>

      <div class="sidebar-doodle">
        <svg width="104" height="104" viewBox="0 0 64 64" shape-rendering="crispEdges" xmlns="http://www.w3.org/2000/svg">
          <!-- mer -->
          <rect x="30" y="44" width="34" height="20" fill="#3f6fb8" />
          <rect x="30" y="44" width="34" height="3" fill="#5b9bf0" />

          <!-- ponton -->
          <rect x="0" y="42" width="4" height="6" fill="#c9822b" />
          <rect x="4" y="42" width="4" height="6" fill="#8a5a2b" />
          <rect x="8" y="42" width="4" height="6" fill="#c9822b" />
          <rect x="12" y="42" width="4" height="6" fill="#8a5a2b" />
          <rect x="16" y="42" width="4" height="6" fill="#c9822b" />
          <rect x="20" y="42" width="4" height="6" fill="#8a5a2b" />
          <rect x="24" y="42" width="4" height="6" fill="#c9822b" />
          <rect x="28" y="42" width="4" height="6" fill="#8a5a2b" />
          <rect x="2" y="48" width="4" height="10" fill="#6b4423" />
          <rect x="24" y="48" width="4" height="10" fill="#6b4423" />

          <!-- personnage assis, profil face à la mer -->
          <g class="doodle-figure">
            <!-- casquette -->
            <rect x="14" y="16" width="12" height="4" fill="#3d2f8f" />
            <rect x="14" y="20" width="12" height="2" fill="#3d2f8f" />
            <rect x="26" y="20" width="6" height="2" fill="#2a2066" />
            <!-- visage -->
            <rect x="16" y="22" width="12" height="6" fill="#e8b382" />
            <rect x="24" y="24" width="2" height="2" fill="#2b2b4a" />
            <rect x="28" y="24" width="2" height="2" fill="#e8b382" />
            <!-- veste -->
            <rect x="14" y="28" width="14" height="10" fill="#5a7247" />
            <rect x="14" y="28" width="14" height="2" fill="#6b855a" />
            <!-- jambes qui pendent au bord -->
            <rect x="16" y="38" width="14" height="2" fill="#2b2b4a" />
            <rect x="20" y="40" width="4" height="10" fill="#2b2b4a" />
            <rect x="26" y="40" width="4" height="10" fill="#2b2b4a" />
            <rect x="19" y="50" width="6" height="3" fill="#14213d" />
            <rect x="25" y="50" width="6" height="3" fill="#14213d" />
          </g>

          <!-- bras + canne (balance et pique) -->
          <g class="doodle-rod">
            <rect x="26" y="30" width="4" height="3" fill="#5a7247" />
            <rect x="29" y="32" width="4" height="3" fill="#5a7247" />
            <rect x="32" y="33" width="3" height="3" fill="#e8b382" />
            <rect x="35" y="31" width="4" height="3" fill="#8a5a34" />
            <rect x="39" y="28" width="4" height="3" fill="#8a5a34" />
            <rect x="43" y="25" width="4" height="3" fill="#8a5a34" />
            <rect x="47" y="22" width="4" height="3" fill="#a06a3f" />
          </g>

          <!-- ligne -->
          <rect class="doodle-line" x="49" y="25" width="1" height="20" fill="#dfe6ef" />

          <!-- flotteur -->
          <g class="doodle-bobber">
            <rect x="48" y="43" width="3" height="2" fill="#e6e6e6" />
            <rect x="48" y="45" width="3" height="2" fill="#d9534f" />
          </g>

          <!-- ondes autour du flotteur -->
          <rect class="doodle-ring doodle-ring-l" x="43" y="47" width="3" height="1" fill="#fff" />
          <rect class="doodle-ring doodle-ring-r" x="53" y="47" width="3" height="1" fill="#fff" />

          <!-- vaguelettes -->
          <g class="doodle-water" fill="#fff">
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
      <!-- décor spatial clair -->
      <div class="space-bg">
        <div class="sky-nebula sky-nebula-a"></div>
        <div class="sky-nebula sky-nebula-b"></div>
        <div class="sky-stars sky-stars-1"></div>
        <div class="sky-stars sky-stars-2"></div>
        <div class="sky-shooting"></div>
        <div class="sky-system">
          <div class="sky-sun"></div>
          <div class="sky-orbit sky-orbit-1"><span class="sky-planet sky-planet-1"></span></div>
          <div class="sky-orbit sky-orbit-2"><span class="sky-planet sky-planet-2"></span></div>
          <div class="sky-orbit sky-orbit-3"><span class="sky-planet sky-planet-3"></span></div>
        </div>
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
      </div>
      <main>
        <Dashboard v-if="currentView === 'dashboard'" @navigate="currentView = $event" />
        <TargetList v-else-if="currentView === 'targets'" />
        <ToolGenerator v-else-if="currentView === 'generator'" />
        <Veille v-else-if="currentView === 'veille'" />
        <Kanban v-else-if="currentView === 'kanban'" />
      </main>
      <footer class="app-footer">Centre de contrôle — usage local</footer>
    </div>
  </div>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: flex;
}

.sidebar {
  width: 240px;
  flex-shrink: 0;
  background: linear-gradient(180deg, #1a2c4d 0%, #101a30 100%);
  display: flex;
  flex-direction: column;
  padding: 22px 14px;
  margin-block: 6px;
  margin-inline-start: 0;
  border-radius: 12px;
  box-shadow: 2px 0 12px rgba(10, 24, 22, 0.12);
  z-index: 1;
  overflow: hidden;
  transition: width 0.2s ease, margin 0.2s ease, padding 0.2s ease, opacity 0.15s ease;
  position: sticky;
  top: 6px;
  align-self: flex-start;
  height: calc(100vh - 12px);
}

/* mode réduit : bande étroite avec les icônes seulement */
.sidebar.collapsed {
  width: 64px;
  padding-inline: 10px;
}

.sidebar.collapsed .sidebar-label {
  display: none;
}

.sidebar.collapsed .sidebar-section-label {
  visibility: hidden;
  height: 0;
  padding: 10px 0 0;
}

.sidebar.collapsed .sidebar-doodle {
  display: none;
}

.sidebar.collapsed .sidebar-brand {
  justify-content: center;
  padding-inline: 0;
}

.sidebar.collapsed .sidebar-link,
.sidebar.collapsed .sidebar-logout {
  justify-content: center;
  padding-inline: 0;
}

.sidebar.collapsed .sidebar-link.active::before {
  display: none;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 9px;
  color: #fff;
  font-weight: 600;
  font-size: 0.98rem;
  letter-spacing: -0.01em;
  padding: 6px 10px 18px;
  margin-bottom: 6px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.sidebar-logo {
  width: 38px;
  height: 38px;
  object-fit: contain;
  flex-shrink: 0;
  filter: drop-shadow(1.5px 0 0 #fff) drop-shadow(-1.5px 0 0 #fff) drop-shadow(0 1.5px 0 #fff) drop-shadow(0 -1.5px 0 #fff);
}

.sidebar-section-label {
  font-size: 0.66rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #7288b5;
  padding: 22px 10px 8px;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 14px;
  flex: 1;
}

.sidebar-link {
  position: relative;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px 9px 16px;
  background: none;
  border: none;
  border-radius: 7px;
  cursor: pointer;
  font-size: 0.87rem;
  color: #a9bede;
  text-align: left;
  transition: background 0.15s ease, color 0.15s ease, transform 0.15s ease;
}

.sidebar-link-icon {
  flex-shrink: 0;
  color: #6c8ebf;
}

.sidebar-link.active .sidebar-link-icon {
  color: #fff;
}

.sidebar-link:hover {
  background: rgba(255, 255, 255, 0.07);
  color: #fff;
  transform: translateX(2px);
}

.sidebar-link.active {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.sidebar-link.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 16px;
  border-radius: 2px;
  background: #6c8ebf;
}

.sidebar-doodle {
  display: flex;
  justify-content: center;
  padding-top: 8px;
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

/* balance douce, puis pique d'un coup (une touche) puis remonte */
@keyframes doodle-cast {
  0%, 55% {
    transform: rotate(0deg);
  }
  40% {
    transform: rotate(-2deg);
  }
  65% {
    transform: rotate(7deg);
  }
  72% {
    transform: rotate(-5deg);
  }
  82% {
    transform: rotate(2deg);
  }
  100% {
    transform: rotate(0deg);
  }
}

/* le flotteur ondule, puis plonge au moment de la touche */
@keyframes doodle-dip {
  0%, 45% {
    transform: translateY(0);
  }
  25% {
    transform: translateY(1px);
  }
  60% {
    transform: translateY(1px);
  }
  66% {
    transform: translateY(5px);
  }
  78% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(0);
  }
}

/* la ligne s'étire quand le flotteur plonge */
@keyframes doodle-line {
  0%, 60% {
    transform: scaleY(1);
  }
  66% {
    transform: scaleY(1.22);
  }
  78% {
    transform: scaleY(1);
  }
  100% {
    transform: scaleY(1);
  }
}

@keyframes doodle-ring-l {
  0%, 63% {
    opacity: 0;
    transform: translateX(0);
  }
  70% {
    opacity: 1;
  }
  100% {
    opacity: 0;
    transform: translateX(-4px);
  }
}

@keyframes doodle-ring-r {
  0%, 63% {
    opacity: 0;
    transform: translateX(0);
  }
  70% {
    opacity: 1;
  }
  100% {
    opacity: 0;
    transform: translateX(4px);
  }
}

@keyframes doodle-ripple {
  0%, 49% {
    opacity: 1;
  }
  50%, 100% {
    opacity: 0.3;
  }
}

@keyframes doodle-bob {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-1px);
  }
}

.sidebar-logout {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 12px;
  padding: 14px 12px 9px;
  background: none;
  border: none;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 0;
  cursor: pointer;
  font-size: 0.82rem;
  color: #a9bede;
  text-align: left;
  transition: color 0.15s ease;
}

.sidebar-logout-icon {
  flex-shrink: 0;
  color: #6c8ebf;
}

.sidebar-logout:hover {
  color: #fff;
}

.main-area {
  position: relative;
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  background: transparent;
}

/* ---------- décor spatial clair ---------- */
.space-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  background: #eef1f6;
  overflow: hidden;
  pointer-events: none;
}

.sky-nebula {
  position: absolute;
  border-radius: 50%;
  filter: blur(70px);
  opacity: 0.45;
}

.sky-nebula-a {
  width: 560px;
  height: 560px;
  top: -160px;
  right: 10%;
  background: radial-gradient(circle, #d7c9ff 0%, transparent 70%);
  animation: sky-drift-a 30s ease-in-out infinite;
}

.sky-nebula-b {
  width: 620px;
  height: 620px;
  bottom: -220px;
  left: 5%;
  background: radial-gradient(circle, #cfe0ff 0%, transparent 70%);
  animation: sky-drift-b 36s ease-in-out infinite;
}

@keyframes sky-drift-a {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(-30px, 24px); }
}

@keyframes sky-drift-b {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(30px, -20px); }
}

.sky-stars {
  position: absolute;
  inset: 0;
  background-repeat: repeat;
}

.sky-stars-1 {
  background-image:
    radial-gradient(1px 1px at 40px 60px, rgba(70, 100, 170, 0.5), transparent),
    radial-gradient(1px 1px at 160px 120px, rgba(120, 90, 190, 0.45), transparent),
    radial-gradient(1px 1px at 260px 40px, rgba(70, 100, 170, 0.5), transparent),
    radial-gradient(1px 1px at 90px 220px, rgba(90, 110, 180, 0.4), transparent),
    radial-gradient(1px 1px at 320px 180px, rgba(70, 100, 170, 0.5), transparent);
  background-size: 360px 300px;
  animation: sky-twinkle 5s ease-in-out infinite;
}

.sky-stars-2 {
  background-image:
    radial-gradient(1.5px 1.5px at 120px 90px, rgba(120, 90, 190, 0.45), transparent),
    radial-gradient(1.5px 1.5px at 300px 240px, rgba(70, 100, 170, 0.4), transparent),
    radial-gradient(1.5px 1.5px at 420px 140px, rgba(90, 110, 180, 0.4), transparent);
  background-size: 480px 360px;
  animation: sky-twinkle 7s ease-in-out infinite 1.5s;
}

@keyframes sky-twinkle {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.9; }
}

.sky-shooting {
  position: absolute;
  top: 12%;
  left: -140px;
  width: 110px;
  height: 2px;
  background: linear-gradient(90deg, rgba(120, 150, 220, 0), rgba(120, 150, 220, 0.9));
  border-radius: 2px;
  opacity: 0;
  animation: sky-shoot 9s ease-in infinite 2s;
}

@keyframes sky-shoot {
  0% { opacity: 0; transform: translate(0, 0) rotate(24deg); }
  4% { opacity: 0.8; }
  16% { opacity: 0.8; }
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
  width: 34px;
  height: 34px;
  margin: -17px 0 0 -17px;
  border-radius: 50%;
  background: radial-gradient(circle at 40% 35%, #ffe7a8, #ffc65c 60%, #ffb03d 90%);
  opacity: 0.55;
  box-shadow: 0 0 26px 10px rgba(255, 190, 90, 0.28);
  animation: sky-sun-pulse 6s ease-in-out infinite;
}

@keyframes sky-sun-pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 0.7; }
}

.sky-orbit {
  position: absolute;
  top: 50%;
  left: 50%;
  border: 1px solid rgba(70, 100, 170, 0.1);
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
  opacity: 0.6;
}

.sky-planet-1 {
  width: 12px;
  height: 12px;
  background: radial-gradient(circle at 35% 30%, #ffd6a8, #d98a52);
}

.sky-planet-2 {
  width: 16px;
  height: 16px;
  top: -8px;
  background: radial-gradient(circle at 35% 30%, #bcdcff, #6a9fe0);
}

.sky-planet-3 {
  width: 14px;
  height: 14px;
  top: -7px;
  background: radial-gradient(circle at 35% 30%, #d8c8ff, #9070d0);
}

.main-topbar {
  padding: 16px 28px;
  position: sticky;
  top: 0;
  z-index: 10;
  background: rgba(238, 241, 246, 0.82);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
}

.sidebar-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  background: #fff;
  border: 1px solid #d8deea;
  border-radius: 8px;
  color: #5b6478;
  cursor: pointer;
  transition: border-color 0.15s ease, color 0.15s ease;
}

.sidebar-toggle:hover {
  border-color: #1e3a5f;
  color: #1e3a5f;
}

main {
  position: relative;
  z-index: 1;
  flex: 1;
  padding: 28px;
}

.app-footer {
  position: relative;
  z-index: 1;
  padding: 20px 28px 32px;
  text-align: center;
  color: #8a93a3;
  font-size: 0.8rem;
}

@media (max-width: 640px) {
  .app-shell {
    flex-direction: column;
  }

  .sidebar,
  .sidebar.collapsed {
    width: 100%;
    flex-direction: row;
    align-items: center;
    padding: 12px 16px;
  }

  .sidebar.collapsed .sidebar-brand,
  .sidebar.collapsed .sidebar-link,
  .sidebar.collapsed .sidebar-logout {
    padding-inline: 8px;
  }

  .sidebar-brand {
    padding: 0 14px 0 0;
  }

  .sidebar-nav {
    flex-direction: row;
  }

  .sidebar-logout {
    margin-top: 0;
    margin-left: auto;
  }
}
</style>
