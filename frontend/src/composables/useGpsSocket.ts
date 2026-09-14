import { onUnmounted, ref, shallowRef } from 'vue'

import type { ConnectionStatus, GpsFix } from '../types/gps'

const INITIAL_RETRY_MS = 500
const MAX_RETRY_MS = 10_000

const NUMBER_FIELDS = [
  'latitude',
  'longitude',
  'altitude',
  'status',
  'timestamp',
  'seq',
] as const

function parseGpsFix(raw: unknown): GpsFix | null {
  if (typeof raw !== 'string') {
    return null
  }
  let data: unknown
  try {
    data = JSON.parse(raw)
  } catch {
    return null
  }
  if (typeof data !== 'object' || data === null) {
    return null
  }
  const record = data as Record<string, unknown>
  if (NUMBER_FIELDS.some((field) => typeof record[field] !== 'number')) {
    return null
  }
  if (typeof record.frame_id !== 'string') {
    return null
  }
  return record as unknown as GpsFix
}

/**
 * 連線 `/ws/gps`，斷線後以指數退避重連。
 *
 * 每筆訊息都經 `onFix` 送出：新連線會一次補送最多 500 筆歷史點，
 * 只看 `latest` 會因為 ref 批次更新而漏掉中間的點。
 */
export function useGpsSocket(url: string, onFix?: (fix: GpsFix) => void) {
  const status = ref<ConnectionStatus>('connecting')
  const latest = shallowRef<GpsFix | null>(null)

  let socket: WebSocket | null = null
  let retryMs = INITIAL_RETRY_MS
  let retryTimer: ReturnType<typeof setTimeout> | null = null
  let disposed = false

  function connect() {
    status.value = 'connecting'
    socket = new WebSocket(url)

    socket.onopen = () => {
      retryMs = INITIAL_RETRY_MS
      status.value = 'open'
    }

    socket.onmessage = (event) => {
      const fix = parseGpsFix(event.data)
      if (fix === null) {
        console.warn('Ignoring malformed GPS message', event.data)
        return
      }
      latest.value = fix
      onFix?.(fix)
    }

    // onerror 之後瀏覽器必定再觸發 onclose，重連只在 onclose 處理一次。
    socket.onerror = () => socket?.close()

    socket.onclose = () => {
      socket = null
      status.value = 'closed'
      scheduleReconnect()
    }
  }

  function scheduleReconnect() {
    if (disposed) {
      return
    }
    retryTimer = setTimeout(connect, retryMs)
    retryMs = Math.min(retryMs * 2, MAX_RETRY_MS)
  }

  function close() {
    disposed = true
    if (retryTimer !== null) {
      clearTimeout(retryTimer)
      retryTimer = null
    }
    socket?.close()
    socket = null
    status.value = 'closed'
  }

  connect()
  onUnmounted(close)

  return { status, latest, close }
}
