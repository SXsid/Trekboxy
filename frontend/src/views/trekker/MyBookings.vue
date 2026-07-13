<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h3 class="mb-0"><i class="bi bi-calendar-check me-2"></i>My Bookings</h3>
      <button class="btn btn-outline-success btn-sm" @click="exportCSV" :disabled="exporting">
        <span v-if="exporting" class="spinner-border spinner-border-sm me-1"></span>
        <i v-else class="bi bi-download me-1"></i>
        {{ exporting ? 'Exporting...' : 'Export CSV' }}
      </button>
    </div>

    <div v-if="exportMsg" :class="`alert alert-${exportMsg.type} py-2`">{{ exportMsg.text }}</div>

    <div v-if="loading" class="text-center py-5"><div class="spinner-border text-success"></div></div>

    <div v-else-if="bookings.length === 0" class="alert alert-info">
      No bookings yet. <RouterLink to="/treks">Browse treks</RouterLink>
    </div>

    <div v-else class="row g-3">
      <div class="col-md-6" v-for="b in bookings" :key="b.id">
        <div class="card shadow-sm h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between mb-2">
              <h5 class="card-title mb-0">{{ b.trek?.name || 'Trek' }}</h5>
              <span :class="statusClass(b.status)">{{ b.status }}</span>
            </div>
            <p class="text-muted small mb-1"><i class="bi bi-geo-alt me-1"></i>{{ b.trek?.location }}</p>
            <p class="text-muted small mb-1">
              <i class="bi bi-calendar-range me-1"></i>
              {{ b.trek?.start_date }} → {{ b.trek?.end_date }}
            </p>
            <p class="text-muted small mb-2">
              <i class="bi bi-tag me-1"></i>Trek status:
              <span class="fw-semibold">{{ b.trek?.status }}</span>
            </p>
            <p class="text-muted small">
              Booked on {{ new Date(b.booking_date).toLocaleDateString() }}
            </p>

            <button
              v-if="b.status === 'Booked'"
              class="btn btn-outline-danger btn-sm"
              @click="cancelBooking(b)"
            >Cancel</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'

const bookings  = ref([])
const loading   = ref(true)
const exporting = ref(false)
const exportMsg = ref(null)

async function fetchBookings() {
  const { data } = await api.get('/api/bookings/')
  bookings.value = data.bookings
  loading.value  = false
}

async function cancelBooking(booking) {
  if (!confirm('Cancel this booking?')) return
  await api.put(`/api/bookings/${booking.id}/cancel`)
  booking.status = 'Cancelled'  // optimistic update
}

async function exportCSV() {
  exporting.value = true
  exportMsg.value = null
  try {
    const { data } = await api.get('/api/bookings/export')
    exportMsg.value = {
      type: 'success',
      text: data.message + ' Check your email!'
    }
  } catch (err) {
    exportMsg.value = {
      type: 'warning',
      text: err.response?.data?.message || 'Export already queued'
    }
  } finally {
    exporting.value = false
  }
}

function statusClass(s) {
  return { Booked: 'badge bg-success', Cancelled: 'badge bg-danger', Completed: 'badge bg-dark' }[s] || 'badge bg-secondary'
}

onMounted(fetchBookings)
</script>
