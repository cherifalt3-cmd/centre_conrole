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
    <h2>Carnet de cibles</h2>

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
  max-width: 720px;
  margin: 0 auto;
}

h2 {
  text-align: center;
  margin: 0 0 40px;
  font-family: 'Playfair Display', Georgia, serif;
  font-size: 2.1rem;
  font-weight: 700;
  color: #14201e;
}

.card {
  background: #fff;
  border: 1px solid #d7e0de;
  border-radius: 12px;
  box-shadow: 0 1px 2px rgba(20, 32, 30, 0.05), 0 6px 18px rgba(20, 32, 30, 0.05);
}

.add-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 16px;
  margin-bottom: 24px;
}

.form-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.add-form input {
  flex: 1;
  min-width: 140px;
  padding: 9px 11px;
  border: 1px solid #c3d0cd;
  border-radius: 8px;
  font-size: 0.9rem;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.notes-input {
  width: 100%;
  padding: 9px 11px;
  border: 1px solid #c3d0cd;
  border-radius: 8px;
  font-size: 0.9rem;
  box-sizing: border-box;
  resize: vertical;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.add-form input:focus,
.notes-input:focus {
  outline: none;
  border-color: #0f6d63;
  box-shadow: 0 0 0 3px rgba(15, 109, 99, 0.15);
}

.add-form button {
  padding: 9px 16px;
  background: #0f6d63;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s ease;
}

.add-form button:hover {
  background: #0a4f48;
}

.error {
  color: #a85a17;
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
  background: #fff;
  border: 1px solid #d7e0de;
  border-radius: 10px;
  padding: 14px 16px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  box-shadow: 0 1px 2px rgba(20, 32, 30, 0.04);
  transition: box-shadow 0.15s ease, border-color 0.15s ease;
}

.target-list li:hover {
  border-color: #c3d0cd;
  box-shadow: 0 4px 14px rgba(20, 32, 30, 0.06);
}

.target-info {
  flex: 1;
  min-width: 0;
}

.target-info strong {
  overflow-wrap: break-word;
}

.notes {
  color: #5b6b68;
  font-size: 0.88rem;
  margin: 4px 0 0;
  overflow-wrap: break-word;
}

.address-inline {
  display: inline-flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  min-width: 0;
  max-width: 100%;
}

.address-text {
  min-width: 0;
  overflow-wrap: break-word;
}

.copy-address-btn {
  flex-shrink: 0;
  background: none;
  border: 1px solid #c3d0cd;
  color: #0f6d63;
  border-radius: 6px;
  padding: 2px 8px;
  font-size: 0.74rem;
  cursor: pointer;
  transition: background 0.15s ease, border-color 0.15s ease;
}

.copy-address-btn:hover {
  background: #e5eff5;
  border-color: #0f6d63;
}

.item-actions {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex-shrink: 0;
}

.edit-btn {
  flex-shrink: 0;
  background: none;
  border: 1px solid #c3d0cd;
  color: #5b6b68;
  border-radius: 7px;
  padding: 5px 10px;
  font-size: 0.8rem;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.15s ease, border-color 0.15s ease;
}

.edit-btn:hover {
  background: #f6f9f8;
  border-color: #0f6d63;
  color: #0f6d63;
}

.delete-btn {
  flex-shrink: 0;
  background: none;
  border: 1px solid #a85a17;
  color: #a85a17;
  border-radius: 7px;
  padding: 5px 10px;
  font-size: 0.8rem;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.15s ease;
}

.delete-btn:hover {
  background: #f6ece0;
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
  padding: 7px 10px;
  border: 1px solid #c3d0cd;
  border-radius: 7px;
  font-size: 0.85rem;
}

.edit-form input:focus {
  outline: none;
  border-color: #0f6d63;
  box-shadow: 0 0 0 3px rgba(15, 109, 99, 0.15);
}

.edit-actions {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

.save-btn {
  background: #0f6d63;
  color: #fff;
  border: none;
  border-radius: 7px;
  padding: 7px 12px;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s ease;
}

.save-btn:hover {
  background: #0a4f48;
}

.cancel-btn {
  background: none;
  border: 1px solid #c3d0cd;
  color: #5b6b68;
  border-radius: 7px;
  padding: 7px 12px;
  font-size: 0.82rem;
  cursor: pointer;
  transition: background 0.15s ease;
}

.cancel-btn:hover {
  background: #f6f9f8;
}
</style>
