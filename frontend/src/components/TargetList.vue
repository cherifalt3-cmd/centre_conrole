<script setup>
import { ref, onMounted } from 'vue'
import { apiFetch } from '../api'

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

// Le serveur explique le refus (ex : cible deja presente) : on affiche son message
// plutot qu'un texte generique qui ne dirait pas pourquoi.
async function serverError(response, fallback) {
  try {
    const data = await response.json()
    return data.address?.[0] || fallback
  } catch {
    return fallback
  }
}

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
  const response = await apiFetch(`/api/recon/targets/${target.id}/`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: editName.value,
      address: editAddress.value,
      notes: editNotes.value,
    }),
  })

  if (!response.ok) {
    error.value = await serverError(response, 'Impossible de modifier la cible.')
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
  try {
    const response = await apiFetch('/api/recon/targets/')
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    targets.value = await response.json()
  } catch {
    error.value = 'Impossible de charger le carnet.'
  }
}

async function addTarget() {
  error.value = ''
  const response = await apiFetch('/api/recon/targets/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: newName.value,
      address: newAddress.value,
      notes: newNotes.value,
    }),
  })

  if (!response.ok) {
    error.value = await serverError(response, "Impossible d'ajouter la cible.")
    return
  }

  newName.value = ''
  newAddress.value = ''
  newNotes.value = ''
  await fetchTargets()
}

// Suppression en deux temps, comme dans le Kanban : le premier clic transforme
// le bouton en « Confirmer ? » pendant quelques secondes.
const pendingDeleteId = ref(null)
let pendingDeleteTimer = null

async function requestDelete(target) {
  if (pendingDeleteId.value !== target.id) {
    clearTimeout(pendingDeleteTimer)
    pendingDeleteId.value = target.id
    pendingDeleteTimer = setTimeout(() => (pendingDeleteId.value = null), 4000)
    return
  }

  clearTimeout(pendingDeleteTimer)
  pendingDeleteId.value = null
  error.value = ''
  const response = await apiFetch(`/api/recon/targets/${target.id}/`, { method: 'DELETE' })
  if (!response.ok) error.value = "La cible n'a pas pu être supprimée."
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
        <label class="field">
          <span class="field-label">Nom <span class="field-optional">facultatif</span></span>
          <input v-model="newName" type="text" placeholder="Ex : Serveur de recette" />
        </label>
        <label class="field">
          <span class="field-label">Adresse</span>
          <input v-model="newAddress" type="text" placeholder="IP, domaine ou URL" required />
        </label>
      </div>
      <label class="field">
        <span class="field-label">Notes <span class="field-optional">facultatif</span></span>
        <textarea v-model="newNotes" rows="3" class="notes-input"></textarea>
      </label>
      <button type="submit">Ajouter</button>
    </form>

    <p v-if="error" class="error" role="alert">{{ error }}</p>

    <ul class="target-list">
      <li v-for="target in targets" :key="target.id">
        <template v-if="editingId === target.id">
          <div class="edit-form">
            <div class="form-row">
              <label class="field">
                <span class="field-label">Nom <span class="field-optional">facultatif</span></span>
                <input v-model="editName" type="text" />
              </label>
              <label class="field">
                <span class="field-label">Adresse</span>
                <input v-model="editAddress" type="text" required />
              </label>
            </div>
            <label class="field">
              <span class="field-label">Notes <span class="field-optional">facultatif</span></span>
              <textarea v-model="editNotes" rows="3" class="notes-input"></textarea>
            </label>
            <div class="edit-actions">
              <button type="button" class="save-btn" @click="saveEdit(target)">Enregistrer</button>
              <button type="button" class="cancel-btn" @click="cancelEdit">Annuler</button>
            </div>
          </div>
        </template>

        <template v-else>
          <div class="target-info">
            <strong>{{ target.name || target.address }}</strong>
            <span class="address-inline">
              <span v-if="target.name" class="address-text">— {{ target.address }}</span>
              <button
                type="button"
                class="copy-address-btn"
                :aria-label="`Copier l'adresse ${target.address}`"
                @click="copyAddress(target)"
              >
                {{ copiedId === target.id ? 'Copié !' : 'Copier' }}
              </button>
            </span>
            <p v-if="target.notes" class="notes">{{ target.notes }}</p>
          </div>
          <div class="item-actions">
            <button type="button" class="edit-btn" @click="startEdit(target)">Modifier</button>
            <button
              type="button"
              :class="['delete-btn', { armed: pendingDeleteId === target.id }]"
              :aria-label="
                pendingDeleteId === target.id
                  ? `Confirmer la suppression de ${target.name || target.address}`
                  : `Supprimer ${target.name || target.address}`
              "
              @click="requestDelete(target)"
            >
              {{ pendingDeleteId === target.id ? 'Confirmer ?' : 'Supprimer' }}
            </button>
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
  margin-bottom: 32px;
}

