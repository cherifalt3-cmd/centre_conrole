import { ref } from 'vue'
import { API_BASE } from './config'
import { readStored, writeStored, removeStored } from './storage'

// Au démarrage de l'app, on relit le jeton déjà sauvegardé (s'il y en a un) pour rester connecté
export const authToken = ref(readStored('authToken'))

export async function login(username, password) {
  const response = await fetch(`${API_BASE}/api-token-auth/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`,
  })

  if (!response.ok) {
    throw new Error('Identifiants incorrects.')
  }

  const data = await response.json()
  authToken.value = data.token
  writeStored('authToken', data.token)
}

export function logout() {
  authToken.value = null
  removeStored('authToken')
}
