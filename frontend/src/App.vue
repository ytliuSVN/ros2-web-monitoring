<script setup lang="ts">
import MapView from './components/MapView.vue'
import StatusBar from './components/StatusBar.vue'
import TelemetryPanel from './components/TelemetryPanel.vue'
import { useGpsSocket } from './composables/useGpsSocket'
import { usePathTrack } from './composables/usePathTrack'

// 預設走同源 /ws（production 由 nginx 反代、dev 由 vite proxy），
// 從別台機器或別的埠口開啟時也不會連錯；VITE_WS_URL 可覆寫。
function sameOriginWsUrl(): string {
  const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${protocol}//${location.host}/ws/gps`
}

const WS_URL = import.meta.env.VITE_WS_URL || sameOriginWsUrl()

const { points, revision, addFix } = usePathTrack()
const { status, latest } = useGpsSocket(WS_URL, addFix)
</script>

<template>
  <StatusBar :status="status" />
  <MapView class="map" :points="points" :revision="revision" />
  <TelemetryPanel :fix="latest" />
</template>

<style scoped>
/* Leaflet 需要父層給定高度，否則地圖容器會塌成 0。 */
.map {
  flex: 1;
  min-height: 0;
}
</style>
