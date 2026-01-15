import { useMemo, useState } from 'react'
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  PieChart,
  Pie,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import './index.css'
import {
  useAlertsData,
  useDailyData,
  useRiskData,
  useStateData,
} from './lib/data'

// --- Constants ---
const RISK_COLORS: Record<string, string> = {
  HIGH: '#ea580c',
  MEDIUM: '#ca8a04',
  LOW: '#16a34a',
}

const COMPONENT_INFO = {
  risk_enrollment_velocity: { label: 'Enrollment Velocity', color: '#6366f1', weight: '30%', desc: 'New registrations vs national median' },
  risk_update_velocity: { label: 'Update Velocity', color: '#8b5cf6', weight: '25%', desc: 'Demographic changes vs median' },
  risk_demographic_anomaly: { label: 'Demographic Anomaly', color: '#ec4899', weight: '20%', desc: 'Unusual age/ratio patterns' },
  risk_geographic_outlier: { label: 'Geographic Outlier', color: '#14b8a6', weight: '15%', desc: 'Deviation from district/state norms' },
  risk_temporal_spike: { label: 'Temporal Spike', color: '#f59e0b', weight: '10%', desc: 'Sudden activity bursts' },
}

// --- Utility ---
function sample<T>(arr: T[], n: number): T[] {
  if (arr.length <= n) return arr
  const step = Math.floor(arr.length / n)
  return arr.filter((_, i) => i % step === 0).slice(0, n)
}

function histogram(values: number[], bins = 15) {
  if (!values.length) return []
  const min = Math.min(...values)
  const max = Math.max(...values)
  const step = (max - min || 1) / bins
  return Array.from({ length: bins }, (_, i) => {
    const lo = min + i * step
    const hi = lo + step
    return {
      range: `${lo.toFixed(1)}-${hi.toFixed(1)}`,
      count: values.filter((v) => v >= lo && v < hi).length,
      mid: lo + step / 2,
    }
  })
}

// --- Explainer Component ---
function Explainer({ question, formula, assumption }: { question: string; formula?: string; assumption?: string }) {
  return (
    <div className="text-xs text-muted space-y-1 mb-3 border-l-2 border-primary/30 pl-3">
      <p><strong>Q:</strong> {question}</p>
      {formula && <p><strong>Formula:</strong> <code className="bg-surface px-1 rounded">{formula}</code></p>}
      {assumption && <p><strong>Assumption:</strong> {assumption}</p>}
    </div>
  )
}

// --- Card ---
function Card({ title, children, className = '' }: { title: string; children: React.ReactNode; className?: string }) {
  return (
    <div className={`glass-panel p-4 ${className}`}>
      <h3 className="text-sm font-semibold text-text mb-2">{title}</h3>
      {children}
    </div>
  )
}

// --- KPI ---
function KPI({ label, value, subtext, color }: { label: string; value: string | number; subtext?: string; color?: string }) {
  return (
    <div className="text-center">
      <p className="text-xs text-muted uppercase tracking-wide">{label}</p>
      <p className="text-2xl font-bold" style={{ color: color || '#e2e8f0' }}>{value}</p>
      {subtext && <p className="text-xs text-muted">{subtext}</p>}
    </div>
  )
}

// --- Risk Badge ---
function RiskBadge({ level }: { level: string }) {
  return (
    <span
      className="px-2 py-0.5 rounded text-xs font-medium"
      style={{ backgroundColor: RISK_COLORS[level] || '#475569', color: '#fff' }}
    >
      {level}
    </span>
  )
}

// --- Main App ---
type Section = 'overview' | 'risk-scores' | 'velocities' | 'alerts'

