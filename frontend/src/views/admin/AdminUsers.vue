<template>
  <div class="container py-4">
    <h3 class="mb-4"><i class="bi bi-people me-2"></i>Manage Users & Staff</h3>

    <ul class="nav nav-tabs mb-3">
      <li class="nav-item">
        <button :class="['nav-link', activeTab === 'trekker' ? 'active' : '']" @click="switchTab('trekker')">
          Trekkers
        </button>
      </li>
      <li class="nav-item">
        <button :class="['nav-link', activeTab === 'staff' ? 'active' : '']" @click="switchTab('staff')">
          Staff
        </button>
      </li>
    </ul>

    <div class="d-flex gap-2 mb-3">
      <input v-model="search" class="form-control" style="max-width:300px"
             placeholder="Search by name or email" @input="fetchUsers" />
      <button v-if="activeTab === 'staff'" class="btn btn-success" @click="showCreateStaff = true">
        <i class="bi bi-plus-lg me-1"></i>Add Staff
      </button>
    </div>

    <div v-if="loading" class="text-center py-5"><div class="spinner-border text-success"></div></div>

    <div v-else class="table-responsive">
      <table class="table table-hover align-middle">
        <thead class="table-dark">
          <tr><th>Username</th><th>Email</th><th>Full Name</th><th>Status</th><th>Actions</th></tr>
        </thead>
        <tbody>
          <tr v-if="users.length === 0">
            <td colspan="5" class="text-center text-muted py-4">No users found</td>
          </tr>
          <tr v-else v-for="user in users" :key="user.id">
            <td>{{ user.username }}</td>
            <td>{{ user.email }}</td>
            <td>{{ user.full_name || '—' }}</td>
            <td>
              <span v-if="user.is_blacklisted" class="badge bg-danger">Blacklisted</span>
              <span v-else-if="!user.is_active" class="badge bg-warning text-dark">Inactive</span>
              <span v-else class="badge bg-success">Active</span>
            </td>
            <td>
              <button v-if="user.is_active && !user.is_blacklisted"
                class="btn btn-sm btn-outline-warning me-1"
                @click="setStatus(user.id, { is_active: false })">Deactivate</button>
              <button v-if="!user.is_active || !user.is_blacklisted"
                class="btn btn-sm btn-outline-danger me-1"
                @click="setStatus(user.id, { is_blacklisted: true })">Blacklist</button>
              <button v-if="!user.is_active || user.is_blacklisted"
                class="btn btn-sm btn-outline-success"
                @click="setStatus(user.id, { is_active: true, is_blacklisted: false })">Activate</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showCreateStaff" class="modal d-block" style="background:rgba(0,0,0,0.5)">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Create Staff Account</h5>
            <button class="btn-close" @click="showCreateStaff = false"></button>
          </div>
          <div class="modal-body">
            <div v-if="staffError" class="alert alert-danger py-2">{{ staffError }}</div>
            <form @submit.prevent="createStaff" id="staffForm">
              <div class="mb-3">
                <label class="form-label">Username *</label>
                <input v-model="staffForm.username" class="form-control" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Email *</label>
                <input v-model="staffForm.email" type="email" class="form-control" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Full Name</label>
                <input v-model="staffForm.full_name" class="form-control" required minlength="8" />
              </div>
              <div class="mb-3">
                <label class="form-label">
                  Phone 
                </label>
                <input v-model="staffForm.phone" class="form-control" placeholder="+91..."  required minlength="10" maxlength="10"/>
              </div>
              <div class="mb-3">
                <label class="form-label">Password *</label>
                <input v-model="staffForm.password" type="password" class="form-control" required minlength="6" />
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showCreateStaff = false">Cancel</button>
            <button class="btn btn-success" form="staffForm" type="submit">Create</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '../../api'

const users      = ref([])
const loading    = ref(true)
const search     = ref('')
const activeTab  = ref('trekker')

const showCreateStaff = ref(false)
const staffError = ref('')
const staffForm  = reactive({ username: '', email: '', full_name: '', phone: '', password: '' })

async function fetchUsers() {
  loading.value = true
  const { data } = await api.get('/api/admin/users', {
    params: { role: activeTab.value, search: search.value }
  })
  users.value   = data.users
  loading.value = false
}

function switchTab(tab) {
  activeTab.value = tab
  search.value    = ''
  fetchUsers()
}

async function setStatus(userId, payload) {
  await api.put(`/api/admin/users/${userId}/status`, payload)
  await fetchUsers()
}

async function createStaff() {
  staffError.value = ''
  try {
    await api.post('/api/admin/staff', staffForm)
    showCreateStaff.value = false
    Object.assign(staffForm, { username: '', email: '', full_name: '', phone: '', password: '' })
    //manual refetch 
    if (activeTab.value === 'staff') await fetchUsers()
  } catch (err) {
    staffError.value = err.response?.data?.error || 'Failed to create staff'
  }
}

onMounted(fetchUsers)
</script>
