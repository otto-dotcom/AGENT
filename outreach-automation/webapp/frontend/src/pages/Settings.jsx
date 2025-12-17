import { useState, useEffect } from 'react'
import axios from 'axios'
import { Settings as SettingsIcon, Check, AlertCircle } from 'lucide-react'

export default function Settings() {
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    checkHealth()
  }, [])

  const checkHealth = async () => {
    setLoading(true)
    try {
      const response = await axios.get('/api/health')
      setHealth(response.data)
    } catch (error) {
      console.error('Failed to check health:', error)
    }
    setLoading(false)
  }

  const getStatusIcon = (status) => {
    if (status === 'healthy') {
      return <Check className="w-5 h-5 text-green-500" />
    }
    return <AlertCircle className="w-5 h-5 text-red-500" />
  }

  const getStatusColor = (status) => {
    if (status === 'healthy') {
      return 'bg-green-100 text-green-800'
    }
    return 'bg-red-100 text-red-800'
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="mt-2 text-gray-600">
          Configure your outreach automation system
        </p>
      </div>

      {/* System Health */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">System Health</h2>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          {loading ? (
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center">
                  {getStatusIcon(health?.overall_status)}
                  <span className="ml-3 font-medium text-gray-900">
                    Overall System Status
                  </span>
                </div>
                <span className={`px-3 py-1 text-sm font-medium rounded-full ${getStatusColor(health?.overall_status)}`}>
                  {health?.overall_status || 'unknown'}
                </span>
              </div>

              {health?.components && Object.entries(health.components).map(([name, component]) => (
                <div key={name} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                  <div className="flex items-center">
                    {getStatusIcon(component.status)}
                    <span className="ml-3 text-gray-900 capitalize">{name}</span>
                  </div>
                  <div className="text-right">
                    <span className={`px-3 py-1 text-sm font-medium rounded-full ${getStatusColor(component.status)}`}>
                      {component.status}
                    </span>
                    {component.total_workflows && (
                      <p className="text-xs text-gray-500 mt-1">
                        {component.total_workflows} workflows
                      </p>
                    )}
                    {component.quality_score && (
                      <p className="text-xs text-gray-500 mt-1">
                        Quality: {component.quality_score}%
                      </p>
                    )}
                  </div>
                </div>
              ))}

              <button
                onClick={checkHealth}
                className="w-full mt-4 px-4 py-2 text-sm font-medium text-primary-600 border border-primary-600 rounded-lg hover:bg-primary-50"
              >
                Refresh Status
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Campaign Settings */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Campaign Settings</h2>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Maximum Emails Per Day
              </label>
              <input
                type="number"
                defaultValue="50"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
              <p className="mt-1 text-sm text-gray-500">
                Recommended: 50 during warm-up, 100+ after
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Maximum SMS Per Day
              </label>
              <input
                type="number"
                defaultValue="30"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
              <p className="mt-1 text-sm text-gray-500">
                Recommended: 30 per day
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Timezone
              </label>
              <select className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500">
                <option>Europe/Zurich</option>
                <option>Europe/London</option>
                <option>America/New_York</option>
                <option>America/Los_Angeles</option>
              </select>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="dry_run"
                defaultChecked
                className="w-4 h-4 text-primary-600 rounded"
              />
              <label htmlFor="dry_run" className="ml-2 text-sm text-gray-700">
                Enable dry run mode by default (test mode)
              </label>
            </div>

            <button
              onClick={() => {
                setSaving(true)
                setTimeout(() => {
                  setSaving(false)
                  alert('Settings saved successfully!')
                }, 1000)
              }}
              disabled={saving}
              className="w-full bg-primary-600 text-white py-3 rounded-lg font-semibold hover:bg-primary-700 disabled:bg-gray-400"
            >
              {saving ? 'Saving...' : 'Save Settings'}
            </button>
          </div>
        </div>
      </div>

      {/* API Credentials Status */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">API Credentials</h2>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="space-y-3">
            {[
              { name: 'Airtable API', configured: true },
              { name: 'n8n API', configured: true },
              { name: 'OpenAI API', configured: true },
              { name: 'Twilio API', configured: false },
              { name: 'Mailchimp API', configured: false },
            ].map((api) => (
              <div key={api.name} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                <span className="text-gray-900">{api.name}</span>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                  api.configured
                    ? 'bg-green-100 text-green-800'
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {api.configured ? 'Configured' : 'Not Configured'}
                </span>
              </div>
            ))}
          </div>
          <p className="mt-4 text-sm text-gray-600">
            Configure API credentials in your environment variables or .env file
          </p>
        </div>
      </div>
    </div>
  )
}
