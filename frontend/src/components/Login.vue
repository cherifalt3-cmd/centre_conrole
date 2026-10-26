<script setup>
import { ref } from 'vue'
import { login } from '../auth'
import SpaceBackground from './SpaceBackground.vue'

const username = ref('')
const password = ref('')
const error = ref('')

async function handleLogin() {
  error.value = ''
  try {
    await login(username.value, password.value)
  } catch (e) {
    error.value = e.message
  }
}
</script>

<template>
  <div class="page">
    <SpaceBackground />

    <div class="card">
      <form @submit.prevent="handleLogin">
        <p class="eyebrow">Centre de contrôle</p>
        <h1>Connexion</h1>

        <div class="field">
          <label for="username">Nom d'utilisateur</label>
          <input id="username" v-model="username" type="text" autocomplete="username" />
        </div>

        <div class="field">
          <label for="password">Mot de passe</label>
          <input id="password" v-model="password" type="password" autocomplete="current-password" />
        </div>

        <button class="btn" type="submit">Se connecter</button>

        <p v-if="error" class="error">{{ error }}</p>
      </form>
    </div>
  </div>
</template>

<style scoped>
.page {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

/* ---------- carte (verre sombre) ---------- */
.card {
  position: relative;
  z-index: 1;
  background: rgba(14, 16, 26, 0.6);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-3), 0 0 80px rgba(124, 108, 245, 0.14);
  padding: 40px 32px;
  width: 100%;
  max-width: 376px;
}

/* liseré lumineux sur l'arête haute */
.card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  padding: 1px;
  background: linear-gradient(160deg, rgba(124, 108, 245, 0.6), rgba(255, 255, 255, 0) 45%);
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}

.eyebrow {
  font-family: 'IBM Plex Mono', monospace;
  font-size: var(--fs-xs);
  font-weight: 500;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--accent-text);
  margin: 0 0 8px;
}

h1 {
  font-size: var(--fs-2xl);
  font-weight: 600;
  letter-spacing: -0.02em;
  margin: 0 0 32px;
  color: #fff;
}

.field {
  margin-bottom: 20px;
}

label {
  display: block;
  font-size: var(--fs-sm);
  font-weight: 500;
  color: var(--text-muted);
  margin-bottom: 8px;
}

input {
  width: 100%;
  padding: 12px 12px;
  background: var(--glass-2);
  border: 1px solid var(--border-input);
  border-radius: var(--radius-sm);
  font-size: var(--fs-base);
  color: var(--text);
  transition: border-color 0.16s ease, box-shadow 0.16s ease, background 0.16s ease;
}

input:focus {
  background: var(--glass-3);
  border-color: var(--accent);
}

.btn {
  width: 100%;
  padding: 12px;
  margin-top: 10px;
  background: linear-gradient(135deg, var(--accent-strong), #6355d6);
  color: #fff;
  border: 1px solid var(--accent-line);
  border-radius: var(--radius-sm);
  font-size: var(--fs-base);
  font-weight: 500;
  cursor: pointer;
  box-shadow: 0 6px 24px rgba(124, 108, 245, 0.3);
  transition: filter 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease;
}

.btn:hover {
  filter: brightness(1.12);
  box-shadow: 0 8px 32px rgba(124, 108, 245, 0.45);
  transform: translateY(-1px);
}

.error {
  margin-top: 16px;
  margin-bottom: 0;
  color: var(--danger);
  font-size: var(--fs-base);
}
</style>
