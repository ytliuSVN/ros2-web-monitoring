<script setup lang="ts">
import MapView from './components/MapView.vue'
import StatusBar from './components/StatusBar.vue'
import TelemetryPanel from './components/TelemetryPanel.vue'
import { useGpsSocket } from './composables/useGpsSocket'
import { usePathTrack } from './composables/usePathTrack'

const WS_URL = 'ws://localhost:8000/ws/gps'

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
