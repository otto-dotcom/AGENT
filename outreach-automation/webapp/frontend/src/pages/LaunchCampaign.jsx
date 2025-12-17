import { useState, useEffect } from 'react'
import axios from 'axios'
import { Rocket, Users, Mail, MessageSquare, Calendar, AlertCircle } from 'lucide-react'

export default function LaunchCampaign() {
  const [step, setStep] = useState(1)
  const [campaignData, setCampaignData] = useState({
    campaign_name: '',
    campaign_type: 'email',
    template_id: '',
    lead_ids: [],
    schedule_time: null,
    dry_run: true,
  })

  const [leads, setLeads] = useState([])
  const [templates, setTemplates] = useState([])
  const [selectedLeads, setSelectedLeads] = useState([])
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    fetchLeads()
    fetchTemplates()
  }, [])

  const fetchLeads = async () => {
    try {
      const response = await axios.get('/api/leads', {
        params: { status: 'Enriched', limit: 1000 }
      })
      setLeads(response.data.leads)
    } catch (error) {
      console.error('Failed to fetch leads:', error)
    }
  }

  const fetchTemplates = async () => {
    try {
      const emailRes = await axios.get('/api/templates/email')
      const smsRes = await axios.get('/api/templates/sms')

      setTemplates({
        email: emailRes.data.templates,
        sms: smsRes.data.templates,
      })
    } catch (error) {
      console.error('Failed to fetch templates:', error)
    }
  }

  const handleLaunch = async () => {
    setLoading(true)
    try {
      const response = await axios.post('/api/campaigns/launch', {
        ...campaignData,
        lead_ids: selectedLeads.map(l => l.id),
      })

      setSuccess(true)
      setTimeout(() => {
        window.location.href = '/campaigns'
      }, 2000)
    } catch (error) {
      console.error('Failed to launch campaign:', error)
      alert('Failed to launch campaign. Please try again.')
    }
    setLoading(false)
  }

  const toggleLead = (lead) => {
    if (selectedLeads.find(l => l.id === lead.id)) {
      setSelectedLeads(selectedLeads.filter(l => l.id !== lead.id))
    } else {
      setSelectedLeads([...selectedLeads, lead])
    }
  }

  const selectAll = () => {
    setSelectedLeads(leads)
  }

  const clearSelection = () => {
    setSelectedLeads([])
  }

  if (success) {
    return (
      <div className="flex flex-col items-center justify-center h-96">
        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
          <Rocket className="w-8 h-8 text-green-600" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Campaign Launched!</h2>
        <p className="text-gray-600">Redirecting to campaigns page...</p>
      </div>
    )
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Launch Campaign</h1>
        <p className="mt-2 text-gray-600">
          Create and launch a new outreach campaign
        </p>
      </div>

      {/* Progress Steps */}
      <div className="mb-8">
        <div className="flex items-center justify-between max-w-2xl mx-auto">
          {[1, 2, 3, 4].map((s) => (
            <div key={s} className="flex items-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${
                step >= s
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-200 text-gray-600'
              }`}>
                {s}
              </div>
              {s < 4 && (
                <div className={`h-1 w-24 mx-2 ${
                  step > s ? 'bg-primary-600' : 'bg-gray-200'
                }`} />
              )}
            </div>
          ))}
        </div>
        <div className="flex justify-between max-w-2xl mx-auto mt-2 text-sm text-gray-600">
          <span>Campaign Type</span>
          <span>Select Leads</span>
          <span>Choose Template</span>
          <span>Review & Launch</span>
        </div>
      </div>

      {/* Step Content */}
      <div className="max-w-4xl mx-auto">
        {step === 1 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
            <h2 className="text-xl font-semibold mb-6">Campaign Details</h2>

            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Campaign Name
                </label>
                <input
                  type="text"
                  value={campaignData.campaign_name}
                  onChange={(e) => setCampaignData({...campaignData, campaign_name: e.target.value})}
                  placeholder="e.g., Q4 Tech Outreach"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Campaign Type
                </label>
                <div className="grid grid-cols-3 gap-4">
                  {[
                    { value: 'email', icon: Mail, label: 'Email Only' },
                    { value: 'sms', icon: MessageSquare, label: 'SMS Only' },
                    { value: 'both', icon: Users, label: 'Email + SMS' },
                  ].map((type) => (
                    <button
                      key={type.value}
                      onClick={() => setCampaignData({...campaignData, campaign_type: type.value})}
                      className={`p-6 border-2 rounded-lg flex flex-col items-center ${
                        campaignData.campaign_type === type.value
                          ? 'border-primary-600 bg-primary-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <type.icon className="w-8 h-8 mb-2" />
                      <span className="font-medium">{type.label}</span>
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  checked={campaignData.dry_run}
                  onChange={(e) => setCampaignData({...campaignData, dry_run: e.target.checked})}
                  className="w-4 h-4 text-primary-600 rounded"
                />
                <label className="ml-2 text-sm text-gray-700">
                  Dry run mode (test without actually sending)
                </label>
              </div>
            </div>

            <button
              onClick={() => setStep(2)}
              disabled={!campaignData.campaign_name}
              className="mt-8 w-full bg-primary-600 text-white py-3 rounded-lg font-semibold hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              Continue to Lead Selection
            </button>
          </div>
        )}

        {step === 2 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold">Select Leads</h2>
              <div className="space-x-2">
                <button
                  onClick={selectAll}
                  className="px-4 py-2 text-sm text-primary-600 border border-primary-600 rounded-lg hover:bg-primary-50"
                >
                  Select All
                </button>
                <button
                  onClick={clearSelection}
                  className="px-4 py-2 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Clear
                </button>
              </div>
            </div>

            <div className="mb-4 text-sm text-gray-600">
              {selectedLeads.length} of {leads.length} leads selected
            </div>

            <div className="max-h-96 overflow-y-auto border border-gray-200 rounded-lg">
              {leads.map((lead) => (
                <div
                  key={lead.id}
                  onClick={() => toggleLead(lead)}
                  className={`p-4 border-b cursor-pointer hover:bg-gray-50 ${
                    selectedLeads.find(l => l.id === lead.id) ? 'bg-primary-50' : ''
                  }`}
                >
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      checked={!!selectedLeads.find(l => l.id === lead.id)}
                      onChange={() => {}}
                      className="mr-3"
                    />
                    <div className="flex-1">
                      <p className="font-medium">{lead.fields['Company Name']}</p>
                      <p className="text-sm text-gray-600">{lead.fields['Contact Person']} • {lead.fields['Email']}</p>
                    </div>
                    <span className="text-sm text-gray-500">{lead.fields['Industry']}</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-8 flex space-x-4">
              <button
                onClick={() => setStep(1)}
                className="flex-1 bg-gray-100 text-gray-700 py-3 rounded-lg font-semibold hover:bg-gray-200"
              >
                Back
              </button>
              <button
                onClick={() => setStep(3)}
                disabled={selectedLeads.length === 0}
                className="flex-1 bg-primary-600 text-white py-3 rounded-lg font-semibold hover:bg-primary-700 disabled:bg-gray-300"
              >
                Continue to Templates
              </button>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
            <h2 className="text-xl font-semibold mb-6">Choose Template</h2>

            <div className="space-y-4">
              {(templates[campaignData.campaign_type] || templates.email || []).map((template) => (
                <div
                  key={template.id}
                  onClick={() => setCampaignData({...campaignData, template_id: template.id})}
                  className={`p-6 border-2 rounded-lg cursor-pointer ${
                    campaignData.template_id === template.id
                      ? 'border-primary-600 bg-primary-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <h3 className="font-semibold text-lg mb-2">{template.name}</h3>
                  <p className="text-sm text-gray-600 mb-4">{template.type}</p>
                  <div className="text-sm text-gray-700">
                    {template.subject_lines && (
                      <p className="mb-2"><strong>Subject:</strong> {template.subject_lines[0]}</p>
                    )}
                    <p className="text-gray-600 line-clamp-2">{template.body?.substring(0, 200)}...</p>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-8 flex space-x-4">
              <button
                onClick={() => setStep(2)}
                className="flex-1 bg-gray-100 text-gray-700 py-3 rounded-lg font-semibold hover:bg-gray-200"
              >
                Back
              </button>
              <button
                onClick={() => setStep(4)}
                disabled={!campaignData.template_id}
                className="flex-1 bg-primary-600 text-white py-3 rounded-lg font-semibold hover:bg-primary-700 disabled:bg-gray-300"
              >
                Review Campaign
              </button>
            </div>
          </div>
        )}

        {step === 4 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
            <h2 className="text-xl font-semibold mb-6">Review & Launch</h2>

            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Campaign Name</p>
                  <p className="font-semibold">{campaignData.campaign_name}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">Campaign Type</p>
                  <p className="font-semibold capitalize">{campaignData.campaign_type}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">Number of Leads</p>
                  <p className="font-semibold">{selectedLeads.length}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">Mode</p>
                  <p className="font-semibold">{campaignData.dry_run ? 'Dry Run (Test)' : 'Live'}</p>
                </div>
              </div>

              {campaignData.dry_run && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-start">
                  <AlertCircle className="w-5 h-5 text-yellow-600 mr-3 mt-0.5" />
                  <div>
                    <p className="font-medium text-yellow-900">Dry Run Mode</p>
                    <p className="text-sm text-yellow-700 mt-1">
                      No emails or SMS will actually be sent. This is a test run to verify everything works.
                    </p>
                  </div>
                </div>
              )}

              <div className="border-t pt-6">
                <h3 className="font-semibold mb-4">Campaign Summary</h3>
                <ul className="space-y-2 text-sm text-gray-700">
                  <li>• {selectedLeads.length} leads will be contacted</li>
                  <li>• Using template: {campaignData.template_id}</li>
                  <li>• Campaign will {campaignData.dry_run ? 'run in test mode' : 'send live messages'}</li>
                  <li>• Estimated completion: {Math.ceil(selectedLeads.length * 2 / 60)} minutes</li>
                </ul>
              </div>
            </div>

            <div className="mt-8 flex space-x-4">
              <button
                onClick={() => setStep(3)}
                className="flex-1 bg-gray-100 text-gray-700 py-3 rounded-lg font-semibold hover:bg-gray-200"
              >
                Back
              </button>
              <button
                onClick={handleLaunch}
                disabled={loading}
                className="flex-1 bg-primary-600 text-white py-3 rounded-lg font-semibold hover:bg-primary-700 disabled:bg-gray-400 flex items-center justify-center"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Launching...
                  </>
                ) : (
                  <>
                    <Rocket className="w-5 h-5 mr-2" />
                    Launch Campaign
                  </>
                )}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
