<template>
  <nav v-if="auth.isLoggedIn" class="navbar navbar-expand-lg navbar-himtrek">
    <div class="container">
      <RouterLink class="navbar-brand d-flex align-items-center gap-2 " to="/">
        <i class="bi bi-compass-fill" style="color: var(--orange); font-size:1.5rem"></i>
        HimTrek
      </RouterLink>

      <button class="navbar-toggler border-0" type="button" data-bs-toggle="collapse" data-bs-target="#navMenu">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navMenu">
        <ul class="navbar-nav me-auto ms-4 gap-4">

          <template v-if="auth.role === 'admin'">
            <li class="nav-item"><RouterLink class="nav-link" to="/admin">Dashboard</RouterLink></li>
            <li class="nav-item"><RouterLink class="nav-link" to="/admin/treks">Treks</RouterLink></li>
            <li class="nav-item"><RouterLink class="nav-link" to="/admin/users">Users</RouterLink></li>
            <li class="nav-item"><RouterLink class="nav-link" to="/admin/bookings">Bookings</RouterLink></li>
          </template>

          <template v-if="auth.role === 'staff'">
            <li class="nav-item"><RouterLink class="nav-link" to="/staff">My Treks</RouterLink></li>
          </template>

          <template v-if="auth.role === 'trekker'">
            <li class="nav-item"><RouterLink class="nav-link" to="/treks">Browse Treks</RouterLink></li>
            <li class="nav-item"><RouterLink class="nav-link" to="/bookings">My Bookings</RouterLink></li>
          </template>

        </ul>

        <ul class="navbar-nav ms-auto align-items-center gap-2">
          <li class="nav-item">
            <span class="nav-link text-muted small">
              <i class="bi bi-person-circle me-1"></i>
              {{ auth.user?.username }}
            </span>
          </li>
          <li v-if="auth.role === 'trekker'" class="nav-item">
            <RouterLink class="nav-link" to="/profile">
              <i class="bi bi-gear me-1"></i>Profile
            </RouterLink>
          </li>
          <li class="nav-item">
            <button class="btn btn-sm btn-success px-3" @click="handleLogout">
              <i class="bi bi-box-arrow-right me-1"></i>Logout
            </button>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from '../store/auth'
import { useRouter } from 'vue-router'

const auth   = useAuthStore()
const router = useRouter()

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>
