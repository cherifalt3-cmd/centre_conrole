<script setup>
import { ref, onMounted } from 'vue'
import { authToken } from '../auth'

const targets = ref([])
const newName = ref('')
const newAddress = ref('')
const newNotes = ref('')
const error = ref('')

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

    <form class="add-form" @submit.prevent="addTarget">
      <input v-model="newName" type="text" placeholder="Nom (facultatif)" />
      <input v-model="newAddress" type="text" placeholder="Adresse (IP ou domaine)" required />
      <input v-model="newNotes" type="text" placeholder="Notes (facultatif)" />
      <button type="submit">Ajouter</button>
    </form>

    <p v-if="error" class="error">{{ error }}</p>

    <ul class="target-list">
      <li v-for="target in targets" :key="target.id">
        <div>
          <strong>{{ target.name || target.address }}</strong>
          <span v-if="target.name"> — {{ target.address }}</span>
          <p v-if="target.notes" class="notes">{{ target.notes }}</p>
        </div>
        <button class="delete-btn" @click="deleteTarget(target.id)">Supprimer</button>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.targets {
  max-width: 640px;
  margin: 0 auto;
}

h2 {
  margin: 0 0 20px;
  color: #14201e;
}

.add-form {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 24px;
}

.add-form input {
  flex: 1;
  min-width: 140px;
  padding: 9px 11px;
  border: 1px solid #c3d0cd;
  border-radius: 8px;
  font-size: 0.9rem;
}

.add-form button {
  padding: 9px 16px;
  background: #0f6d63;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
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
  gap: 10px;
}

.target-list li {
  background: #fff;
  border: 1px solid #d7e0de;
  border-radius: 10px;
  padding: 14px 16px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.notes {
  color: #5b6b68;
  font-size: 0.88rem;
  margin: 4px 0 0;
}

.delete-btn {
  background: none;
  border: 1px solid #a85a17;
  color: #a85a17;
  border-radius: 7px;
  padding: 5px 10px;
  font-size: 0.8rem;
  cursor: pointer;
  white-space: nowrap;
}

.delete-btn:hover {
  background: #f6ece0;
}
</style>