export default function App() {
  const [section, setSection] = useState<Section>('overview')

  const riskQ = useRiskData()
  const dailyQ = useDailyData()
  const stateQ = useStateData()
  const alertsQ = useAlertsData()

  const isLoading = riskQ.isLoading
  const riskData = riskQ.data ?? []
  const dailyData = dailyQ.data ?? []
  const stateData = stateQ.data ?? []
  const alertsData = alertsQ.data ?? []

  // --- Pre-computed stats (memoized) ---
  const stats = useMemo(() => {
    const total = riskData.length
    const byLevel = {
      HIGH: riskData.filter((r) => r.risk_level === 'HIGH').length,
      MEDIUM: riskData.filter((r) => r.risk_level === 'MEDIUM').length,
      LOW: riskData.filter((r) => r.risk_level === 'LOW').length,
    }
    const avgScore = total ? riskData.reduce((s, r) => s + (r.risk_score ?? 0), 0) / total : 0
    const maxScore = total ? Math.max(...riskData.map((r) => r.risk_score ?? 0)) : 0
    return { total, byLevel, avgScore, maxScore }
  }, [riskData])

  // Pie chart data for risk distribution
  const riskPieData = useMemo(() => {
    return Object.entries(stats.byLevel)
      .filter(([_, count]) => count > 0)
      .map(([level, count]) => ({
        name: level,
        value: count,
        fill: RISK_COLORS[level],
      }))
  }, [stats.byLevel])

  // Top 5 high-risk states
  const topStates = useMemo(
    () => [...stateData].sort((a, b) => b.avg_risk_score - a.avg_risk_score).slice(0, 5),
    [stateData]
  )

  // Sampled data for scatter plots (300 points for speed)
  const scatterData = useMemo(() => {
    const sampled = sample(riskData, 300)
    return sampled.map((r) => ({
      pincode: r.pincode,
      enrollment_velocity: r.enrollment_velocity ?? 0,
      update_velocity: r.update_velocity ?? 0,
      bio_velocity: r.bio_velocity ?? 0,
      risk_score: r.risk_score ?? 0,
      risk_level: r.risk_level ?? 'LOW',
      risk_enrollment_velocity: r.risk_enrollment_velocity ?? 0,
      risk_update_velocity: r.risk_update_velocity ?? 0,
      risk_demographic_anomaly: r.risk_demographic_anomaly ?? 0,
      risk_geographic_outlier: r.risk_geographic_outlier ?? 0,
      risk_temporal_spike: r.risk_temporal_spike ?? 0,
    }))
  }, [riskData])

  // Risk score histogram
  const riskHist = useMemo(() => histogram(riskData.map((r) => r.risk_score ?? 0), 20), [riskData])

  // Component distributions (histograms)
  const componentHistograms = useMemo(() => {
    const keys = ['risk_enrollment_velocity', 'risk_update_velocity', 'risk_demographic_anomaly', 'risk_geographic_outlier', 'risk_temporal_spike'] as const
    return keys.map((key) => ({
      key,
      info: COMPONENT_INFO[key],
      data: histogram(riskData.map((r) => (r[key] as number) ?? 0), 12),
    }))
  }, [riskData])

  // Daily trends (sampled)
  const dailySampled = useMemo(() => sample(dailyData, 30), [dailyData])

  // Recent alerts
  const recentAlerts = useMemo(() => alertsData.slice(0, 15), [alertsData])

  // --- Loading / Error ---
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full mx-auto mb-3" />
          <p className="text-muted">Loading data...</p>
        </div>
      </div>
    )
  }

  if (!riskData.length) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-muted">No data available. Ensure CSV files exist in public/outputs/</p>
      </div>
    )
  }

  const sections: { id: Section; label: string }[] = [
    { id: 'overview', label: 'Overview' },
    { id: 'risk-scores', label: 'Risk Scores' },
    { id: 'velocities', label: 'Velocities' },
    { id: 'alerts', label: 'Alerts' },
  ]

  return (
    <div className="min-h-screen bg-background text-text">
      {/* Header */}
      <header className="border-b border-border sticky top-0 z-20 bg-surface/95 backdrop-blur">
        <div className="max-w-5xl mx-auto px-4 py-3">
          <h1 className="text-lg font-bold">Aadhaar Fraud Analytics</h1>
          <p className="text-xs text-muted">Explainable risk scoring for PIN-level anomaly detection</p>
        </div>
        <nav className="max-w-5xl mx-auto px-4 flex gap-1 pb-1">
          {sections.map((s) => (
            <button
              key={s.id}
              onClick={() => setSection(s.id)}
              className={`px-3 py-1.5 text-xs font-medium rounded-t transition ${
                section === s.id ? 'bg-primary/20 text-primary' : 'text-muted hover:text-text'
              }`}
            >
              {s.label}
            </button>
          ))}
        </nav>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-5 space-y-5">
        {/* ===================== OVERVIEW ===================== */}
        {section === 'overview' && (
          <>
            {/* KPIs */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <Card title="Total PINs" className="flex flex-col items-center justify-center">
                <KPI label="" value={stats.total.toLocaleString()} />
              </Card>
              <Card title="High Risk" className="flex flex-col items-center justify-center">
                <KPI label="" value={stats.byLevel.HIGH.toLocaleString()} color={RISK_COLORS.HIGH} subtext={`${((stats.byLevel.HIGH / stats.total) * 100).toFixed(1)}%`} />
              </Card>
              <Card title="Medium Risk" className="flex flex-col items-center justify-center">
                <KPI label="" value={stats.byLevel.MEDIUM.toLocaleString()} color={RISK_COLORS.MEDIUM} subtext={`${((stats.byLevel.MEDIUM / stats.total) * 100).toFixed(1)}%`} />
              </Card>
              <Card title="Avg Score" className="flex flex-col items-center justify-center">
                <KPI label="" value={stats.avgScore.toFixed(2)} subtext={`Max: ${stats.maxScore.toFixed(2)}`} />
              </Card>
            </div>

            {/* Risk Distribution Pie + Top States */}
            <div className="grid md:grid-cols-2 gap-4">
              <Card title="Risk Level Distribution">
                <Explainer
                  question="How are PINs distributed across risk tiers?"
                  formula="Count of PINs per risk_level (CRITICAL ≥8, HIGH ≥6, MEDIUM ≥4, LOW <4)"
                  assumption="Risk levels are mutually exclusive and exhaustive."
                />
                <ResponsiveContainer width="100%" height={180}>
                  <PieChart>
                    <Pie
                      data={riskPieData}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={65}
                      label={({ name, percent }) => `${name} ${((percent ?? 0) * 100).toFixed(0)}%`}
                      labelLine={false}
                    >
                      {riskPieData.map((entry, i) => (
                        <Cell key={i} fill={entry.fill} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Card>

              <Card title="Top 5 High-Risk States">
                <Explainer
                  question="Which states have the highest average risk?"
                  formula="AVG(risk_score) grouped by state"
                  assumption="States with higher avg scores warrant deeper investigation."
                />
                <ResponsiveContainer width="100%" height={180}>
                  <BarChart data={topStates} layout="vertical" margin={{ left: 80 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis type="number" domain={[0, 10]} tick={{ fill: '#94a3b8', fontSize: 10 }} />
                    <YAxis type="category" dataKey="state" tick={{ fill: '#94a3b8', fontSize: 10 }} width={80} />
                    <Tooltip contentStyle={{ background: '#1e293b', border: 'none' }} />
                    <Bar dataKey="avg_risk_score" radius={[0, 4, 4, 0]}>
                      {topStates.map((s, i) => (
                        <Cell key={i} fill={s.avg_risk_score >= 8 ? RISK_COLORS.CRITICAL : s.avg_risk_score >= 6 ? RISK_COLORS.HIGH : '#6366f1'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </div>

            {/* Daily Trends */}
            <Card title="Daily Activity Trends (Last 30 Days)">
              <Explainer
                question="How does enrollment/update activity vary over time?"
                formula="SUM(enrollments), SUM(demo_updates), SUM(bio_updates) per day"
                assumption="Sudden spikes may indicate coordinated fraud."
              />
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={dailySampled}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="date" tickFormatter={(v) => v?.slice(5, 10) || ''} tick={{ fill: '#94a3b8', fontSize: 10 }} />
                  <YAxis tick={{ fill: '#94a3b8', fontSize: 10 }} />
                  <Tooltip contentStyle={{ background: '#1e293b', border: 'none' }} />
                  <Line type="monotone" dataKey="total_enrollments" name="Enrollments" stroke="#22c55e" dot={false} strokeWidth={2} />
                  <Line type="monotone" dataKey="total_demo_updates" name="Demo Updates" stroke="#eab308" dot={false} strokeWidth={2} />
                  <Line type="monotone" dataKey="total_bio_updates" name="Bio Updates" stroke="#6366f1" dot={false} strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
              <div className="flex gap-4 justify-center mt-2 text-xs">
                <span className="flex items-center gap-1"><span className="w-3 h-0.5 bg-[#22c55e] inline-block" /> Enrollments</span>
                <span className="flex items-center gap-1"><span className="w-3 h-0.5 bg-[#eab308] inline-block" /> Demo Updates</span>
                <span className="flex items-center gap-1"><span className="w-3 h-0.5 bg-[#6366f1] inline-block" /> Bio Updates</span>
              </div>
            </Card>
          </>
        )}

        {/* ===================== VELOCITIES ===================== */}
        {section === 'velocities' && (
          <>
            <Card title="Understanding Velocities">
              <div className="text-sm text-muted space-y-2">
                <p><strong>Velocity</strong> = PIN activity ÷ National Median. Value of <strong>1.0</strong> = national average. Higher = unusual.</p>
                <div className="grid grid-cols-3 gap-2 text-xs mt-3">
                  <div className="bg-surface p-2 rounded"><strong>Enrollment</strong>: New registrations (30% weight)</div>
                  <div className="bg-surface p-2 rounded"><strong>Update</strong>: Demographic changes (25% weight)</div>
                  <div className="bg-surface p-2 rounded"><strong>Bio</strong>: Biometric re-captures</div>
                </div>
              </div>
            </Card>

            {/* Velocity Scatter Plot */}
            <Card title="Enrollment vs Update Velocity">
              <Explainer
                question="Are high-enrollment PINs also high-update PINs?"
                formula="Scatter: enrollment_velocity (x) vs update_velocity (y)"
                assumption="Correlated high velocities suggest coordinated fraud."
              />
              <ResponsiveContainer width="100%" height={240}>
                <ScatterChart margin={{ bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="enrollment_velocity" name="Enrollment" tick={{ fill: '#94a3b8', fontSize: 10 }} />
                  <YAxis dataKey="update_velocity" name="Update" tick={{ fill: '#94a3b8', fontSize: 10 }} />
                  <Tooltip contentStyle={{ background: '#1e293b', border: 'none' }} formatter={(v) => typeof v === 'number' ? v.toFixed(2) : v} />
                  <Scatter data={scatterData} shape="circle">
                    {scatterData.map((d, i) => (
                      <Cell key={i} fill={RISK_COLORS[d.risk_level] || '#475569'} opacity={0.7} />
                    ))}
                  </Scatter>
                </ScatterChart>
              </ResponsiveContainer>
            </Card>

            {/* Bio Velocity vs Risk */}
            <Card title="Bio Velocity vs Risk Score">
              <Explainer
                question="Does biometric recapture frequency correlate with risk?"
                formula="Scatter: bio_velocity (x) vs risk_score (y)"
              />
              <ResponsiveContainer width="100%" height={200}>
                <ScatterChart>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="bio_velocity" tick={{ fill: '#94a3b8', fontSize: 10 }} />
                  <YAxis dataKey="risk_score" domain={[0, 10]} tick={{ fill: '#94a3b8', fontSize: 10 }} />
                  <Tooltip contentStyle={{ background: '#1e293b', border: 'none' }} />
                  <Scatter data={scatterData} fill="#14b8a6" opacity={0.6} />
                </ScatterChart>
              </ResponsiveContainer>
            </Card>
          </>
        )}

        {/* ===================== RISK SCORES ===================== */}
        {section === 'risk-scores' && (
          <>
            {/* Formula Explanation */}
            <Card title="Risk Score Formula">
              <div className="text-sm text-muted space-y-2">
                <pre className="bg-surface p-3 rounded text-xs overflow-x-auto">
{`Risk_Score (0-10) = 
  Enrollment_Velocity × 0.30 +
  Update_Velocity × 0.25 +
  Demographic_Anomaly × 0.20 +
  Geographic_Outlier × 0.15 +
  Temporal_Spike × 0.10`}
                </pre>
                <p className="mt-2"><strong>Thresholds:</strong> HIGH ≥ 6.0 | MEDIUM ≥ 4.0 | LOW &lt; 4.0</p>
              </div>
            </Card>

            {/* Risk Score Distribution */}
            <Card title="Risk Score Distribution">
              <Explainer
                question="How are composite risk scores distributed?"
                formula="Histogram of risk_score values (0-10)"
              />
              <ResponsiveContainer width="100%" height={180}>
                <AreaChart data={riskHist}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="mid" tickFormatter={(v) => v.toFixed(1)} tick={{ fill: '#94a3b8', fontSize: 10 }} />
                  <YAxis tick={{ fill: '#94a3b8', fontSize: 10 }} />
                  <Tooltip contentStyle={{ background: '#1e293b', border: 'none' }} />
                  <Area dataKey="count" stroke="#6366f1" fill="rgba(99,102,241,0.3)" />
                </AreaChart>
              </ResponsiveContainer>
            </Card>

            {/* Individual Component Distributions */}
            <div className="grid md:grid-cols-2 gap-4">
              {componentHistograms.map(({ key, info, data }) => (
                <Card key={key} title={`${info.label} (${info.weight})`}>
                  <p className="text-xs text-muted mb-2">{info.desc}</p>
                  <ResponsiveContainer width="100%" height={120}>
                    <BarChart data={data}>
                      <XAxis dataKey="mid" tickFormatter={(v) => v.toFixed(1)} tick={{ fill: '#94a3b8', fontSize: 9 }} />
                      <YAxis hide />
                      <Tooltip contentStyle={{ background: '#1e293b', border: 'none' }} />
                      <Bar dataKey="count" fill={info.color} radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </Card>
              ))}
            </div>

            {/* Component vs Risk Score Scatter */}
            <Card title="Risk Components vs Final Score">
              <Explainer
                question="Which components correlate most strongly with final risk?"
                formula="Scatter plot of each component vs risk_score"
              />
              <div className="grid md:grid-cols-2 gap-4">
                {/* Enrollment Velocity vs Score */}
                <div>
                  <p className="text-xs text-muted mb-1">Enrollment Velocity (30%)</p>
                  <ResponsiveContainer width="100%" height={140}>
                    <ScatterChart>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                      <XAxis dataKey="risk_enrollment_velocity" tick={{ fill: '#94a3b8', fontSize: 9 }} />
                      <YAxis dataKey="risk_score" domain={[0, 10]} tick={{ fill: '#94a3b8', fontSize: 9 }} />
                      <Tooltip contentStyle={{ background: '#1e293b', border: 'none' }} />
                      <Scatter data={scatterData} fill={COMPONENT_INFO.risk_enrollment_velocity.color} opacity={0.6} />
                    </ScatterChart>
                  </ResponsiveContainer>
                </div>
                {/* Update Velocity vs Score */}
                <div>
                  <p className="text-xs text-muted mb-1">Update Velocity (25%)</p>
                  <ResponsiveContainer width="100%" height={140}>
                    <ScatterChart>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                      <XAxis dataKey="risk_update_velocity" tick={{ fill: '#94a3b8', fontSize: 9 }} />
                      <YAxis dataKey="risk_score" domain={[0, 10]} tick={{ fill: '#94a3b8', fontSize: 9 }} />
                      <Tooltip contentStyle={{ background: '#1e293b', border: 'none' }} />
                      <Scatter data={scatterData} fill={COMPONENT_INFO.risk_update_velocity.color} opacity={0.6} />
                    </ScatterChart>
                  </ResponsiveContainer>
                </div>
                {/* Demographic Anomaly vs Score */}
                <div>
                  <p className="text-xs text-muted mb-1">Demographic Anomaly (20%)</p>
                  <ResponsiveContainer width="100%" height={140}>
                    <ScatterChart>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                      <XAxis dataKey="risk_demographic_anomaly" tick={{ fill: '#94a3b8', fontSize: 9 }} />
                      <YAxis dataKey="risk_score" domain={[0, 10]} tick={{ fill: '#94a3b8', fontSize: 9 }} />
                      <Tooltip contentStyle={{ background: '#1e293b', border: 'none' }} />
                      <Scatter data={scatterData} fill={COMPONENT_INFO.risk_demographic_anomaly.color} opacity={0.6} />
                    </ScatterChart>
                  </ResponsiveContainer>
                </div>
                {/* Geographic Outlier vs Score */}
                <div>
                  <p className="text-xs text-muted mb-1">Geographic Outlier (15%)</p>
                  <ResponsiveContainer width="100%" height={140}>
                    <ScatterChart>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                      <XAxis dataKey="risk_geographic_outlier" tick={{ fill: '#94a3b8', fontSize: 9 }} />
                      <YAxis dataKey="risk_score" domain={[0, 10]} tick={{ fill: '#94a3b8', fontSize: 9 }} />
                      <Tooltip contentStyle={{ background: '#1e293b', border: 'none' }} />
                      <Scatter data={scatterData} fill={COMPONENT_INFO.risk_geographic_outlier.color} opacity={0.6} />
                    </ScatterChart>
                  </ResponsiveContainer>
                </div>
              </div>
              {/* Temporal Spike - full width */}
              <div className="mt-4">
                <p className="text-xs text-muted mb-1">Temporal Spike (10%)</p>
                <ResponsiveContainer width="100%" height={140}>
                  <ScatterChart>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="risk_temporal_spike" tick={{ fill: '#94a3b8', fontSize: 9 }} />
                    <YAxis dataKey="risk_score" domain={[0, 10]} tick={{ fill: '#94a3b8', fontSize: 9 }} />
                    <Tooltip contentStyle={{ background: '#1e293b', border: 'none' }} />
                    <Scatter data={scatterData} fill={COMPONENT_INFO.risk_temporal_spike.color} opacity={0.6} />
                  </ScatterChart>
                </ResponsiveContainer>
              </div>
            </Card>
          </>
        )}

        {/* ===================== ALERTS ===================== */}
        {section === 'alerts' && (
          <>
            {/* Overall Risk Score */}
            {(() => {
              // Calculate overall risk out of 100
              // Based on: weighted combination of high-risk %, avg score, and alert density
              const highRiskPct = (stats.byLevel.HIGH / stats.total) * 100
              const mediumRiskPct = (stats.byLevel.MEDIUM / stats.total) * 100
              const avgScoreNorm = (stats.avgScore / 10) * 100
              const alertDensity = Math.min((alertsData.length / stats.total) * 1000, 100)
              
              // Overall = 40% high-risk weight + 20% medium + 25% avg score + 15% alerts
              const overallRisk = Math.round(
                highRiskPct * 0.4 + mediumRiskPct * 0.2 + avgScoreNorm * 0.25 + alertDensity * 0.15
              )
              const riskColor = overallRisk >= 50 ? '#ea580c' : overallRisk >= 25 ? '#ca8a04' : '#16a34a'
              
              return (
                <Card title="Overall System Risk Score">
                  <Explainer
                    question="What is the aggregate fraud risk across all PINs?"
                    formula="0.4×(HIGH%) + 0.2×(MEDIUM%) + 0.25×(AvgScore/10×100) + 0.15×(AlertDensity)"
                    assumption="Higher score = more systemic fraud risk across the network."
                  />
                  <div className="flex items-center justify-center gap-8 py-4">
                    <div className="text-center">
                      <p className="text-5xl font-bold" style={{ color: riskColor }}>{overallRisk}</p>
                      <p className="text-sm text-muted mt-1">out of 100</p>
                    </div>
                    <div className="text-left text-xs text-muted space-y-1 border-l border-border pl-4">
                      <p><span className="font-medium text-text">High Risk PINs:</span> {highRiskPct.toFixed(2)}%</p>
                      <p><span className="font-medium text-text">Medium Risk PINs:</span> {mediumRiskPct.toFixed(2)}%</p>
                      <p><span className="font-medium text-text">Avg Risk Score:</span> {stats.avgScore.toFixed(2)} / 10</p>
                      <p><span className="font-medium text-text">Total Alerts:</span> {alertsData.length}</p>
                    </div>
                  </div>
                  <div className="w-full bg-surface rounded-full h-3 mt-2">
                    <div
                      className="h-3 rounded-full transition-all"
                      style={{ width: `${overallRisk}%`, backgroundColor: riskColor }}
                    />
                  </div>
                  <p className="text-xs text-center text-muted mt-2">
                    {overallRisk < 25 ? '✅ Low systemic risk' : overallRisk < 50 ? '⚠️ Moderate risk - monitor closely' : '🚨 Elevated risk - investigation recommended'}
                  </p>
                </Card>
              )
            })()}

            <Card title="Recent Fraud Alerts">
              <Explainer
                question="Which PINs have triggered IOC (Indicator of Compromise) alerts?"
                formula="Filtered from ioc_catalogue.csv or alerts.csv"
                assumption="Each alert represents a detected anomaly pattern."
              />
              {recentAlerts.length === 0 ? (
                <p className="text-muted text-sm">No alerts found.</p>
              ) : (
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {recentAlerts.map((a, i) => (
                    <div key={i} className="flex items-center justify-between p-3 bg-surface rounded">
                      <div>
                        <p className="font-medium text-sm">{a.pincode} – {a.district}, {a.state}</p>
                        <p className="text-xs text-muted">{a.pattern_name || 'Unknown pattern'}</p>
                      </div>
                      <div className="text-right">
                        <RiskBadge level={a.risk_level || 'LOW'} />
                        <p className="text-xs text-muted mt-1">{a.date_detected || '—'}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card>

            {/* Alerts by Level */}
            <Card title="Alerts by Risk Level">
              <Explainer
                question="How are alerts distributed across severity tiers?"
                formula="COUNT(*) GROUP BY risk_level"
              />
              {(() => {
                const counts = ['HIGH', 'MEDIUM', 'LOW'].map((level) => ({
                  level,
                  count: alertsData.filter((a) => a.risk_level === level).length,
                }))
                return (
                  <ResponsiveContainer width="100%" height={160}>
                    <BarChart data={counts}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                      <XAxis dataKey="level" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                      <YAxis tick={{ fill: '#94a3b8', fontSize: 10 }} />
                      <Tooltip contentStyle={{ background: '#1e293b', border: 'none' }} />
                      <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                        {counts.map((c, i) => (
                          <Cell key={i} fill={RISK_COLORS[c.level]} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                )
              })()}
            </Card>
          </>
        )}
      </main>

      <footer className="border-t border-border py-3 mt-6">
        <p className="text-center text-xs text-muted">Aadhaar Fraud Analytics — Explainable AI for SOC Teams</p>
      </footer>
    </div>
  )
}
