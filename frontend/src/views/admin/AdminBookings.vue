<template>
  <div class="container py-4">
    <h3 class="mb-4"><i class="bi bi-journal-check me-2"></i>All Bookings</h3>

    <div class="d-flex gap-2 mb-3 flex-wrap">
      <select v-model="statusFilter" class="form-select" style="max-width:160px" @change="fetchBookings">
        <option value="">All Statuses</option>
        <option>Booked</option><option>Cancelled</option><option>Completed</option>
      </select>
    </div>

    <div v-if="loading" class="text-center py-5"><div class="spinner-border text-success"></div></div>

    <div v-else class="table-responsive">
      <table class="table table-hover align-middle small">
        <thead class="table-dark">
          <tr>
            <th>Booking ID</th><th>Trekker</th><th>Trek</th>
            <th>Status</th><th>Payment</th><th>Booked On</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="b in bookings" :key="b.id">
            <td>{{ b.id }})</td>
            <td>{{ b.user?.username || b.user_id }}</td>
            <td>{{ b.trek?.name || b.trek_id }}</td>
            <td>
              <span :class="statusClass(b.status)">{{ b.status }}</span>
            </td>
            <td>{{ b.payment_status }}</td>
            <td>{{ new Date(b.booking_date).toLocaleDateString() }}</td>
          </tr>
          <tr v-if="bookings.length === 0">
            <td colspan="6" class="text-center text-muted py-4">No bookings found</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'

const bookings     = ref([])
const loading      = ref(true)
const statusFilter = ref('')

async function fetchBookings() {
  loading.value = true
  const { data } = await api.get('/api/admin/bookings', {
    params: { status: statusFilter.value || undefined }
  })
  bookings.value = data.bookings
  loading.value  = false
}

function statusClass(s) {
  const map = { Booked: 'badge bg-success', Cancelled: 'badge bg-danger', Completed: 'badge bg-dark' }
  return map[s] || 'badge bg-secondary'
}

onMounted(fetchBookings)
</script>
