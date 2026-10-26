<script setup>
import { ref, reactive, onMounted } from 'vue'
import { apiFetch } from '../api'

const board = ref(null)
const loading = ref(false)
const loadError = ref('')
const actionError = ref('')
const newCardTitle = reactive({})

async function fetchBoard() {
  loading.value = true
  loadError.value = ''
  try {
    const response = await apiFetch('/api/kanban/boards/')
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const boards = await response.json()
    board.value = boards.length ? boards[0] : null
  } catch {
    loadError.value = 'Impossible de charger le tableau.'
  } finally {
    loading.value = false
  }
}

onMounted(fetchBoard)

// Une action qui echoue doit le dire : sans ca, la carte semblerait simplement
// ne pas bouger ou ne pas s'ajouter, sans explication.
async function runAction(request, failureMessage) {
  actionError.value = ''
  try {
    const response = await request()
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
  } catch {
    actionError.value = failureMessage
  }
  await fetchBoard()
}

// Le nombre de cartes ne convient pas comme rang : apres une suppression, une
// colonne aux rangs 0 et 2 en compte deux, et la nouvelle carte recevrait le 2,
// deja pris. On part du rang le plus eleve.
function nextOrder(column) {
  return column.cards.reduce((highest, card) => Math.max(highest, card.order), -1) + 1
}

async function addCard(column) {
  const title = (newCardTitle[column.id] || '').trim()
  if (!title) return

  newCardTitle[column.id] = ''
  await runAction(
    () => apiFetch('/api/kanban/cards/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ column: column.id, title, order: nextOrder(column) }),
    }),
    "La carte n'a pas pu être ajoutée.",
  )
}

// Suppression en deux temps : un premier clic arme le bouton (« Confirmer ? »),
// un second supprime. Un clic malencontreux ne detruit plus rien, et c'est plus
// leger qu'une boite de dialogue.
const pendingDeleteId = ref(null)
let pendingDeleteTimer = null

function requestDelete(card) {
  if (pendingDeleteId.value === card.id) {
    clearTimeout(pendingDeleteTimer)
    pendingDeleteId.value = null
    runAction(
      () => apiFetch(`/api/kanban/cards/${card.id}/`, { method: 'DELETE' }),
      "La carte n'a pas pu être supprimée.",
    )
    return
  }
  clearTimeout(pendingDeleteTimer)
  pendingDeleteId.value = card.id
  pendingDeleteTimer = setTimeout(() => (pendingDeleteId.value = null), 4000)
}

async function moveCard(card, direction) {
  const targetColumn = neighbourColumn(card, direction)
  if (!targetColumn) return

  await runAction(
    () => apiFetch(`/api/kanban/cards/${card.id}/`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ column: targetColumn.id, order: nextOrder(targetColumn) }),
    }),
    "La carte n'a pas pu être déplacée.",
  )
}

function neighbourColumn(card, direction) {
  const columns = board.value.columns
  const index = columns.findIndex((c) => c.id === card.column)
  return columns[index + direction] || null
}

// Nom accessible des fleches : « flèche gauche » ne dit ni quoi ni ou
function moveLabel(card, direction) {
  const target = neighbourColumn(card, direction)
  return target ? `Déplacer « ${card.title} » vers « ${target.name} »` : ''
}

function isFirstColumn(column) {
  return board.value.columns[0]?.id === column.id
}

function isLastColumn(column) {
  return board.value.columns[board.value.columns.length - 1]?.id === column.id
}

// Le gris de depart atteint 5:1 sur la carte : il sert aussi de couleur de texte
// au compteur de la colonne.
const COLUMN_COLORS = ['#7f8698', '#f5c26b', '#f5c26b', '#3ddc97']

function columnColor(column) {
  const total = board.value.columns.length
  const index = board.value.columns.findIndex((c) => c.id === column.id)
  if (index === 0) return COLUMN_COLORS[0]
  if (index === total - 1) return COLUMN_COLORS[3]
  return COLUMN_COLORS[1]
}
</script>

