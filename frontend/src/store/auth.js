import { defineStore } from "pinia";
import { ref, computed } from "vue";

export const useAuthStore = defineStore("auth", () => {
  const token = ref(localStorage.getItem("token") || null);
  const user = ref(JSON.parse(localStorage.getItem("user") || "null"));

  const isLoggedIn = computed(() => !!token.value);
  const role = computed(() => user.value?.role || null);

  function login(tokenStr, userData) {
    token.value = tokenStr;
    user.value = userData;
    localStorage.setItem("token", tokenStr);
    localStorage.setItem("user", JSON.stringify(userData));
  }

  function logout() {
    token.value = null;
    user.value = null;
    localStorage.removeItem("token");
    localStorage.removeItem("user");
  }

  function updateUser(userData) {
    user.value = { ...user.value, ...userData };
    localStorage.setItem("user", JSON.stringify(user.value));
  }

  return { token, user, isLoggedIn, role, login, logout, updateUser };
});
