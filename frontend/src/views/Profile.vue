<template>
  <div class="container py-4" style="max-width: 560px">
    <h3 class="mb-4"><i class="bi bi-person-circle me-2"></i>My Profile</h3>

    <div v-if="saved" class="alert alert-success py-2">Profile updated!</div>
    <div v-if="error"  class="alert alert-danger py-2">{{ error }}</div>

    <div class="card shadow-sm">
      <div class="card-body p-4">
        <form @submit.prevent="saveProfile">
          <div class="mb-3">
            <label class="form-label">Username</label>
            <!-- readonly — users can't change their username -->
            <input :value="auth.user?.username" class="form-control" readonly />
          </div>
          <div class="mb-3">
            <label class="form-label">Email</label>
            <input :value="auth.user?.email" class="form-control" readonly />
          </div>
          <div class="mb-3">
            <label class="form-label">Full Name</label>
            <input v-model="form.full_name" class="form-control" />
          </div>
          <div class="mb-3">
            <label class="form-label">Phone</label>
            <input v-model="form.phone" class="form-control" />
          </div>
          <hr />
          <p class="text-muted small">Change password (leave blank to keep current)</p>
          <div class="mb-3">
            <label class="form-label">Current Password</label>
            <input v-model="form.current_password" type="password" class="form-control" />
          </div>
          <div class="mb-3">
            <label class="form-label">New Password</label>
            <input v-model="form.new_password" type="password" class="form-control" minlength="6" />
          </div>

          <button type="submit" class="btn btn-success" :disabled="saving">
            <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
            Save Changes
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useAuthStore } from '../store/auth'
import api from '../api'

const auth = useAuthStore()

// Initialize form from current user data in store
const form  = reactive({
  full_name: auth.user?.full_name || '',
  phone:     auth.user?.phone || '',
  current_password: '',
  new_password:  ''
})
const saving = ref(false)
const saved  = ref(false)
const error  = ref('')

async function saveProfile() {
  saving.value = true
  saved.value  = false
  error.value  = ''

  const payload = { full_name: form.full_name, phone: form.phone }
  if (form.new_password) {
    if (!form.current_password) {
      error.value = 'Current password is required to set a new password'
      saving.value = false
      return
    }
    payload.current_password = form.current_password
    payload.new_password = form.new_password
  }

  try {
    const { data } = await api.put('/api/auth/me', payload)
    auth.updateUser(data.user)  // update Pinia store so Navbar shows new name
    saved.value   = true
    form.current_password = ''
    form.new_password = ''
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to update'
  } finally {
    saving.value = false
  }
}
</script>
