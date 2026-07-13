<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h3 class="mb-0"><i class="bi bi-map me-2"></i>Manage Treks</h3>
      <button class="btn btn-success" @click="openCreate">
        <i class="bi bi-plus-lg me-1"></i>New Trek
      </button>
    </div>

    <div class="input-group mb-3" style="max-width: 400px">
      <input v-model="search" class="form-control" placeholder="Search treks..." @input="fetchTreks" />
      <span class="input-group-text"><i class="bi bi-search"></i></span>
    </div>

    <div v-if="loading" class="text-center py-5"><div class="spinner-border text-success"></div></div>

    <div v-else class="table-responsive">
      <table class="table table-hover align-middle">
        <thead class="table-dark">
          <tr>
            <th>Name</th><th>Location</th><th>Difficulty</th>
            <th>Slots</th><th>Status</th><th>Staff_ID</th><th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="trek in treks" :key="trek.id">
            <td>{{ trek.name }}</td>
            <td>{{ trek.location }}</td>
            <td>
              <span :class="difficultyBadge(trek.difficulty)">{{ trek.difficulty }}</span>
            </td>
            <td>{{ trek.available_slots }} / {{ trek.total_slots }}</td>
            <td>
              <span :class="statusBadge(trek.status)">{{ trek.status }}</span>
            </td>
            <td>{{ trek.assigned_staff_id || '—' }}</td>
            <td>
              <button class="btn btn-sm btn-outline-primary me-1" @click="openEdit(trek)">Edit</button>
              <button class="btn btn-sm btn-outline-secondary me-1" @click="openAssign(trek)">Assign</button>
              <button class="btn btn-sm btn-outline-danger" @click="deleteTrek(trek.id)">Delete</button>
            </td>
          </tr>
          <tr v-if="treks.length === 0">
            <td colspan="7" class="text-center text-muted py-4">No treks found</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showForm" class="modal d-block" style="background:rgba(0,0,0,0.5)">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ editingTrek ? 'Edit Trek' : 'Create Trek' }}</h5>
            <button type="button" class="btn-close" @click="closeForm"></button>
          </div>
          <div class="modal-body">
            <div v-if="formError" class="alert alert-danger py-2">{{ formError }}</div>
            <form @submit.prevent="saveTrek" id="trekForm">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label">Trek Name *</label>
                  <input v-model="form.name" class="form-control" required />
                </div>
                <div class="col-md-6">
                  <label class="form-label">Location *</label>
                  <input v-model="form.location" class="form-control" required />
                </div>
                <div class="col-md-4">
                  <label class="form-label">Difficulty *</label>
                  <select v-model="form.difficulty" class="form-select" required>
                    <option>Easy</option><option>Moderate</option><option>Hard</option>
                  </select>
                </div>
                <div class="col-md-4">
                  <label class="form-label">Duration (days) *</label>
                  <input v-model.number="form.duration_days" type="number" min="1" class="form-control" required />
                </div>
                <div class="col-md-4">
                  <label class="form-label">Total Slots *</label>
                  <input v-model.number="form.total_slots" type="number" min="1" class="form-control" required />
                </div>
                <div class="col-md-4">
                  <label class="form-label">Start Date *</label>
                  <input v-model="form.start_date" type="date" class="form-control" required />
                </div>
                <div class="col-md-4">
                  <label class="form-label">End Date *</label>
                  <input v-model="form.end_date" type="date" class="form-control" required />
                </div>
                <div class="col-md-4">
                  <label class="form-label">Registration Deadline *</label>
                  <input v-model="form.registration_deadline" type="date" class="form-control" />
                </div>
                <div class="col-md-4">
                  <label class="form-label">Price (₹)</label>
                  <input v-model.number="form.price" type="number" min="0" class="form-control" />
                </div>
                <div v-if="editingTrek" class="col-md-4">
                  <label class="form-label">Status</label>
                  <select v-model="form.status" class="form-select">
                    <option>Pending</option><option>Approved</option>
                    <option>Open</option><option>Closed</option><option>Completed</option>
                  </select>
                </div>
                <div class="col-12">
                  <label class="form-label">Description</label>
                  <textarea v-model="form.description" class="form-control" rows="2"></textarea>
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="closeForm">Cancel</button>
            <button class="btn btn-success" form="trekForm" type="submit" :disabled="saving">
              <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
              {{ editingTrek ? 'Update' : 'Create' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showAssign" class="modal d-block" style="background:rgba(0,0,0,0.5)">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Assign Staff to {{ assigningTrek?.name }}</h5>
            <button class="btn-close" @click="showAssign = false"></button>
          </div>
          <div class="modal-body">
            <div v-if="staffList.length === 0" class="text-muted">No staff found. Create staff first.</div>
            <div v-for="s in staffList" :key="s.id" class="form-check mb-2">
              <input class="form-check-input" type="radio" :value="s.id" v-model="selectedStaffId" :id="`staff-${s.id}`" />
              <label class="form-check-label" :for="`staff-${s.id}`">
                {{ s.username }} — {{ s.full_name || s.email }}
              </label>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showAssign = false">Cancel</button>
            <button class="btn btn-success" @click="assignStaff" :disabled="!selectedStaffId">Assign</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '../../api'

const treks   = ref([])
const loading = ref(true)
const search  = ref('')

const showForm    = ref(false)
const editingTrek = ref(null)
const saving      = ref(false)
const formError   = ref('')
const form = reactive({
  name: '', location: '', difficulty: 'Easy', duration_days: 1,
  total_slots: 10, start_date: '', end_date: '', price: 0,registration_deadline:'',
  description: '', status: 'Pending'
})

const showAssign     = ref(false)
const assigningTrek  = ref(null)
const staffList      = ref([])
const selectedStaffId = ref(null)

async function fetchTreks() {
  loading.value = true
  const { data } = await api.get('/api/admin/treks', { params: { search: search.value } })
  treks.value   = data.treks
  loading.value = false
}

function openCreate() {
  editingTrek.value = null
  Object.assign(form, { name: '', location: '', difficulty: 'Easy', duration_days: 1,
    total_slots: 10, start_date: '', end_date: '', price: 0, description: '', status: 'Pending' ,registration_deadline:''})
  showForm.value = true
}

function openEdit(trek) {
  editingTrek.value = trek
  Object.assign(form, {
    name: trek.name, location: trek.location, difficulty: trek.difficulty,
    duration_days: trek.duration_days, total_slots: trek.total_slots,
    start_date: trek.start_date, end_date: trek.end_date,
    price: trek.price, description: trek.description, status: trek.status,
    registration_deadline:trek.registration_deadline
  })
  showForm.value = true
}

function closeForm() { showForm.value = false; formError.value = '' }

async function saveTrek() {
  saving.value = true; formError.value = ''
  try {
    if (editingTrek.value) {
      await api.put(`/api/treks/${editingTrek.value.id}`, form)
    } else {
      await api.post('/api/treks/', form)
    }
    closeForm(); await fetchTreks()
  } catch (err) {
    formError.value = err.response?.data?.error || 'Failed to save trek'
  } finally {
    saving.value = false
  }
}

async function deleteTrek(id) {
  if (!confirm('Delete this trek?')) return
  await api.delete(`/api/treks/${id}`)
  await fetchTreks()
}

async function openAssign(trek) {
  assigningTrek.value  = trek
  selectedStaffId.value = trek.assigned_staff_id
  const { data } = await api.get('/api/admin/users', { params: { role: 'staff' } })
  staffList.value = data.users.filter(u => u.is_active)
  showAssign.value = true
}

async function assignStaff() {
  await api.post(`/api/treks/${assigningTrek.value.id}/assign`, { staff_id: selectedStaffId.value })
  showAssign.value = false
  await fetchTreks()
}

function difficultyBadge(d) {
  return { 'badge': true, 'bg-success': d === 'Easy', 'bg-warning text-dark': d === 'Moderate', 'bg-danger': d === 'Hard' }
}
function statusBadge(s) {
  const map = { Open: 'bg-success', Closed: 'bg-secondary', Completed: 'bg-dark',
                Pending: 'bg-warning text-dark', Approved: 'bg-info text-dark' }
  return `badge ${map[s] || 'bg-secondary'}`
}

onMounted(fetchTreks)
</script>
