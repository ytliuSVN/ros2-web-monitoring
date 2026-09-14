import type { LatLngTuple } from 'leaflet'
import { ref, shallowRef, triggerRef } from 'vue'

import type { GpsFix } from '../types/gps'

const MAX_POINTS = 10_000

/**
 * 累積走過的座標。
 *
 * `addFix` 回傳新加入的點，與前一點重複時回傳 null。
 * `revision` 為已接受的累計點數，供地圖判斷要補畫幾個點。
 */
export function usePathTrack(maxPoints = MAX_POINTS) {
  // shallowRef + 原地 push：5 Hz 下每筆都複製上萬筆陣列太貴，改用 triggerRef 通知。
  const points = shallowRef<LatLngTuple[]>([])
  const revision = ref(0)

  function addFix(fix: GpsFix): LatLngTuple | null {
    const point: LatLngTuple = [fix.latitude, fix.longitude]
    const last = points.value.at(-1)
    if (last !== undefined && last[0] === point[0] && last[1] === point[1]) {
      return null
    }

    points.value.push(point)
    const overflow = points.value.length - maxPoints
    if (overflow > 0) {
      points.value.splice(0, overflow)
    }
    triggerRef(points)
    revision.value += 1
    return point
  }

  return { points, revision, addFix }
}
