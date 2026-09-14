<script setup lang="ts">
import type { GpsFix } from '../types/gps'

defineProps<{ fix: GpsFix | null }>()

function formatDegrees(value: number | undefined): string {
  return value === undefined ? '—' : value.toFixed(6)
}
</script>

<template>
  <footer class="telemetry">
    <div class="field">
      <span class="label">緯度</span>
      <span class="value">{{ formatDegrees(fix?.latitude) }}</span>
    </div>
    <div class="field">
      <span class="label">經度</span>
      <span class="value">{{ formatDegrees(fix?.longitude) }}</span>
    </div>
  </footer>
</template>

<style scoped>
.telemetry {
  display: flex;
  gap: 32px;
  padding: 10px 16px;
  border-top: 1px solid var(--border);
  background: var(--bg);
}

.field {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.label {
  font-size: 13px;
}

.value {
  font-family: var(--mono);
  font-size: 15px;
  color: var(--text-h);
}
</style>
