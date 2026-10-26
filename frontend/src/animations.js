import { reactive, watch } from 'vue'
import { readStored, writeStored } from './storage'

// Creatures du fond spatial que l'utilisateur peut afficher ou masquer une a une.
// L'etat est partage : la barre superieure les coche, le fond les affiche.
export const ANIMATIONS = [
  { key: 'rocket', label: 'Fusée' },
  { key: 'saucer', label: 'Soucoupe' },
  { key: 'shuttle', label: 'Navette' },
  { key: 'monsters', label: 'Monstres de feu' },
  { key: 'comet', label: 'Comète' },
  { key: 'astronaut', label: 'Astronaute' },
  { key: 'satellite', label: 'Satellite' },
]

function readChoices() {
  try {
    return JSON.parse(readStored('animationChoices') || '{}')
  } catch {
    return {}
  }
}

const stored = readChoices()

// Tout est affiche par defaut ; seul un choix explicite (false) masque une creature
export const enabledAnimations = reactive(
  Object.fromEntries(ANIMATIONS.map(({ key }) => [key, stored[key] !== false])),
)

watch(enabledAnimations, (choices) => writeStored('animationChoices', JSON.stringify(choices)), {
  deep: true,
})
