<script setup>
import { ref } from 'vue'

// Ces variables sont "réactives" : l'écran se met à jour automatiquement quand elles changent
const username = ref('')
const password = ref('')
const token = ref('')
const error = ref('')

// Appelée quand le formulaire est soumis
async function handleLogin() {
  error.value = ''
  token.value = ''

  const response = await fetch('http://127.0.0.1:8000/api-token-auth/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: `username=${encodeURIComponent(username.value)}&password=${encodeURIComponent(password.value)}`,
  })

  if (!response.ok) {
    error.value = 'Identifiants incorrects.'
    return
  }

  const data = await response.json()
  token.value = data.token
}
</script>

<template>
  <form @submit.prevent="handleLogin">
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
    <p v-if="token">Connecté ! Jeton reçu : {{ token }}</p>
  </form>
</template>