<template>
  <div class="kanban">
    <div class="kanban-head">
      <p class="eyebrow">Tableau</p>
      <h2>{{ board?.name || 'Kanban' }}</h2>
    </div>

    <p v-if="actionError" class="kanban-error" role="alert">{{ actionError }}</p>

    <p v-if="loading && !board" class="empty-hint">Chargement...</p>
    <p v-else-if="loadError" class="kanban-error" role="alert">{{ loadError }}</p>
    <p v-else-if="!board" class="empty-hint">Aucun tableau pour l'instant.</p>

    <div v-else class="board">
      <section
        v-for="column in board.columns"
        :key="column.id"
        class="column"
        :style="{ '--column-color': columnColor(column) }"
        :aria-labelledby="`column-title-${column.id}`"
      >
        <div class="column-accent"></div>
        <div class="column-header">
          <h3 :id="`column-title-${column.id}`" class="column-title">{{ column.name }}</h3>
          <span class="column-count tabular">
            {{ column.cards.length }}<span class="visually-hidden">
              carte{{ column.cards.length === 1 ? '' : 's' }}</span>
          </span>
        </div>

        <div class="card-list">
          <p v-if="column.cards.length === 0" class="column-empty">Aucune carte</p>
          <article v-for="card in column.cards" :key="card.id" class="kanban-card">
            <p class="card-title">{{ card.title }}</p>
            <p v-if="card.description" class="card-desc">{{ card.description }}</p>
            <div class="card-actions">
              <button
                type="button"
                class="move-btn"
                :disabled="isFirstColumn(column)"
                :aria-label="moveLabel(card, -1) || 'Déjà dans la première colonne'"
                :title="moveLabel(card, -1) || null"
                @click="moveCard(card, -1)"
              >
                ←
              </button>
              <button
                type="button"
                class="move-btn"
                :disabled="isLastColumn(column)"
                :aria-label="moveLabel(card, 1) || 'Déjà dans la dernière colonne'"
                :title="moveLabel(card, 1) || null"
                @click="moveCard(card, 1)"
              >
                →
              </button>
              <button
                type="button"
                :class="['delete-card-btn', { armed: pendingDeleteId === card.id }]"
                :aria-label="
                  pendingDeleteId === card.id
                    ? `Confirmer la suppression de « ${card.title} »`
                    : `Supprimer « ${card.title} »`
                "
                @click="requestDelete(card)"
              >
                <span v-if="pendingDeleteId === card.id" class="delete-confirm">Confirmer ?</span>
                <svg aria-hidden="true" focusable="false" v-else width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M4 7H20" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
                  <path d="M9 7V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                  <path d="M6 7L7 20a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1l1-13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
              </button>
            </div>
          </article>
        </div>

        <form class="add-card-form" @submit.prevent="addCard(column)">
          <label :for="`new-card-${column.id}`" class="visually-hidden">
            Nouvelle carte dans « {{ column.name }} »
          </label>
          <input
            :id="`new-card-${column.id}`"
            v-model="newCardTitle[column.id]"
            type="text"
            placeholder="Nouvelle carte..."
          />
          <button type="submit" :aria-label="`Ajouter la carte dans « ${column.name} »`">+</button>
        </form>
      </section>
    </div>
  </div>
</template>

<style scoped>
.kanban {
  max-width: 1120px;
  margin: 0 auto;
}

.kanban-head {
  margin-bottom: 16px;
}

h2 {
  margin: 4px 0 0;
  font-size: var(--fs-xl);
  font-weight: 600;
  letter-spacing: -0.02em;
  color: var(--text);
}

.empty-hint {
  color: var(--text-muted);
  font-size: var(--fs-base);
}

.board {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(248px, 1fr));
  gap: 16px;
  align-items: start;
}

.column {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: var(--glass-1);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px 16px 16px;
  overflow: hidden;
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  box-shadow: var(--shadow-2);
}

.column-accent {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--column-color);
  box-shadow: 0 0 16px var(--column-color);
}

.column-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.column-title {
  font-weight: 600;
  font-size: var(--fs-base);
  color: var(--text);
}

.column-count {
  font-size: var(--fs-xs);
  font-weight: 600;
  color: var(--column-color);
  background: color-mix(in srgb, var(--column-color) 12%, transparent);
  border: 1px solid color-mix(in srgb, var(--column-color) 28%, transparent);
  border-radius: 999px;
  padding: 1px 10px;
}

