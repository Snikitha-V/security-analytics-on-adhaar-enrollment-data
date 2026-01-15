import { useEffect, useState } from 'react'
import { csvParse, csvParseRows } from 'd3-dsv'
import { useQuery } from '@tanstack/react-query'
import { z } from 'zod'

const base = (import.meta.env.BASE_URL ?? '/').replace(/\/$/, '')
const pathFor = (file: string) => `${base}/outputs/${file}`

const riskRowSchema = z.object({
  pincode: z.string().trim(),
  state: z.string().trim(),
  district: z.string().trim(),
  total_enrollments: z.coerce.number().default(0),
  total_demo_updates: z.coerce.number().default(0),
  total_bio_updates: z.coerce.number().default(0),
  age_0_5: z.coerce.number().default(0),
  age_5_17: z.coerce.number().default(0),
  age_18_greater: z.coerce.number().default(0),
  child_ratio: z.coerce.number().optional(),
  update_ratio: z.coerce.number().optional(),
  bio_recapture_ratio: z.coerce.number().optional(),
  enrollment_velocity: z.coerce.number().optional(),
  update_velocity: z.coerce.number().optional(),
  bio_velocity: z.coerce.number().optional(),
  child_ratio_zscore: z.coerce.number().optional(),
  update_ratio_zscore: z.coerce.number().optional(),
  bio_recapture_ratio_zscore: z.coerce.number().optional(),
  risk_enrollment_velocity: z.coerce.number().optional(),
  risk_update_velocity: z.coerce.number().optional(),
  risk_demographic_anomaly: z.coerce.number().optional(),
  risk_geographic_outlier: z.coerce.number().optional(),
  risk_temporal_spike: z.coerce.number().optional(),
  risk_score: z.coerce.number().optional(),
  risk_level: z.string().optional(),
  first_date: z.string().optional(),
  last_date: z.string().optional(),
})

const dailyRowSchema = z.object({
  date: z.string(),
  total_enrollments: z.coerce.number().default(0),
  total_demo_updates: z.coerce.number().default(0),
  total_bio_updates: z.coerce.number().default(0),
  active_pins: z.coerce.number().default(0),
})

const stateRowSchema = z.object({
  state: z.string(),
  avg_risk_score: z.coerce.number().default(0),
  max_risk_score: z.coerce.number().default(0),
  risk_score_std: z.coerce.number().default(0),
  pin_count: z.coerce.number().default(0),
  high_risk_pins: z.coerce.number().default(0),
  total_enrollments: z.coerce.number().optional(),
  total_demo_updates: z.coerce.number().optional(),
  total_bio_updates: z.coerce.number().optional(),
})

const districtRowSchema = z.object({
  state: z.string(),
  district: z.string(),
  avg_risk_score: z.coerce.number().default(0),
  max_risk_score: z.coerce.number().default(0),
  pin_count: z.coerce.number().default(0),
  total_enrollments: z.coerce.number().default(0),
  total_demo_updates: z.coerce.number().default(0),
  total_bio_updates: z.coerce.number().default(0),
})

const alertsRowSchema = z.object({
  ioc_id: z.string().optional(),
  pattern_name: z.string().optional(),
  state: z.string().optional(),
  district: z.string().optional(),
  pincode: z.string().optional(),
  risk_level: z.string().optional(),
  risk_score: z.coerce.number().optional(),
  date_detected: z.string().optional(),
  recommended_action: z.string().optional(),
})

export type RiskRecord = z.infer<typeof riskRowSchema>
export type DailyRow = z.infer<typeof dailyRowSchema>
export type StateRow = z.infer<typeof stateRowSchema>
export type DistrictRow = z.infer<typeof districtRowSchema>
export type AlertRow = z.infer<typeof alertsRowSchema>

async function fetchCsv(path: string) {
  const res = await fetch(path)
  if (!res.ok) {
    throw new Error(`Failed to load ${path}: ${res.status}`)
  }
  const text = await res.text()
  return csvParse(text)
}

function coerceRows<T>(rows: object[], schema: z.ZodTypeAny): T[] {
  const parsed: T[] = []
  rows.forEach((row) => {
    const result = schema.safeParse(row)
    if (result.success) parsed.push(result.data as T)
  })
  return parsed
}

