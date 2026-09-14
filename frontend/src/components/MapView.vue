<script setup lang="ts">
import 'leaflet/dist/leaflet.css'

import * as L from 'leaflet'
import type { LatLngTuple } from 'leaflet'
import { onMounted, onUnmounted, ref, watch } from 'vue'

const props = defineProps<{
  points: LatLngTuple[]
  revision: number
}>()

// 還沒有資料前先看高雄市區，與 path_data.csv 起點同區域。
const DEFAULT_CENTER: LatLngTuple = [22.6273, 120.3014]
const DEFAULT_ZOOM = 16

const container = ref<HTMLDivElement | null>(null)

let map: L.Map | null = null
let track: L.Polyline | null = null
let marker: L.CircleMarker | null = null

function sync() {
  if (track === null || marker === null || map === null) {
    return
  }

  const points = props.points
  const lastPoint = points.at(-1)
  if (lastPoint === undefined) {
    return
  }

  // 以 Polyline 目前的點數判斷要補畫哪些；超出上限被裁切過就整條重建。
  const drawn = (track.getLatLngs() as L.LatLng[]).length
  if (drawn > 0 && drawn < points.length) {
    for (const point of points.slice(drawn)) {
      track.addLatLng(point)
    }
  } else if (drawn !== points.length) {
    track.setLatLngs(points)
  }

  marker.setLatLng(lastPoint)
  map.panTo(lastPoint, { animate: true, duration: 0.2 })
}

onMounted(() => {
  map = L.map(container.value!).setView(DEFAULT_CENTER, DEFAULT_ZOOM)
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
    maxZoom: 19,
  }).addTo(map)

  track = L.polyline([], { color: '#aa3bff', weight: 4 }).addTo(map)
  // 用 circleMarker 而非預設 Marker：預設圖示會去載 Leaflet 的 PNG，
  // 打包後路徑會失效，MVP 不值得為此搬資源。
  marker = L.circleMarker(DEFAULT_CENTER, {
    radius: 7,
    color: '#fff',
    weight: 2,
    fillColor: '#aa3bff',
    fillOpacity: 1,
  }).addTo(map)

  sync()
})

onUnmounted(() => {
  map?.remove()
  map = null
  track = null
  marker = null
})

watch(() => props.revision, sync)
</script>

<template>
  <div ref="container" class="map-view"></div>
</template>

<style scoped>
.map-view {
  width: 100%;
  height: 100%;
}
</style>
