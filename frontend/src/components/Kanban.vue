<script setup>
import { ref, reactive, onMounted } from 'vue'
import { authToken } from '../auth'

const board = ref(null)
const loading = ref(false)
const newCardTitle = reactive({})

async function fetchBoard() {
  loading.value = true
  const response = await fetch('http://127.0.0.1:8000/api/kanban/boards/', {
    headers: { Authorization: `Token ${authToken.value}` },
  })
  const boards = await response.json()
  board.value = boards.length ? boards[0] : null
  loading.value = false
}

onMounted(fetchBoard)

async function addCard(column) {
  const title = (newCardTitle[column.id] || '').trim()
  if (!title) return

  await fetch('http://127.0.0.1:8000/api/kanban/cards/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Token ${authToken.value}`,
    },
    body: JSON.stringify({ column: column.id, title, order: column.cards.length }),
  })

  newCardTitle[column.id] = ''
  await fetchBoard()
}

async function deleteCard(cardId) {
  await fetch(`http://127.0.0.1:8000/api/kanban/cards/${cardId}/`, {
    method: 'DELETE',
    headers: { Authorization: `Token ${authToken.value}` },
  })
  await fetchBoard()
}

async function moveCard(card, direction) {
  const columns = board.value.columns
  const currentIndex = columns.findIndex((c) => c.id === card.column)
  const targetIndex = currentIndex + direction
  if (targetIndex < 0 || targetIndex >= columns.length) return

  const targetColumn = columns[targetIndex]

  await fetch(`http://127.0.0.1:8000/api/kanban/cards/${card.id}/`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Token ${authToken.value}`,
    },
    body: JSON.stringify({ column: targetColumn.id, order: targetColumn.cards.length }),
  })

  await fetchBoard()
}

function isFirstColumn(column) {
  return board.value.columns[0]?.id === column.id
}

function isLastColumn(column) {
  return board.value.columns[board.value.columns.length - 1]?.id === column.id
}

const ACCENTS = ['#6a7183', '#f5c26b', '#f5c26b', '#3ddc97']

function columnAccent(column) {
  const total = board.value.columns.length
  const index = board.value.columns.findIndex((c) => c.id === column.id)
  if (index === 0) return ACCENTS[0]
  if (index === total - 1) return ACCENTS[3]
  return ACCENTS[1]
}
</script>

<template>
  <div class="kanban">
    <div class="kanban-head">
      <p class="eyebrow">Tableau</p>
      <h2>{{ board?.name || 'Kanban' }}</h2>
    </div>

    <p v-if="loading" class="empty-hint">Chargement...</p>
    <p v-else-if="!board" class="empty-hint">Aucun tableau pour l'instant.</p>

    <div v-else class="board">
      <div v-for="column in board.columns" :key="column.id" class="column" :style="{ '--accent': columnAccent(column) }">
        <div class="column-accent"></div>
        <div class="column-header">
          <span class="column-title">{{ column.name }}</span>
          <span class="column-count tabular">{{ column.cards.length }}</span>
        </div>

        <div class="card-list">
          <p v-if="column.cards.length === 0" class="column-empty">Aucune carte</p>
          <div v-for="card in column.cards" :key="card.id" class="kanban-card">
            <p class="card-title">{{ card.title }}</p>
            <p v-if="card.description" class="card-desc">{{ card.description }}</p>
            <div class="card-actions">
              <button
                type="button"
                class="move-btn"
                :disabled="isFirstColumn(column)"
                title="Déplacer vers la colonne précédente"
                @click="moveCard(card, -1)"
              >
                ←
              </button>
              <button
                type="button"
                class="move-btn"
                :disabled="isLastColumn(column)"
                title="Déplacer vers la colonne suivante"
                @click="moveCard(card, 1)"
              >
                →
              </button>
              <button type="button" class="delete-card-btn" title="Supprimer" @click="deleteCard(card.id)">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M4 7H20" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
                  <path d="M9 7V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                  <path d="M6 7L7 20a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1l1-13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <form class="add-card-form" @submit.prevent="addCard(column)">
          <input v-model="newCardTitle[column.id]" type="text" placeholder="Nouvelle carte..." />
          <button type="submit" title="Ajouter">+</button>
        </form>
      </div>
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
  font-size: 1.32rem;
  font-weight: 600;
  letter-spacing: -0.02em;
  color: var(--text);
}

.empty-hint {
  color: var(--text-muted);
  font-size: 0.9rem;
}

.board {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(248px, 1fr));
  gap: 14px;
  align-items: start;
}

.column {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 11px;
  background: var(--glass-1);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 17px 14px 14px;
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
  background: var(--accent);
  box-shadow: 0 0 16px var(--accent);
}

.column-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.column-title {
  font-weight: 600;
  font-size: 0.88rem;
  color: var(--text);
}

.column-count {
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--accent);
  background: color-mix(in srgb, var(--accent) 12%, transparent);
  border: 1px solid color-mix(in srgb, var(--accent) 28%, transparent);
  border-radius: 999px;
  padding: 1px 9px;
}

.card-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 4px;
}

.column-empty {
  margin: 2px 0;
  font-size: 0.76rem;
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
  padding: 11px 12px;
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
  background: var(--accent);
}

.kanban-card:hover {
  background: var(--glass-3);
  border-color: var(--border-strong);
  transform: translateY(-2px);
  box-shadow: var(--shadow-2);
}

.card-title {
  margin: 0;
  font-size: 0.86rem;
  font-weight: 500;
  color: var(--text);
  overflow-wrap: break-word;
}

.card-desc {
  margin: 4px 0 0;
  font-size: 0.78rem;
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

.kanban-card:hover .card-actions {
  opacity: 1;
}

.move-btn {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  background: var(--glass-2);
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 0.82rem;
  line-height: 1;
  transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease;
}

.move-btn:hover:not(:disabled) {
  background: var(--accent-soft);
  border-color: var(--accent-line);
  color: var(--accent);
}

.move-btn:disabled {
  opacity: 0.28;
  cursor: not-allowed;
}

.delete-card-btn {
  flex-shrink: 0;
  margin-left: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
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

.add-card-form {
  display: flex;
  gap: 6px;
}

.add-card-form input {
  flex: 1;
  min-width: 0;
  padding: 8px 11px;
  background: var(--glass-1);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text);
  font-size: 0.83rem;
  transition: border-color 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
}

.add-card-form input::placeholder {
  color: var(--text-faint);
}

.add-card-form input:focus {
  outline: none;
  background: var(--glass-2);
  border-color: var(--accent-line);
  box-shadow: 0 0 0 3px var(--accent-soft);
}

.add-card-form button {
  flex-shrink: 0;
  width: 34px;
  background: var(--accent-soft);
  color: var(--accent);
  border: 1px solid var(--accent-line);
  border-radius: var(--radius-sm);
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s ease, box-shadow 0.15s ease;
}

.add-card-form button:hover {
  background: rgba(124, 108, 245, 0.26);
  box-shadow: 0 0 18px rgba(124, 108, 245, 0.3);
}
</style>
