<script setup lang="ts">
import type { ConnectionStatus } from '../types/gps'

defineProps<{ status: ConnectionStatus }>()

const LABELS: Record<ConnectionStatus, string> = {
  connecting: '連線中',
  open: '已連線',
  closed: '已斷線',
}
</script>

<template>
  <header class="status-bar">
    <h1>GNSS 即時路徑監控</h1>
    <span class="state">
      <span class="dot" :class="status"></span>
      {{ LABELS[status] }}
    </span>
  </header>
</template>

<style scoped>
.status-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 10px 16px;
  border-bottom: 1px solid var(--border);
  background: var(--bg);
}

h1 {
  margin: 0;
  font-size: 16px;
  letter-spacing: normal;
}

.state {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-family: var(--mono);
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--text);
}

.dot.connecting {
  background: #d98324;
}

.dot.open {
  background: #2e9e5b;
}

.dot.closed {
  background: #d64545;
}
</style>