.card-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 4px;
}

.column-empty {
  margin: 2px 0;
  font-size: var(--fs-xs);
  color: var(--text-faint);
  font-style: italic;
  text-align: center;
  padding: 12px 0;
  border: 1px dashed var(--border-strong);
  border-radius: var(--radius-sm);
}

.kanban-card {
  position: relative;
  background: var(--glass-2);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 12px 12px;
  transition: background 0.16s ease, border-color 0.16s ease, transform 0.16s ease, box-shadow 0.16s ease;
}

.kanban-card::before {
  content: '';
  position: absolute;
  top: 10px;
  bottom: 10px;
  left: 0;
  width: 2px;
  border-radius: 0 2px 2px 0;
  background: var(--column-color);
}

.kanban-card:hover {
  background: var(--glass-3);
  border-color: var(--border-strong);
  transform: translateY(-2px);
  box-shadow: var(--shadow-2);
}

.card-title {
  margin: 0;
  font-size: var(--fs-base);
  font-weight: 500;
  color: var(--text);
  overflow-wrap: break-word;
}

.card-desc {
  margin: 4px 0 0;
  font-size: var(--fs-xs);
  color: var(--text-muted);
  overflow-wrap: break-word;
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 10px;
  opacity: 0.55;
  transition: opacity 0.16s ease;
}

/* Le clavier doit reveler les actions aussi bien que la souris */
.kanban-card:hover .card-actions,
.kanban-card:focus-within .card-actions {
  opacity: 1;
}

/* 32px : au-dela du minimum WCAG de 24px, plus confortable a viser (Fitts) */
.move-btn {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  background: var(--glass-2);
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--text-muted);
  cursor: pointer;
  font-size: var(--fs-sm);
  line-height: 1;
  transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease;
}

.move-btn:hover:not(:disabled) {
  background: var(--accent-soft);
  border-color: var(--accent-line);
  color: var(--text);
}

.move-btn:disabled {
  opacity: 0.28;
  cursor: not-allowed;
}

/* Isolee a droite, loin des fleches : une suppression ne doit pas etre a un
   glissement de souris d'un deplacement */
.delete-card-btn {
  flex-shrink: 0;
  margin-left: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 32px;
  background: var(--glass-2);
  border: 1px solid var(--border);
  color: var(--text-faint);
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease;
}

.delete-card-btn:hover {
  background: var(--danger-soft);
  border-color: var(--danger);
  color: var(--danger);
}

/* L'etat arme est plein : une action irreversible doit se distinguer nettement
   d'un simple survol, et un rouge sur fond rougi n'atteignait que 4,08:1 */
.delete-card-btn.armed {
  background: var(--danger-strong);
  border-color: var(--danger-strong);
  color: #fff;
}

.delete-confirm {
  padding: 0 10px;
  font-size: var(--fs-xs);
  font-weight: 600;
  white-space: nowrap;
}

.kanban-error {
  color: var(--danger);
  font-size: var(--fs-base);
  margin-bottom: 12px;
}

.add-card-form {
  display: flex;
  gap: 6px;
}

.add-card-form input {
  flex: 1;
  min-width: 0;
  padding: 8px 12px;
  background: var(--glass-1);
  border: 1px solid var(--border-input);
  border-radius: var(--radius-sm);
  color: var(--text);
  font-size: var(--fs-sm);
  transition: border-color 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
}

.add-card-form input::placeholder {
  color: var(--text-faint);
}

.add-card-form input:focus {
  background: var(--glass-2);
  border-color: var(--accent);
}

.add-card-form button {
  flex-shrink: 0;
  width: 34px;
  background: var(--accent-soft);
  color: var(--text);
  border: 1px solid var(--accent-line);
  border-radius: var(--radius-sm);
  font-size: var(--fs-md);
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s ease, box-shadow 0.15s ease;
}

.add-card-form button:hover {
  background: rgba(124, 108, 245, 0.26);
  box-shadow: 0 0 18px rgba(124, 108, 245, 0.3);
}
</style>