type RiskHookState = {
  rows: RiskRecord[]
  isLoading: boolean
  isPartial: boolean
  error: Error | null
}

function coerceRowArray(row: string[], header: string[]): RiskRecord | null {
  const obj: Record<string, string> = {}
  header.forEach((key, idx) => {
    obj[key] = row[idx] ?? ''
  })
  const parsed = riskRowSchema.safeParse(obj)
  return parsed.success ? parsed.data : null
}

function scheduleIdle(fn: () => void) {
  if (typeof (window as any).requestIdleCallback === 'function') {
    ;(window as any).requestIdleCallback(fn)
  } else {
    setTimeout(fn, 0)
  }
}

export function useRiskData() {
  const [state, setState] = useState<RiskHookState>({
    rows: [],
    isLoading: true,
    isPartial: true,
    error: null,
  })

  useEffect(() => {
    let cancelled = false

    const load = async () => {
      try {
        const res = await fetch(pathFor('risk_scores.csv'))
        if (!res.ok) throw new Error(`Failed to load risk_scores.csv: ${res.status}`)
        const text = await res.text()
        const rows = csvParseRows(text)
        if (!rows.length) throw new Error('risk_scores.csv is empty')
        const [header, ...dataRows] = rows
        const headerClean = header.map((h) => h.trim())

        const CHUNK = 800
        const initial = dataRows.slice(0, CHUNK).map((r) => coerceRowArray(r, headerClean)).filter(Boolean) as RiskRecord[]

        if (cancelled) return
        setState({ rows: initial, isLoading: false, isPartial: dataRows.length > CHUNK, error: null })

        if (dataRows.length > CHUNK) {
          let idx = CHUNK
          const append = () => {
            if (cancelled) return
            const chunk = dataRows.slice(idx, idx + CHUNK).map((r) => coerceRowArray(r, headerClean)).filter(Boolean) as RiskRecord[]
            idx += CHUNK
            if (chunk.length) {
              setState((prev) => ({ ...prev, rows: [...prev.rows, ...chunk] }))
            }
            if (idx < dataRows.length) {
              scheduleIdle(append)
            } else {
              setState((prev) => ({ ...prev, isPartial: false }))
            }
          }
          scheduleIdle(append)
        }
      } catch (err: any) {
        if (cancelled) return
        setState({ rows: [], isLoading: false, isPartial: false, error: err })
      }
    }

    load()
    return () => {
      cancelled = true
    }
  }, [])

  return {
    data: state.rows,
    isLoading: state.isLoading,
    isError: !!state.error,
    error: state.error,
    isPartial: state.isPartial,
  }
}

async function loadDaily(): Promise<DailyRow[]> {
  const rows = await fetchCsv(pathFor('daily_summary.csv'))
  return coerceRows<DailyRow>(rows, dailyRowSchema)
}

async function loadStates(): Promise<StateRow[]> {
  const rows = await fetchCsv(pathFor('state_summary.csv'))
  return coerceRows<StateRow>(rows, stateRowSchema)
}

async function loadDistricts(): Promise<DistrictRow[]> {
  const rows = await fetchCsv(pathFor('district_summary.csv'))
  return coerceRows<DistrictRow>(rows, districtRowSchema)
}

async function loadAlerts(): Promise<AlertRow[]> {
  const rows = await fetchCsv(pathFor('alerts.csv'))
  return coerceRows<AlertRow>(rows, alertsRowSchema)
}

export function useDailyData() {
  return useQuery({
    queryKey: ['daily'],
    queryFn: loadDaily,
    staleTime: 1000 * 60 * 10,
  })
}

export function useStateData() {
  return useQuery({
    queryKey: ['state-summary'],
    queryFn: loadStates,
    staleTime: 1000 * 60 * 10,
  })
}

export function useDistrictData() {
  return useQuery({
    queryKey: ['district-summary'],
    queryFn: loadDistricts,
    staleTime: 1000 * 60 * 10,
  })
}

export function useAlertsData() {
  return useQuery({
    queryKey: ['alerts'],
    queryFn: loadAlerts,
    staleTime: 1000 * 60 * 10,
  })
}