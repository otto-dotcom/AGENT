import { useState, useEffect } from 'react'
import axios from 'axios'
import {
  Users,
  Mail,
  MessageSquare,
  TrendingUp,
  Calendar,
  CheckCircle,
  XCircle,
  Clock
} from 'lucide-react'

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await axios.get('/api/analytics/overview')
      setStats(response.data)
      setLoading(false)
    } catch (error) {
      console.error('Failed to fetch stats:', error)
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  const statCards = [
    {
      name: 'Total Leads',
      value: stats?.total_leads || 0,
      icon: Users,
      color: 'bg-blue-500',
      change: '+12%',
    },
    {
      name: 'Emails Sent',
      value: stats?.conversion_metrics?.email_sent || 0,
      icon: Mail,
      color: 'bg-green-500',
      change: '+23%',
    },
    {
      name: 'SMS Sent',
      value: stats?.conversion_metrics?.sms_sent || 0,
      icon: MessageSquare,
      color: 'bg-purple-500',
      change: '+8%',
    },
    {
      name: 'Response Rate',
      value: `${stats?.response_rate || 0}%`,
      icon: TrendingUp,
      color: 'bg-orange-500',
      change: '+2.4%',
    },
  ]

  const statusBreakdown = stats?.by_status || {}
  const recentActivity = [
    { action: 'Email campaign launched', time: '2 hours ago', status: 'success' },
    { action: 'Lead responded - Interested', time: '3 hours ago', status: 'success' },
    { action: 'SMS campaign completed', time: '5 hours ago', status: 'success' },
    { action: 'New leads imported', time: '1 day ago', status: 'info' },
  ]

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Welcome back! Here's what's happening with your campaigns.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 mb-8 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat) => (
          <div
            key={stat.name}
            className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                <p className="mt-2 text-3xl font-bold text-gray-900">{stat.value}</p>
              </div>
              <div className={`${stat.color} p-3 rounded-lg`}>
                <stat.icon className="w-6 h-6 text-white" />
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm">
              <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
              <span className="text-green-600 font-medium">{stat.change}</span>
              <span className="text-gray-500 ml-2">vs last month</span>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Status Breakdown */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Lead Status Breakdown
          </h2>
          <div className="space-y-3">
            {Object.entries(statusBreakdown).map(([status, count]) => (
              <div key={status} className="flex items-center justify-between">
                <div className="flex items-center">
                  {status.includes('Interested') ? (
                    <CheckCircle className="w-5 h-5 text-green-500 mr-3" />
                  ) : status.includes('Not Interested') ? (
                    <XCircle className="w-5 h-5 text-red-500 mr-3" />
                  ) : (
                    <Clock className="w-5 h-5 text-gray-400 mr-3" />
                  )}
                  <span className="text-sm text-gray-700">{status}</span>
                </div>
                <span className="text-sm font-medium text-gray-900">{count}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Recent Activity
          </h2>
          <div className="space-y-4">
            {recentActivity.map((activity, idx) => (
              <div key={idx} className="flex items-start">
                <div className={`flex-shrink-0 w-2 h-2 mt-2 rounded-full ${
                  activity.status === 'success' ? 'bg-green-500' : 'bg-blue-500'
                }`} />
                <div className="ml-4 flex-1">
                  <p className="text-sm text-gray-900">{activity.action}</p>
                  <p className="text-xs text-gray-500 mt-1">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-8 bg-gradient-to-r from-primary-600 to-primary-700 rounded-lg shadow-lg p-8">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-2xl font-bold text-white mb-2">
              Ready to launch your next campaign?
            </h3>
            <p className="text-primary-100">
              Select your leads, choose a template, and start engaging!
            </p>
          </div>
          <button
            onClick={() => window.location.href = '/campaigns/launch'}
            className="bg-white text-primary-600 px-6 py-3 rounded-lg font-semibold hover:bg-primary-50 transition-colors"
          >
            Launch Campaign
          </button>
        </div>
      </div>
    </div>
  )
}
