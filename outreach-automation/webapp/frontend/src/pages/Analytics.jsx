import { useState, useEffect } from 'react'
import axios from 'axios'
import { TrendingUp, Users, Mail, MessageSquare, Target } from 'lucide-react'

export default function Analytics() {
  const [analytics, setAnalytics] = useState(null)
  const [byStatus, setByStatus] = useState({})
  const [byIndustry, setByIndustry] = useState({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAnalytics()
  }, [])

  const fetchAnalytics = async () => {
    setLoading(true)
    try {
      const [overviewRes, statusRes, industryRes] = await Promise.all([
        axios.get('/api/analytics/overview'),
        axios.get('/api/analytics/by-status'),
        axios.get('/api/analytics/by-industry')
      ])

      setAnalytics(overviewRes.data)
      setByStatus(statusRes.data.by_status || {})
      setByIndustry(industryRes.data.by_industry || {})
    } catch (error) {
      console.error('Failed to fetch analytics:', error)
    }
    setLoading(false)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  const metrics = [
    {
      name: 'Total Leads',
      value: analytics?.total_leads || 0,
      icon: Users,
      color: 'bg-blue-500',
    },
    {
      name: 'Emails Sent',
      value: analytics?.conversion_metrics?.email_sent || 0,
      icon: Mail,
      color: 'bg-green-500',
    },
    {
      name: 'SMS Sent',
      value: analytics?.conversion_metrics?.sms_sent || 0,
      icon: MessageSquare,
      color: 'bg-purple-500',
    },
    {
      name: 'Responses',
      value: analytics?.conversion_metrics?.responded || 0,
      icon: TrendingUp,
      color: 'bg-orange-500',
    },
  ]

  const conversionMetrics = [
    {
      name: 'Response Rate',
      value: `${analytics?.response_rate || 0}%`,
      description: 'Leads that responded',
      target: '5%',
      achieved: (analytics?.response_rate || 0) >= 5,
    },
    {
      name: 'Meeting Conversion',
      value: `${analytics?.meeting_conversion_rate || 0}%`,
      description: 'Leads that booked meetings',
      target: '1%',
      achieved: (analytics?.meeting_conversion_rate || 0) >= 1,
    },
  ]

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
        <p className="mt-2 text-gray-600">
          Track your campaign performance and metrics
        </p>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 gap-6 mb-8 sm:grid-cols-2 lg:grid-cols-4">
        {metrics.map((metric) => (
          <div
            key={metric.name}
            className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{metric.name}</p>
                <p className="mt-2 text-3xl font-bold text-gray-900">{metric.value}</p>
              </div>
              <div className={`${metric.color} p-3 rounded-lg`}>
                <metric.icon className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Conversion Metrics */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Conversion Metrics</h2>
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {conversionMetrics.map((metric) => (
            <div
              key={metric.name}
              className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{metric.name}</h3>
                  <p className="text-sm text-gray-600">{metric.description}</p>
                </div>
                <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                  metric.achieved
                    ? 'bg-green-100 text-green-800'
                    : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {metric.achieved ? 'Target Met' : 'Below Target'}
                </div>
              </div>
              <div className="flex items-end justify-between">
                <div className="text-4xl font-bold text-gray-900">{metric.value}</div>
                <div className="text-sm text-gray-600">Target: {metric.target}</div>
              </div>
              <div className="mt-4 w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${metric.achieved ? 'bg-green-500' : 'bg-yellow-500'}`}
                  style={{ width: `${Math.min((parseFloat(metric.value) / parseFloat(metric.target)) * 100, 100)}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* By Status */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Leads by Status</h2>
          <div className="space-y-4">
            {Object.entries(byStatus).map(([status, count]) => {
              const total = analytics?.total_leads || 1
              const percentage = ((count / total) * 100).toFixed(1)
              return (
                <div key={status}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">{status}</span>
                    <span className="text-sm text-gray-600">{count} ({percentage}%)</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="h-2 rounded-full bg-primary-600"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* By Industry */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Leads by Industry</h2>
          <div className="space-y-4">
            {Object.entries(byIndustry).sort((a, b) => b[1] - a[1]).slice(0, 5).map(([industry, count]) => {
              const total = analytics?.total_leads || 1
              const percentage = ((count / total) * 100).toFixed(1)
              return (
                <div key={industry}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">{industry}</span>
                    <span className="text-sm text-gray-600">{count} ({percentage}%)</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="h-2 rounded-full bg-purple-600"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}
