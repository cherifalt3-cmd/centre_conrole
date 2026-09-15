<script setup>
import Login from './components/Login.vue'
import TargetList from './components/TargetList.vue'
import { authToken, logout } from './auth'
</script>

<template>
  <Login v-if="!authToken" />

  <div v-else class="app-shell">
    <header class="topbar">
      <span class="brand">Centre de contrôle</span>
      <button class="logout-btn" @click="logout">Se déconnecter</button>
    </header>
    <main>
      <TargetList />
    </main>
  </div>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
  background: #eef2f1;
  font-family: system-ui, -apple-system, 'Segoe UI', sans-serif;
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 28px;
  background: #ffffff;
  border-bottom: 1px solid #d7e0de;
}

.brand {
  font-weight: 700;
  color: #0a4f48;
}

.logout-btn {
  padding: 7px 14px;
  background: #ffffff;
  color: #0f6d63;
  border: 1px solid #0f6d63;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.85rem;
}

.logout-btn:hover {
  background: #e5eff5;
}

main {
  padding: 28px;
}
</style>
