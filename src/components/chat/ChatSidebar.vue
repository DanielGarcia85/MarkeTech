<template>
  <div class="chat-sidebar">
    <h2 class="sidebar-title">Messages</h2>
    <ul class="conversation-list">
      <li
        v-for="conversation in conversations"
        :key="conversation.application_id"
        @click="selectConversation(conversation)"
        class="conversation-item"
      >
        <img :src="conversation.avatar" alt="avatar" class="avatar" />
        <div class="conversation-info">
          <p class="name">{{ conversation.name }}</p>
          <p class="title">{{ conversation.job_title }}</p>
          <p class="preview">{{ conversation.last_message }}</p>
        </div>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: "ChatSidebar",
  props: {
    conversations: Array
  },
  methods: {
    selectConversation(convo) {
      this.$emit("select", convo)
    }
  }
}
</script>

<style scoped>
.chat-sidebar {
  width: 300px;
  background-color: #f3f4f6;
  border-right: 1px solid #d1d5db;
  height: 100vh;
  overflow-y: auto;
  padding: 1rem;
}

.sidebar-title {
  font-size: 1.2rem;
  font-weight: bold;
  margin-bottom: 1rem;
}

.conversation-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.conversation-item {
  display: flex;
  align-items: center;
  padding: 0.5rem 0;
  cursor: pointer;
  transition: background 0.2s;
}

.conversation-item:hover {
  background-color: #e5e7eb;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 9999px;
  object-fit: cover;
  margin-right: 0.75rem;
}

.conversation-info {
  flex: 1;
}

.name {
  font-weight: 600;
  margin: 0;
}

.title {
  font-size: 0.9rem;
  color: #6b7280;
  margin: 0;
}

.preview {
  font-size: 0.8rem;
  color: #6b7280;
  margin: 0;
}

@media (max-width: 768px) {
  .chat-sidebar {
    width: 100%;
    height: auto;
    max-height: 300px;
    border-right: none;
    border-bottom: 1px solid #d1d5db;
  }
}
</style>
