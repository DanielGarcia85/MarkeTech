<template>
  <div v-if="isPremium" class="premium-badge" :class="variant">
    <i class="fas fa-crown"></i>
    <span>{{ label }}</span>
  </div>
</template>

<script>
export default {
  name: "PremiumBadge",
  props: {
    isPremium: {
      type: Boolean,
      required: true
    },
    variant: {
      type: String,
      default: 'default',
      validator: value => ['default', 'small', 'large'].includes(value)
    },
    label: {
      type: String,
      default: 'Premium'
    }
  }
}
</script>

<style scoped>
.premium-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  background: linear-gradient(135deg, #ffd700, #ffed4e);
  color: #333;
  font-weight: 600;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(255, 215, 0, 0.3);
  animation: subtle-glow 2s ease-in-out infinite alternate;
}

.premium-badge.default {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
}

.premium-badge.small {
  padding: 0.125rem 0.375rem;
  font-size: 0.625rem;
}

.premium-badge.large {
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
}

.premium-badge i {
  font-size: 0.8em;
}

@keyframes subtle-glow {
  from {
    box-shadow: 0 2px 4px rgba(255, 215, 0, 0.3);
  }

  to {
    box-shadow: 0 2px 8px rgba(255, 215, 0, 0.5);
  }
}
</style>
