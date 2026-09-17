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

const ACCENTS = ['#8a93a3', '#c98a2b', '#c98a2b', '#2f7d54']

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
    <h2>{{ board?.name || 'Kanban' }}</h2>

    <p v-if="loading" class="empty-hint">Chargement...</p>
    <p v-else-if="!board" class="empty-hint">Aucun tableau pour l'instant.</p>

    <div v-else class="board">
      <div v-for="column in board.columns" :key="column.id" class="column" :style="{ '--accent': columnAccent(column) }">
        <div class="column-accent"></div>
        <div class="column-header">
          <span class="column-title">{{ column.name }}</span>
          <span class="column-count">{{ column.cards.length }}</span>
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
          <button type="submit">+</button>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.kanban {
  max-width: 1040px;
  margin: 0 auto;
}

h2 {
  margin: 0 0 18px;
  font-size: 1.4rem;
  font-weight: 700;
  color: #14201e;
}

.empty-hint {
  color: #5b6478;
  font-size: 0.9rem;
}

.board {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 14px;
  align-items: start;
}

.column {
  position: relative;
  background: #f2f5fa;
  border: 1px solid #d8deea;
  border-radius: 12px;
  padding: 16px 14px 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow: hidden;
  box-shadow: 0 1px 2px rgba(20, 32, 30, 0.04), 0 6px 16px rgba(20, 32, 30, 0.04);
}

.column-accent {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: var(--accent);
}

.column-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.column-title {
  font-weight: 600;
  font-size: 0.92rem;
  color: #14201e;
}

.column-count {
  font-size: 0.76rem;
  font-weight: 600;
  color: var(--accent);
  background: #fff;
  border: 1px solid #d8deea;
  border-radius: 999px;
  padding: 1px 8px;
}

.card-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 4px;
}

.column-empty {
  margin: 4px 0;
  font-size: 0.78rem;
  color: #8a93a3;
  font-style: italic;
  text-align: center;
  padding: 10px 0;
  border: 1px dashed #c5cedb;
  border-radius: 8px;
}

.kanban-card {
  background: #fff;
  border: 1px solid #d8deea;
  border-left: 3px solid var(--accent);
  border-radius: 8px;
  padding: 10px 12px;
  box-shadow: 0 1px 2px rgba(20, 32, 30, 0.04);
  transition: box-shadow 0.15s ease, transform 0.15s ease;
}

.kanban-card:hover {
  box-shadow: 0 4px 12px rgba(20, 32, 30, 0.08);
  transform: translateY(-1px);
}

.card-title {
  margin: 0;
  font-size: 0.88rem;
  font-weight: 500;
  color: #14201e;
  overflow-wrap: break-word;
}

.card-desc {
  margin: 4px 0 0;
  font-size: 0.8rem;
  color: #5b6478;
  overflow-wrap: break-word;
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
}

.move-btn {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  background: #fff;
  border: 1px solid #c5cedb;
  border-radius: 6px;
  color: #1e3a5f;
  cursor: pointer;
  font-size: 0.85rem;
  line-height: 1;
  transition: background 0.15s ease, border-color 0.15s ease;
}

.move-btn:hover:not(:disabled) {
  background: #e5eff5;
  border-color: #1e3a5f;
}

.move-btn:disabled {
  opacity: 0.35;
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
  background: none;
  border: 1px solid #c5cedb;
  color: #a3271b;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s ease, border-color 0.15s ease;
}

.delete-card-btn:hover {
  background: #fbe2e0;
  border-color: #a3271b;
}

.add-card-form {
  display: flex;
  gap: 6px;
}

.add-card-form input {
  flex: 1;
  min-width: 0;
  padding: 7px 10px;
  border: 1px solid #c5cedb;
  border-radius: 7px;
  font-size: 0.85rem;
  box-sizing: border-box;
}

.add-card-form input:focus {
  outline: none;
  border-color: #1e3a5f;
  box-shadow: 0 0 0 3px rgba(30, 58, 95, 0.15);
}

.add-card-form button {
  flex-shrink: 0;
  width: 32px;
  background: #1e3a5f;
  color: #fff;
  border: none;
  border-radius: 7px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s ease;
}

.add-card-form button:hover {
  background: #14213d;
}
</style>