h2 {
  margin: 6px 0 0;
  font-family: 'Playfair Display', Georgia, serif;
  font-size: var(--fs-3xl);
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
  padding: 20px;
  margin-bottom: 24px;
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
  border: 1px solid var(--border-input);
  border-radius: var(--radius-sm);
  color: var(--text);
  font-size: var(--fs-base);
  transition: border-color 0.16s ease, box-shadow 0.16s ease, background 0.16s ease;
}

/* Chaque champ est enveloppe dans son libelle : c'est le libelle qui occupe la
   place dans la ligne, et le champ prend toute sa largeur */
.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
  min-width: 140px;
}

.field-label {
  font-size: var(--fs-xs);
  font-weight: 500;
  color: var(--text-muted);
}

.field-optional {
  font-weight: 400;
  color: var(--text-faint);
}

.field-optional::before {
  content: '· ';
}

.add-form input,
.edit-form input {
  width: 100%;
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
  background: var(--glass-2);
  border-color: var(--accent);
}

.add-form button {
  align-self: flex-start;
  padding: 10px 20px;
  background: linear-gradient(135deg, var(--accent-strong), #6355d6);
  color: #fff;
  border: 1px solid var(--accent-line);
  border-radius: var(--radius-sm);
  font-size: var(--fs-base);
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
  font-size: var(--fs-base);
  margin-bottom: 16px;
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
  padding: 16px 16px;
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
  font-size: var(--fs-md);
  overflow-wrap: break-word;
}

.notes {
  color: var(--text-muted);
  font-size: var(--fs-sm);
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
  font-size: var(--fs-sm);
  color: var(--text-muted);
  overflow-wrap: break-word;
}

/* min-height 28px : il ne faisait que 18px, sous le minimum WCAG 2.5.8 (24px) */
.copy-address-btn {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  background: var(--glass-2);
  border: 1px solid var(--border);
  color: var(--text-muted);
  border-radius: 6px;
  padding: 2px 10px;
  font-size: var(--fs-xs);
  cursor: pointer;
  transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease;
}

.copy-address-btn:hover {
  background: var(--accent-soft);
  border-color: var(--accent-line);
  color: var(--text);
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
  font-size: var(--fs-xs);
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease;
}

.edit-btn:hover,
.cancel-btn:hover {
  background: var(--accent-soft);
  border-color: var(--accent-line);
  color: var(--text);
}

.delete-btn:hover {
  background: var(--danger-soft);
  border-color: var(--danger);
  color: var(--danger);
}

/* L'etat arme est plein : une action irreversible doit se distinguer nettement
   d'un simple survol, et un rouge sur fond rougi n'atteignait que 4,08:1 */
.delete-btn.armed {
  background: var(--danger-strong);
  border-color: var(--danger-strong);
  color: #fff;
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
  padding: 8px 12px;
  font-size: var(--fs-sm);
}

.edit-actions {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

.save-btn {
  background: linear-gradient(135deg, var(--accent-strong), #6355d6);
  color: #fff;
  border: 1px solid var(--accent-line);
  border-radius: 7px;
  padding: 8px 16px;
  font-size: var(--fs-sm);
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
