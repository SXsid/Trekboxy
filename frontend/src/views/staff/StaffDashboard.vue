<template>
  <div class="container py-4">
    <h3 class="mb-4"><i class="bi bi-person-badge me-2"></i>My Assigned Treks</h3>

    <div v-if="loading" class="text-center py-5"><div class="spinner-border text-success"></div></div>

    <div v-else-if="treks.length === 0" class="alert alert-info">
      No treks assigned to you yet. Contact admin.
    </div>

    <div v-else class="row g-3">
      <div class="col-md-6 col-lg-4" v-for="trek in treks" :key="trek.id">
        <div class="card h-100 shadow-sm">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-2">
              <h5 class="card-title mb-0">{{ trek.name }}</h5>
              <span :class="statusBadge(trek.status)">{{ trek.status }}</span>
            </div>
            <p class="text-muted small mb-1"><i class="bi bi-geo-alt me-1"></i>{{ trek.location }}</p>
            <p class="text-muted small mb-2"><i class="bi bi-people me-1"></i>{{ trek.booking_count }} / {{ trek.total_slots }} registered</p>

            <div class="mb-2">
              <label class="form-label small mb-1">Update Status</label>
              <div class="d-flex gap-2">
                <select v-model="trek._newStatus" class="form-select form-select-sm">
                  <option value="Open">Open</option>
                  <option value="Closed">Closed</option>
                  <option value="Completed">Completed</option>
                </select>
                <button class="btn btn-sm btn-outline-success" @click="updateStatus(trek)">Save</button>
              </div>
            </div>

            <RouterLink :to="`/staff/treks/${trek.id}/participants`" class="btn btn-sm btn-outline-primary w-100">
              <i class="bi bi-people-fill me-1"></i>View Participants
            </RouterLink>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'

const treks   = ref([])
const loading = ref(true)

async function fetchTreks() {
  const { data } = await api.get('/api/staff/treks')
  treks.value = data.treks.map(t => ({ ...t, _newStatus: t.status }))
  loading.value = false
}

async function updateStatus(trek) {
  await api.put(`/api/staff/treks/${trek.id}`, { status: trek._newStatus })
  trek.status = trek._newStatus  
}

function statusBadge(s) {
  const map = { Open: 'badge bg-success', Closed: 'badge bg-secondary',
                Completed: 'badge bg-dark', Pending: 'badge bg-warning text-dark', Approved: 'badge bg-info text-dark' }
  return map[s] || 'badge bg-secondary'
}

onMounted(fetchTreks)
</script>
