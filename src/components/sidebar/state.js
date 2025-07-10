import { ref, computed } from "vue"

export const collapsed = ref(true)
export const toggleSidebar = () => (collapsed.value = !collapsed.value)

export const SIDEBAR_WIDTH = 200
export const SIDEBAR_COLLAPSED_WIDTH = 38
export const sidebarWidth = computed(
  () => `${collapsed.value ? SIDEBAR_COLLAPSED_WIDTH : SIDEBAR_WIDTH}px`
)
