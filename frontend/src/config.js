// Adresse de l'API Django. Surchargeable par VITE_API_URL pour un hebergement,
// sans toucher au code.
export const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
