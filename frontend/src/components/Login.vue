<script setup>
import { ref } from 'vue'
import { authToken, login, logout } from '../auth'

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
    <div class="card">
      <div v-if="authToken" class="connected">
        <p class="connected-msg">Connecté.</p>
        <button class="btn btn-secondary" @click="logout">Se déconnecter</button>
      </div>

      <form v-else @submit.prevent="handleLogin">
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
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #eef2f1;
  font-family: system-ui, -apple-system, 'Segoe UI', sans-serif;
}

.card {
  background: #ffffff;
  border: 1px solid #d7e0de;
  border-radius: 14px;
  box-shadow: 0 6px 20px rgba(20, 32, 30, 0.08);
  padding: 36px 34px;
  width: 100%;
  max-width: 360px;
}

.eyebrow {
  font-size: 0.72rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #0a4f48;
  margin: 0 0 6px;
  font-weight: 600;
}

h1 {
  font-size: 1.6rem;
  margin: 0 0 28px;
  color: #14201e;
}

.field {
  margin-bottom: 18px;
}

label {
  display: block;
  font-size: 0.85rem;
  font-weight: 500;
  color: #5b6b68;
  margin-bottom: 6px;
}

input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #c3d0cd;
  border-radius: 8px;
  font-size: 0.95rem;
  box-sizing: border-box;
}

input:focus {
  outline: none;
  border-color: #0f6d63;
  box-shadow: 0 0 0 3px rgba(15, 109, 99, 0.15);
}

.btn {
  width: 100%;
  padding: 11px;
  margin-top: 6px;
  background: #0f6d63;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
}

.btn:hover {
  background: #0a4f48;
}

.btn-secondary {
  width: auto;
  background: #ffffff;
  color: #0f6d63;
  border: 1px solid #0f6d63;
}

.btn-secondary:hover {
  background: #e5eff5;
}

.error {
  margin-top: 14px;
  margin-bottom: 0;
  color: #a85a17;
  font-size: 0.88rem;
}

.connected-msg {
  font-size: 1.1rem;
  color: #14201e;
  margin-bottom: 16px;
}
</style>
