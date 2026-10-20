import { api } from './client'

export type Health = { status: 'ok' | 'degraded'; database: 'ok' | 'unavailable' }

export async function fetchHealth(): Promise<Health> {
  const { data, response } = await api.GET('/health')
  if (data) return data
  // The API answers 503 with a body when it is up but the database is not.
  if (response.status === 503) return { status: 'degraded', database: 'unavailable' }
  throw new Error(`Health check failed with HTTP ${response.status}`)
}
