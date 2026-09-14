/** 與 backend 推播的 `GpsFix` 契約一致，欄位不可更名。 */
export interface GpsFix {
  latitude: number
  longitude: number
  altitude: number
  /** `sensor_msgs/NavSatStatus`：-1 NO_FIX、0 FIX。 */
  status: number
  /** ROS `header.stamp` 轉成的 Unix 秒。 */
  timestamp: number
  frame_id: string
  seq: number
}

export type ConnectionStatus = 'connecting' | 'open' | 'closed'
