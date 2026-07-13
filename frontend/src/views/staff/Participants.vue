<template>
  <div class="container py-4">
    <div class="d-flex align-items-center gap-2 mb-4">
      <RouterLink to="/staff" class="btn btn-sm btn-outline-secondary">
        <i class="bi bi-arrow-left"></i>
      </RouterLink>
      <h3 class="mb-0">Participants — {{ trekName }}</h3>
    </div>

    <div v-if="loading" class="text-center py-5"><div class="spinner-border text-success"></div></div>

    <div v-else>
      <p class="text-muted">{{ participants.length }} registered participant(s)</p>
      <div class="table-responsive">
        <table class="table table-hover align-middle">
          <thead class="table-dark">
            <tr><th>#</th><th>Username</th><th>Full Name</th><th>Email</th><th>Booking Status</th><th>Booked On</th></tr>
          </thead>
          <tbody>
            <tr v-for="(p, i) in participants" :key="p.id">
              <td>{{ i + 1 }}</td>
              <td>{{ p.user?.username || '—' }}</td>
              <td>{{ p.user?.full_name || '—' }}</td>
              <td>{{ p.user?.email || '—' }}</td>
              <td><span class="badge bg-success">{{ p.status }}</span></td>
              <td>{{ new Date(p.booking_date).toLocaleDateString() }}</td>
            </tr>
            <tr v-if="participants.length === 0">
              <td colspan="6" class="text-center text-muted py-4">No participants yet</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../api'

const route = useRoute()
const trekId = route.params.id

const participants = ref([])
const trekName     = ref('')
const loading      = ref(true)

onMounted(async () => {
  const { data } = await api.get(`/api/staff/treks/${trekId}/participants`)
  participants.value = data.participants
  trekName.value     = data.trek?.name || `Trek #${trekId}`
  loading.value      = false
})
</script>
