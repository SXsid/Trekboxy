<template>
  <div class="auth-wrapper">
    <div class="auth-hero d-none d-md-block">
      <div class="auth-hero-overlay">
        <h1><i class="bi bi-compass-fill me-2"></i>HimTrek</h1>
        <p class="mb-0">Your gateway to the Himalayas.<br/>Discover, book, and conquer.</p>
      </div>
    </div>

    <div class="auth-form-panel">
      <div style="width: 100%; max-width: 360px">


        <h4 class="fw-bold mb-1">Welcome back</h4>
        <p class="text-muted small mb-4">Sign in to your account</p>

        <div v-if="error" class="alert alert-danger py-2 small">{{ error }}</div>

        <form @submit.prevent="handleLogin">
          <div class="mb-3">
            <label class="form-label fw-semibold small">Email</label>
            <input v-model="form.email" type="email" class="form-control" placeholder="you@example.com" required />
          </div>
          <div class="mb-4">
            <label class="form-label fw-semibold small">Password</label>
            <input v-model="form.password" type="password" class="form-control" placeholder="••••••••" required />
          </div>

          <button type="submit" class="btn btn-success w-100 py-2 fw-semibold" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            {{ loading ? 'Signing in...' : 'Sign In' }}
          </button>
        </form>

        <hr class="my-4" />
        <p class="text-center text-muted small mb-0">
          New trekker?
          <RouterLink to="/register" style="color:var(--orange); text-decoration:none; font-weight:600">
            Create account
          </RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'
import api from '../api'

const router  = useRouter()
const auth    = useAuthStore()
const form    = reactive({ email: '', password: '' })
const loading = ref(false)
const error   = ref('')

async function handleLogin() {
  loading.value = true
  error.value   = ''
  try {
    const { data } = await api.post('/api/auth/login', form)
    auth.login(data.access_token, data.user)
    if (data.user.role === 'admin')      router.push('/admin')
    else if (data.user.role === 'staff') router.push('/staff')
    else                                 router.push('/treks')
  } catch (err) {
    error.value = err.response?.data?.error || 'Login failed'
  } finally {
    loading.value = false
  }
}
</script>
