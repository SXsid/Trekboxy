<template>
  <div class="container-fluid px-4 py-4">

    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h3 class="mb-0 fw-bold">Admin Dashboard</h3>
        <p class="text-muted small mb-0">Welcome back. Here's what's happening.</p>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border" style="color:var(--orange)"></div>
    </div>

    <template v-else>
      <div class="row g-3 mb-4">
        <div class="col-sm-6 col-xl-3" v-for="stat in statCards" :key="stat.label">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body d-flex align-items-center gap-3 py-3">
              <div class="stat-icon">
                <i :class="stat.icon"></i>
              </div>
              <div>
                <div class="fs-3 fw-bold lh-1">{{ stat.value }}</div>
                <div class="text-muted small mt-1">{{ stat.label }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="row g-3">
        <div class="col-md-4" v-for="link in quickLinks" :key="link.to">
          <RouterLink :to="link.to" class="card text-decoration-none text-dark border-0 shadow-sm h-100 quick-card">
            <div class="card-body d-flex align-items-center gap-3">
              <div class="stat-icon"><i :class="link.icon"></i></div>
              <div>
                <h6 class="mb-0 fw-bold">{{ link.label }}</h6>
                <p class="small text-muted mb-0 mt-1">{{ link.desc }}</p>
              </div>
              <i class="bi bi-chevron-right ms-auto text-muted"></i>
            </div>
          </RouterLink>
        </div>
      </div>
    </template>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../api'

const stats   = ref(null)
const loading = ref(true)

const statCards = computed(() => {
  if (!stats.value) return []
  return [
    { label: 'Total Treks',    value: stats.value.total_treks,    icon: 'bi bi-map-fill' },
    { label: 'Open Treks',     value: stats.value.open_treks,     icon: 'bi bi-door-open-fill' },
    { label: 'Total Trekkers', value: stats.value.total_users,    icon: 'bi bi-people-fill' },
    { label: 'Total Bookings', value: stats.value.total_bookings, icon: 'bi bi-calendar-check-fill' },
  ]
})

const quickLinks = [
  { to: '/admin/treks',    label: 'Manage Treks',  icon: 'bi bi-map-fill',      desc: 'Create, edit, assign staff' },
  { to: '/admin/users',    label: 'Manage Users',  icon: 'bi bi-people-fill',   desc: 'View, activate or blacklist' },
  { to: '/admin/bookings', label: 'All Bookings',  icon: 'bi bi-journal-check', desc: 'View all booking records' },
]

onMounted(async () => {
  try {
    const { data } = await api.get('/api/admin/dashboard')
    stats.value = data.stats
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.quick-card { transition: transform 0.18s, box-shadow 0.18s; }
.quick-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(204,85,0,0.1) !important;
}
</style>
