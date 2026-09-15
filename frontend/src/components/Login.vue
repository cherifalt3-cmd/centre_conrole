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
  <div v-if="authToken">
    <p>Connecté.</p>
    <button @click="logout">Se déconnecter</button>
  </div>

  <form v-else @submit.prevent="handleLogin">
    <h1>Connexion</h1>

    <div>
      <label for="username">Nom d'utilisateur</label>
      <input id="username" v-model="username" type="text" />
    </div>

    <div>
      <label for="password">Mot de passe</label>
      <input id="password" v-model="password" type="password" />
    </div>

    <button type="submit">Se connecter</button>

    <p v-if="error">{{ error }}</p>
  </form>
</template>
