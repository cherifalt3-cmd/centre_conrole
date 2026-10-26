// localStorage peut lever une exception : navigation privee, donnees de site
// bloquees, quota depasse. Un acces non protege au chargement d'un module empeche
// toute l'application de demarrer. Ces fonctions ne levent jamais : au pire,
// rien n'est memorise et l'application continue.

export function readStored(key) {
  try {
    return localStorage.getItem(key)
  } catch {
    return null
  }
}

export function writeStored(key, value) {
  try {
    localStorage.setItem(key, value)
  } catch {
    // memorisation impossible, sans consequence pour le reste de l'app
  }
}

export function removeStored(key) {
  try {
    localStorage.removeItem(key)
  } catch {
    // idem
  }
}
