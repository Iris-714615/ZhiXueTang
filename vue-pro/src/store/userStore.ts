import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const username = ref(localStorage.getItem('username') || '')
  const userId = ref(localStorage.getItem('user_id') || '')

  const isLoggedIn = computed(() => !!token.value && !!username.value)

  function setUser(info: { token: string; username: string; user_id: string }) {
    token.value = info.token
    username.value = info.username
    userId.value = info.user_id
    localStorage.setItem('token', info.token)
    localStorage.setItem('username', info.username)
    localStorage.setItem('user_id', info.user_id)
  }

  function logout() {
    token.value = ''
    username.value = ''
    userId.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    localStorage.removeItem('user_id')
  }

  // 初始化时从 localStorage 读取
  function init() {
    token.value = localStorage.getItem('token') || ''
    username.value = localStorage.getItem('username') || ''
    userId.value = localStorage.getItem('user_id') || ''
  }

  return { token, username, userId, isLoggedIn, setUser, logout, init }
})
