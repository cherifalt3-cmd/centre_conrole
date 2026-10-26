import { API_BASE } from './config'
import { authToken } from './auth'

// Point d'entree unique vers l'API : ajoute l'adresse de base et le jeton
// d'authentification, que chaque composant repetait jusqu'ici a la main.
export function apiFetch(path, options = {}) {
  const headers = { ...options.headers }
  if (authToken.value) {
    headers.Authorization = `Token ${authToken.value}`
  }
  return fetch(`${API_BASE}${path}`, { ...options, headers })
}
