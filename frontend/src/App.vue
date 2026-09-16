<script setup>
import { ref } from 'vue'
import Login from './components/Login.vue'
import TargetList from './components/TargetList.vue'
import ToolGenerator from './components/ToolGenerator.vue'
import { authToken, logout } from './auth'

const currentView = ref('targets')
</script>

<template>
  <Login v-if="!authToken" />

  <div v-else class="app-shell">
    <aside class="sidebar">
      <div class="sidebar-brand">
        <svg class="sidebar-logo" width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="12" cy="12" r="8.5" stroke="currentColor" stroke-width="2" />
          <circle cx="12" cy="12" r="2.5" fill="currentColor" />
          <line x1="12" y1="0.5" x2="12" y2="4.5" stroke="currentColor" stroke-width="2" />
          <line x1="12" y1="19.5" x2="12" y2="23.5" stroke="currentColor" stroke-width="2" />
          <line x1="0.5" y1="12" x2="4.5" y2="12" stroke="currentColor" stroke-width="2" />
          <line x1="19.5" y1="12" x2="23.5" y2="12" stroke="currentColor" stroke-width="2" />
        </svg>
        Centre de contrôle
      </div>

      <p class="sidebar-section-label">Modules</p>

      <nav class="sidebar-nav">
        <button
          type="button"
          :class="['sidebar-link', { active: currentView === 'targets' }]"
          @click="currentView = 'targets'"
        >
          <svg class="sidebar-link-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2" />
            <circle cx="12" cy="12" r="5" stroke="currentColor" stroke-width="2" />
            <circle cx="12" cy="12" r="1.5" fill="currentColor" />
          </svg>
          Carnet de cibles
        </button>
        <button
          type="button"
          :class="['sidebar-link', { active: currentView === 'generator' }]"
          @click="currentView = 'generator'"
        >
          <svg class="sidebar-link-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="2" y="4" width="20" height="16" rx="2" stroke="currentColor" stroke-width="2" />
            <path d="M6 9L10 12L6 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
            <line x1="12" y1="15" x2="17" y2="15" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
          </svg>
          Générateur de commandes
        </button>
      </nav>

      <button class="sidebar-logout" @click="logout">Se déconnecter</button>
    </aside>

    <div class="main-area">
      <main>
        <TargetList v-if="currentView === 'targets'" />
        <ToolGenerator v-else-if="currentView === 'generator'" />
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
  background: #0a4f48;
  display: flex;
  flex-direction: column;
  padding: 22px 14px;
  box-shadow: 2px 0 12px rgba(10, 24, 22, 0.12);
  z-index: 1;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 9px;
  color: #fff;
  font-weight: 600;
  font-size: 0.98rem;
  letter-spacing: -0.01em;
  padding: 6px 10px 4px;
}

.sidebar-logo {
  color: #59c9b6;
  flex-shrink: 0;
}

.sidebar-section-label {
  font-size: 0.66rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #5f9a90;
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
  color: #a9d4cc;
  text-align: left;
  transition: background 0.15s ease, color 0.15s ease;
}

.sidebar-link-icon {
  flex-shrink: 0;
  color: #59c9b6;
}

.sidebar-link.active .sidebar-link-icon {
  color: #fff;
}

.sidebar-link:hover {
  background: rgba(255, 255, 255, 0.07);
  color: #fff;
}

.sidebar-link.active {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  font-weight: 600;
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
  background: #59c9b6;
}

.sidebar-logout {
  margin-top: 12px;
  padding: 9px 12px;
  background: none;
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 7px;
  cursor: pointer;
  font-size: 0.82rem;
  color: #a9d4cc;
  text-align: left;
  transition: border-color 0.15s ease, color 0.15s ease;
}

.sidebar-logout:hover {
  border-color: rgba(255, 255, 255, 0.5);
  color: #fff;
}

.main-area {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  background: #eef2f1;
}

main {
  flex: 1;
  padding: 28px;
}

.app-footer {
  padding: 20px 28px 32px;
  text-align: center;
  color: #8a9895;
  font-size: 0.8rem;
}

@media (max-width: 640px) {
  .app-shell {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    flex-direction: row;
    align-items: center;
    padding: 12px 16px;
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
