<template>
  <div class="chat-window">
    <div class="chat-header">
      <img :src="selectedConversation.avatar" alt="avatar" class="avatar" />
      <h2>{{ selectedConversation.name }}</h2>
      <h4>{{ selectedConversation.job_title }}</h4>
    </div>

    <div class="chat-body" ref="chatBody">
      <template v-if="messages.length > 0">
        <div v-for="(msg, index) in messages" :key="msg.id"
          :class="['message-wrapper', isSent(msg) ? 'sent' : 'received']">
          <p class="sender-name" v-if="shouldShowSender(index)">
            {{ isSent(msg) ? "You" : msg.sender_username }}
          </p>

          <div :class="['chat-bubble', isSent(msg) ? 'sent' : 'received']">
            <p class="message-text">{{ msg.body }}</p>
            <span class="timestamp">{{ formatDate(msg.created_at) }}</span>
          </div>
        </div>
      </template>

      <div v-else class="no-messages">No messages yet.</div>
    </div>

    <div class="chat-input">
      <input v-model="newMessage" type="text" placeholder="Write a message..." @keyup.enter="sendMessage"
        :disabled="isSending" />
      <button @click="sendMessage" :disabled="isSending" class="flex items-center gap-2">
        <span v-if="!isSending">Send</span>
        <span v-else class="flex items-center gap-1">
          <svg class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none"
            viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
          </svg>
          Sending...
        </span>
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: "ChatWindow",
  props: {
    selectedConversation: Object,
    messages: Array,
    userId: Number
  },
  data() {
    return {
      newMessage: "",
      isSending: false
    }
  },
  methods: {
    async sendMessage() {
      if (this.newMessage.trim() === "" || this.isSending) return

      this.isSending = true
      try {
        await this.$emit("send-message", this.newMessage.trim())
        this.newMessage = ""
      } finally {
        this.isSending = false
      }
    },
    formatDate(dateStr) {
      const d = new Date(dateStr)
      return `${d.getHours()}:${String(d.getMinutes()).padStart(2, "0")}`
    },
    scrollToBottom() {
      this.$nextTick(() => {
        const el = this.$refs.chatBody
        if (el) el.scrollTop = el.scrollHeight
      })
    },
    shouldShowSender(index) {
      if (index === 0) return true
      return this.messages[index - 1].sender !== this.messages[index].sender
    },
    isSent(msg) {
      return Number(msg.sender) === Number(this.userId)
    }
  },
  watch: {
    messages() {
      this.scrollToBottom()
    }
  },
  mounted() {
    this.scrollToBottom()
  }
}
</script>

<style scoped>
.chat-window {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #fff;
  height: 100vh;
}

.chat-header {
  display: flex;
  align-items: center;
  padding: 1rem;
  background-color: #f3f4f6;
  border-bottom: 1px solid #d1d5db;
}

.chat-header .avatar {
  width: 40px;
  height: 40px;
  border-radius: 9999px;
  margin-right: 0.75rem;
}

.chat-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
  margin-right: 0.75rem;
}

.chat-header h4 {
  font-size: 1rem;
  font-weight: 400;
  color: #6b7280;
  margin: 0;
}

.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
}

.message-wrapper {
  width: 100%;
  display: flex;
  flex-direction: column;
  margin-bottom: 0.75rem;
}

.message-wrapper.sent {
  align-items: flex-end;
}

.message-wrapper.received {
  align-items: flex-start;
}

.sender-name {
  font-size: 0.75rem;
  font-weight: 600;
  color: #9ca3af;
  margin-bottom: 0.25rem;
  padding: 0 0.5rem;
}

.chat-bubble {
  padding: 0.75rem;
  border-radius: 1rem;
  position: relative;
  word-break: break-word;
  max-width: 75%;
}

.chat-bubble.sent {
  background-color: #3b82f6;
  color: white;
  border-bottom-right-radius: 0;
  margin-left: auto;
}

.chat-bubble.received {
  background-color: #1f2937;
  color: white;
  border-bottom-left-radius: 0;
  margin-right: auto;
}

.timestamp {
  display: block;
  font-size: 0.75rem;
  margin-top: 0.25rem;
  opacity: 0.6;
  text-align: right;
}

.chat-input {
  display: flex;
  padding: 0.75rem;
  border-top: 1px solid #d1d5db;
}

.chat-input input {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  margin-right: 0.5rem;
}

.chat-input button {
  background-color: #3b82f6;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.chat-input button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.no-messages {
  text-align: center;
  color: #9ca3af;
  font-style: italic;
  padding: 1rem;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 9999px;
  object-fit: cover;
  margin-right: 0.75rem;
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

@media (max-width: 768px) {
  .chat-window {
    height: calc(100vh - 300px);
  }

  .chat-header {
    padding: 0.75rem;
  }

  .chat-body {
    padding: 0.75rem;
  }

  .chat-bubble {
    max-width: 85%;
  }

  /* Nouvelles modifications pour mobile */
  .chat-input {
    flex-direction: column;
    padding: 0.75rem;
    gap: 0.5rem;
  }

  .chat-input input {
    width: 100%;
    margin-right: 0;
    padding: 0.75rem;
    font-size: 16px;
    /* Empêche le zoom sur iOS */
  }

  .chat-input button {
    width: 100%;
    padding: 0.75rem;
    justify-content: center;
  }
}
</style>
