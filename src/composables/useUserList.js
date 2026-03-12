import { ref, onMounted } from 'vue'
import { getUserList } from '@/api/SystemManager/UserView'

export function useUserList(autoFetch = true) {
  const userList = ref([])
  const loading = ref(false)

  const fetchUsers = async () => {
    loading.value = true
    try {
      const res = await getUserList({ page: 1, page_size: 1000 }) // Fetch enough users
      if (res.code === 200) {
        if (Array.isArray(res.data)) {
            userList.value = res.data
        } else if (res.data && res.data.list) {
            userList.value = res.data.list
        } else if (res.data && res.data.items) {
            userList.value = res.data.items
        } else if (res.rows) {
            userList.value = res.rows
        } else {
            userList.value = []
        }
      } else {
        // Fallback or handle error code
         if (res.rows) {
            userList.value = res.rows
        }
      }
    } catch (error) {
      console.error('Failed to fetch users:', error)
    } finally {
      loading.value = false
    }
  }

  // Helper to get user name by ID
  const getUserName = (id) => {
    if (!id) return '-'
    const user = userList.value.find(u => u.user_id === id || u.id === id)
    return user ? (user.nickname || user.username) : String(id)
  }

  // Helper for avatar color
  const getAvatarColor = (name) => {
    if (!name) return '#409EFF'
    const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399', '#303133']
    let hash = 0
    for (let i = 0; i < name.length; i++) {
      hash = name.charCodeAt(i) + ((hash << 5) - hash)
    }
    const index = Math.abs(hash) % colors.length
    return colors[index]
  }

  if (autoFetch) {
    onMounted(() => {
      fetchUsers()
    })
  }

  return {
    userList,
    loading,
    fetchUsers,
    getUserName,
    getAvatarColor
  }
}
