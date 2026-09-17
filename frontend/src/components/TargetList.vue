<script setup>
import { ref, onMounted } from 'vue'
import { authToken } from '../auth'

const targets = ref([])
const newName = ref('')
const newAddress = ref('')
const newNotes = ref('')
const error = ref('')
const copiedId = ref(null)

const editingId = ref(null)
const editName = ref('')
const editAddress = ref('')
const editNotes = ref('')

function startEdit(target) {
  editingId.value = target.id
  editName.value = target.name
  editAddress.value = target.address
  editNotes.value = target.notes
}

function cancelEdit() {
  editingId.value = null
}

async function saveEdit(target) {
  const response = await fetch(`http://127.0.0.1:8000/api/recon/targets/${target.id}/`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Token ${authToken.value}`,
    },
    body: JSON.stringify({
      name: editName.value,
      address: editAddress.value,
      notes: editNotes.value,
    }),
  })

  if (!response.ok) {
    error.value = 'Impossible de modifier la cible.'
    return
  }

  editingId.value = null
  await fetchTargets()
}

async function copyAddress(target) {
  await navigator.clipboard.writeText(target.address)
  copiedId.value = target.id
  setTimeout(() => {
    if (copiedId.value === target.id) copiedId.value = null
  }, 1500)
}

async function fetchTargets() {
  const response = await fetch('http://127.0.0.1:8000/api/recon/targets/', {
    headers: { Authorization: `Token ${authToken.value}` },
  })
  targets.value = await response.json()
}

async function addTarget() {
  error.value = ''
  const response = await fetch('http://127.0.0.1:8000/api/recon/targets/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Token ${authToken.value}`,
    },
    body: JSON.stringify({
      name: newName.value,
      address: newAddress.value,
      notes: newNotes.value,
    }),
  })

  if (!response.ok) {
    error.value = "Impossible d'ajouter la cible."
    return
  }

  newName.value = ''
  newAddress.value = ''
  newNotes.value = ''
  await fetchTargets()
}

async function deleteTarget(id) {
  await fetch(`http://127.0.0.1:8000/api/recon/targets/${id}/`, {
    method: 'DELETE',
    headers: { Authorization: `Token ${authToken.value}` },
  })
  await fetchTargets()
}

onMounted(fetchTargets)
</script>

<template>
  <div class="targets">
    <div class="targets-head">
      <p class="eyebrow">Inventaire</p>
      <h2>Carnet de cibles</h2>
    </div>

    <form class="add-form card" @submit.prevent="addTarget">
      <div class="form-row">
        <input v-model="newName" type="text" placeholder="Nom (facultatif)" />
        <input v-model="newAddress" type="text" placeholder="Adresse (IP ou domaine)" required />
      </div>
      <textarea v-model="newNotes" placeholder="Notes (facultatif)" rows="3" class="notes-input"></textarea>
      <button type="submit">Ajouter</button>
    </form>

    <p v-if="error" class="error">{{ error }}</p>

    <ul class="target-list">
      <li v-for="target in targets" :key="target.id">
        <template v-if="editingId === target.id">
          <div class="edit-form">
            <div class="form-row">
              <input v-model="editName" type="text" placeholder="Nom (facultatif)" />
              <input v-model="editAddress" type="text" placeholder="Adresse (IP ou domaine)" required />
            </div>
            <textarea v-model="editNotes" placeholder="Notes (facultatif)" rows="3" class="notes-input"></textarea>
            <div class="edit-actions">
              <button type="button" class="save-btn" @click="saveEdit(target)">Enregistrer</button>
              <button type="button" class="cancel-btn" @click="cancelEdit">Annuler</button>
            </div>
          </div>
        </template>

        <template v-else>
          <div class="target-info">
            <strong>{{ target.name || target.address }}</strong>
            <span v-if="target.name" class="address-inline">
              <span class="address-text">— {{ target.address }}</span>
              <button type="button" class="copy-address-btn" @click="copyAddress(target)">
                {{ copiedId === target.id ? 'Copié !' : 'Copier' }}
              </button>
            </span>
            <span v-else class="address-inline">
              <button type="button" class="copy-address-btn" @click="copyAddress(target)">
                {{ copiedId === target.id ? 'Copié !' : 'Copier' }}
              </button>
            </span>
            <p v-if="target.notes" class="notes">{{ target.notes }}</p>
          </div>
          <div class="item-actions">
            <button class="edit-btn" @click="startEdit(target)">Modifier</button>
            <button class="delete-btn" @click="deleteTarget(target.id)">Supprimer</button>
          </div>
        </template>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.targets {
  max-width: 780px;
  margin: 0 auto;
}

.targets-head {
  text-align: center;
  margin-bottom: 28px;
}

