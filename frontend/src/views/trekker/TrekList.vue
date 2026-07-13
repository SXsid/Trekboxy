<template>
  <div class="container py-4">
    <h3 class="mb-4"><i class="bi bi-compass me-2"></i>Available Treks</h3>

    <!-- Search + Filters -->
    <div class="row g-2 mb-4">
      <div class="col-sm-4">
        <input v-model="filters.location" class="form-control" placeholder="Search location..." @input="fetchTreks" />
      </div>
      <div class="col-sm-3">
        <select v-model="filters.difficulty" class="form-select" @change="fetchTreks">
          <option value="">All Difficulties</option>
          <option>Easy</option><option>Moderate</option><option>Hard</option>
        </select>
      </div>
      <div class="col-sm-3">
        <input v-model.number="filters.duration" type="number" min="1" class="form-control"
               placeholder="Duration (days)" @input="fetchTreks" />
      </div>
      <div class="col-sm-2">
        <button class="btn btn-outline-secondary w-100" @click="clearFilters">Clear</button>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5"><div class="spinner-border text-success"></div></div>

    <div v-else-if="treks.length === 0" class="alert alert-info">
      No treks available right now. Check back later!
    </div>

    <div v-else class="row g-3">
      <div class="col-md-6 col-lg-4" v-for="trek in treks" :key="trek.id">
        <div class="card h-100 shadow-sm trek-card">
          <div class="card-body d-flex flex-column">
            <div class="d-flex justify-content-between mb-2">
              <h5 class="card-title mb-0">{{ trek.name }}</h5>
              <span :class="diffBadge(trek.difficulty)" class="badge">{{ trek.difficulty }}</span>
            </div>
            <p class="text-muted small mb-1"><i class="bi bi-geo-alt me-1"></i>{{ trek.location }}</p>
            <p class="text-muted small mb-1"><i class="bi bi-clock me-1"></i>{{ trek.duration_days }} days</p>
            <p class="text-muted small mb-1">
              <i class="bi bi-calendar-range me-1"></i>{{ trek.start_date }} → {{ trek.end_date }}
            </p>
            <p class="text-muted small mb-2">
              <i class="bi bi-people me-1"></i>{{ trek.available_slots }} slots left
            </p>
            <div class="mt-auto d-flex justify-content-between align-items-center">
              <span class="fw-bold" style="color:var(--orange)">₹{{ trek.price || 'Free' }}</span>
              <button class="btn btn-success btn-sm px-3"
                @click="bookTrek(trek)"
                :disabled="trek.available_slots === 0 || bookingId === trek.id">
                <span v-if="bookingId === trek.id" class="spinner-border spinner-border-sm me-1"></span>
                {{ trek.available_slots === 0 ? 'Full' : 'Book Now' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast notification -->
    <div v-if="toast.show" class="position-fixed bottom-0 end-0 p-3" style="z-index:9999">
      <div :class="`toast show align-items-center text-white border-0 bg-${toast.type}`">
        <div class="d-flex">
          <div class="toast-body">{{ toast.message }}</div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" @click="toast.show=false"></button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '../../api'

const treks     = ref([])
const loading   = ref(true)
const bookingId = ref(null)  // which trek is being booked right now (for spinner)
const filters   = reactive({ location: '', difficulty: '', duration: '' })
const toast     = reactive({ show: false, message: '', type: 'success' })

async function fetchTreks() {
  loading.value = true
  const params = {}
  if (filters.location)   params.location   = filters.location
  if (filters.difficulty) params.difficulty  = filters.difficulty
  if (filters.duration)   params.duration    = filters.duration

  const endpoint = Object.keys(params).length ? '/api/treks/search' : '/api/treks/'
  const { data } = await api.get(endpoint, { params })
  treks.value   = data.treks
  loading.value = false
}

async function bookTrek(trek) {
  bookingId.value = trek.id
  try {
    await api.post('/api/bookings/', { trek_id: trek.id })
    showToast('Trek booked successfully! 🎉', 'success')
  } catch (err) {
    showToast(err.response?.data?.error || 'Booking failed', 'danger')
  } finally {
    bookingId.value = null
  }
}

function clearFilters() {
  Object.assign(filters, { location: '', difficulty: '', duration: '' })
  fetchTreks()
}

function showToast(message, type = 'success') {
  Object.assign(toast, { show: true, message, type })
  setTimeout(() => { toast.show = false }, 3000)
}

function diffBadge(d) {
  return { 'badge': true, 'bg-success': d === 'Easy', 'bg-warning text-dark': d === 'Moderate', 'bg-danger': d === 'Hard' }
}

onMounted(fetchTreks)
</script>
