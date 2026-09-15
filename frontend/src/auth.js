import { ref } from 'vue'

// Au démarrage de l'app, on relit le jeton déjà sauvegardé (s'il y en a un) pour rester connecté
export const authToken = ref(localStorage.getItem('authToken'))

export async function login(username, password) {
  const response = await fetch('http://127.0.0.1:8000/api-token-auth/', {
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
  localStorage.setItem('authToken', data.token)
}

export function logout() {
  authToken.value = null
  localStorage.removeItem('authToken')
}