h2 {
  margin: 6px 0 0;
  font-family: 'Playfair Display', Georgia, serif;
  font-size: 2.05rem;
  font-weight: 700;
  color: var(--text);
  text-shadow: 0 2px 30px rgba(124, 108, 245, 0.2);
}

.card {
  background: var(--glass-1);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  box-shadow: var(--shadow-2);
}

.add-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 18px;
  margin-bottom: 26px;
}

.form-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.add-form input,
.notes-input,
.edit-form input {
  padding: 10px 12px;
  background: var(--glass-1);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text);
  font-size: 0.88rem;
  transition: border-color 0.16s ease, box-shadow 0.16s ease, background 0.16s ease;
}

.add-form input {
  flex: 1;
  min-width: 140px;
}

.notes-input {
  width: 100%;
  resize: vertical;
  line-height: 1.55;
}

.add-form input::placeholder,
.notes-input::placeholder,
.edit-form input::placeholder {
  color: var(--text-faint);
}

.add-form input:focus,
.notes-input:focus,
.edit-form input:focus {
  outline: none;
  background: var(--glass-2);
  border-color: var(--accent-line);
  box-shadow: 0 0 0 3px var(--accent-soft);
}

.add-form button {
  align-self: flex-start;
  padding: 10px 20px;
  background: linear-gradient(135deg, var(--accent), #6355d6);
  color: #fff;
  border: 1px solid var(--accent-line);
  border-radius: var(--radius-sm);
  font-size: 0.87rem;
  font-weight: 500;
  cursor: pointer;
  box-shadow: 0 6px 22px rgba(124, 108, 245, 0.28);
  transition: filter 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease;
}

.add-form button:hover {
  filter: brightness(1.12);
  box-shadow: 0 8px 30px rgba(124, 108, 245, 0.42);
  transform: translateY(-1px);
}

.error {
  color: var(--danger);
  font-size: 0.87rem;
  margin-bottom: 14px;
}

.target-list {
  list-style: none;
  padding: 0;
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
}

.target-list li {
  min-width: 0;
  background: var(--glass-1);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 15px 17px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  box-shadow: var(--shadow-1);
  transition: background 0.16s ease, border-color 0.16s ease, box-shadow 0.16s ease, transform 0.16s ease;
}

.target-list li:hover {
  background: var(--glass-2);
  border-color: var(--accent-line);
  box-shadow: var(--shadow-2);
  transform: translateY(-2px);
}

.target-info {
  flex: 1;
  min-width: 0;
}

.target-info strong {
  color: var(--text);
  font-weight: 600;
  font-size: 0.94rem;
  overflow-wrap: break-word;
}

.notes {
  color: var(--text-muted);
  font-size: 0.83rem;
  margin: 6px 0 0;
  overflow-wrap: break-word;
}

.address-inline {
  display: inline-flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  min-width: 0;
  max-width: 100%;
  margin-left: 6px;
}

.address-text {
  min-width: 0;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.82rem;
  color: var(--text-muted);
  overflow-wrap: break-word;
}

.copy-address-btn {
  flex-shrink: 0;
  background: var(--glass-2);
  border: 1px solid var(--border);
  color: var(--text-muted);
  border-radius: 6px;
  padding: 2px 9px;
  font-size: 0.71rem;
  cursor: pointer;
  transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease;
}

.copy-address-btn:hover {
  background: var(--accent-soft);
  border-color: var(--accent-line);
  color: var(--accent);
}

.item-actions {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex-shrink: 0;
}

.edit-btn,
.delete-btn,
.cancel-btn {
  flex-shrink: 0;
  background: var(--glass-2);
  border: 1px solid var(--border);
  color: var(--text-muted);
  border-radius: 7px;
  padding: 6px 12px;
  font-size: 0.78rem;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease;
}

.edit-btn:hover,
.cancel-btn:hover {
  background: var(--accent-soft);
  border-color: var(--accent-line);
  color: var(--accent);
}

.delete-btn:hover {
  background: var(--danger-soft);
  border-color: var(--danger);
  color: var(--danger);
}

.edit-form {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.edit-form .form-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.edit-form input {
  flex: 1;
  min-width: 120px;
  padding: 8px 11px;
  font-size: 0.84rem;
}

.edit-actions {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

.save-btn {
  background: linear-gradient(135deg, var(--accent), #6355d6);
  color: #fff;
  border: 1px solid var(--accent-line);
  border-radius: 7px;
  padding: 7px 14px;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(124, 108, 245, 0.26);
  transition: filter 0.16s ease, box-shadow 0.16s ease;
}

.save-btn:hover {
  filter: brightness(1.12);
  box-shadow: 0 6px 22px rgba(124, 108, 245, 0.4);
}
</style>
