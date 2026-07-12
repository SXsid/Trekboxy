<template>
  <div class="auth-wrapper">
    <div class="auth-hero d-none d-md-block">
      <div class="auth-hero-overlay">
        <h1><i class="bi bi-compass-fill me-2"></i>HimTrek</h1>
        <p class="mb-0">Join thousands of trekkers exploring the Himalayas.<br/>Create your account for free.</p>
      </div>
    </div>

    <div class="auth-form-panel" style="width:460px">
      <div style="width:100%; max-width:400px">


        <h4 class="fw-bold mb-1">Create account</h4>
        <p class="text-muted small mb-4">Register as a trekker</p>

        <div v-if="error"   class="alert alert-danger py-2 small">{{ error }}</div>
        <div v-if="success" class="alert alert-success py-2 small">
          Account created! <RouterLink to="/login" style="color:var(--orange)">Sign in now</RouterLink>
        </div>

        <form v-if="!success" @submit.prevent="handleRegister">
          <div class="row g-3">
            <div class="col-6">
              <label class="form-label fw-semibold small">Username *</label>
              <input v-model="form.username" class="form-control" required minlength="3" />
            </div>
            <div class="col-6">
              <label class="form-label fw-semibold small">Full Name</label>
              <input v-model="form.full_name" class="form-control" />
            </div>
            <div class="col-12">
              <label class="form-label fw-semibold small">Email *</label>
              <input v-model="form.email" type="email" class="form-control" required />
            </div>
            <div class="col-6">
              <label class="form-label fw-semibold small">
                Phone 
              </label>
              <input v-model="form.phone" class="form-control" placeholder="+91..."  required minlength="10" maxlength="10"/>
            </div>
            <div class="col-6">
              <label class="form-label fw-semibold small">Password *</label>
              <input v-model="form.password" type="password" class="form-control" required minlength="6" />
            </div>
            <div class="col-12">
              <button type="submit" class="btn btn-success w-100 py-2 fw-semibold" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                Create Account
              </button>
            </div>
          </div>
        </form>

        <hr class="my-4" />
        <p class="text-center text-muted small mb-0">
          Already have an account?
          <RouterLink to="/login" style="color:var(--orange); text-decoration:none; font-weight:600">Sign in</RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import api from '../api'

const form    = reactive({ username: '', email: '', full_name: '', phone: '', password: '' })
const loading = ref(false)
const error   = ref('')
const success = ref(false)

async function handleRegister() {
  loading.value = true; error.value = ''
  try {
    await api.post('/api/auth/register', form)
    success.value = true
  } catch (err) {
    error.value = err.response?.data?.error || 'Registration failed'
  } finally {
    loading.value = false
  }
}
</script>
