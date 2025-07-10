<template>
  <div>
    <ContentHeader title="Communicates with others" description="Chat with your candidates or your employers." />
    <div class="messages-page">
      <ChatSidebar :conversations="conversations" @select="handleSelectConversation" />
      <ChatWindow v-if="selectedConversation && user" :selectedConversation="selectedConversation" :messages="messages"
        :userId="user" @send-message="handleSendMessage" />
      <div v-else class="empty-chat">
        <div class="placeholder">
          <p class="icon">💬</p>
          <p>Select a conversation to start messaging.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { useRoute } from "vue-router"
import ChatSidebar from "@/components/chat/ChatSidebar.vue"
import ChatWindow from "@/components/chat/ChatWindow.vue"
import authService from "@/services/authService"
import messageService from "@/services/messageService"
import ContentHeader from "@/components/ContentHeader.vue"
import api from "@/services/api"

const conversations = ref([])
const selectedConversation = ref(null)
const messages = ref([])
const user = ref(null)
const route = useRoute()

const handleSelectConversation = async (conversation) => {
  selectedConversation.value = conversation
  messages.value = await messageService.fetchMessages(conversation.application_id)
  await authService.getUser()
  user.value = authService.user.value.user.id
}

const handleSendMessage = async (text) => {
  const msg = await messageService.postMessage({
    body: text,
    subject: "Message",
    application: selectedConversation.value.application_id
  })
  messages.value.push(msg)
}

onMounted(async () => {
  conversations.value = await messageService.fetchConversations()

  const selectedId = parseInt(route.query.application_id)
  if (selectedId) {
    let target = conversations.value.find((c) => c.application_id === selectedId)

    if (!target) {
      try {
        const res = await api.get(`/applications/${selectedId}/`, {
          withCredentials: true
        })
        const application = res.data

        target = {
          application_id: selectedId,
          name: application.candidate_username,
          avatar: application.profile_picture || "/media/profile_pictures/place_holder.png",
          last_message: "(No messages yet)"
        }

        conversations.value.unshift(target)
      } catch (error) {
        console.error("Failed to fetch application details:", error)
      }
    }

    if (target) handleSelectConversation(target)
  }
})
</script>

<style scoped>
.messages-page {
  display: flex;
  height: 100vh;
  font-family: sans-serif;
}

@media (max-width: 768px) {
  .messages-page {
    flex-direction: column;
    height: auto;
  }

  .empty-chat {
    height: 70vh;
  }
}

.empty-chat {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
  font-size: 1rem;
}

.placeholder {
  text-align: center;
  opacity: 0.6;
}

.placeholder .icon {
  font-size: 3rem;
  margin-bottom: 0.5rem;
}
</style>
