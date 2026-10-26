import { API_BASE } from './config'
import { authToken, logout } from './auth'

// Point d'entree unique vers l'API : ajoute l'adresse de base et le jeton
// d'authentification, que chaque composant repetait jusqu'ici a la main.
export async function apiFetch(path, options = {}) {
  const headers = { ...options.headers }
  if (authToken.value) {
    headers.Authorization = `Token ${authToken.value}`
  }

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers })

  // Jeton expire ou revoque : on ramene a l'ecran de connexion plutot que de
  // laisser chaque page afficher un etat vide sans explication.
  if (response.status === 401 && authToken.value) {
    logout()
  }

  return response
}
