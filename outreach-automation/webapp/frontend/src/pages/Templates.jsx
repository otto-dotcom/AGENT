import { useState, useEffect } from 'react'
import axios from 'axios'
import { Mail, MessageSquare, Eye, Edit } from 'lucide-react'

export default function Templates() {
  const [emailTemplates, setEmailTemplates] = useState([])
  const [smsTemplates, setSmsTemplates] = useState([])
  const [activeTab, setActiveTab] = useState('email')
  const [previewTemplate, setPreviewTemplate] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchTemplates()
  }, [])

  const fetchTemplates = async () => {
    setLoading(true)
    try {
      const [emailRes, smsRes] = await Promise.all([
        axios.get('/api/templates/email'),
        axios.get('/api/templates/sms')
      ])

      setEmailTemplates(emailRes.data.templates || [])
      setSmsTemplates(smsRes.data.templates || [])
    } catch (error) {
      console.error('Failed to fetch templates:', error)
    }
    setLoading(false)
  }

  const handlePreview = (template) => {
    setPreviewTemplate(template)
  }

  const templates = activeTab === 'email' ? emailTemplates : smsTemplates

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Templates</h1>
        <p className="mt-2 text-gray-600">
          Manage your email and SMS templates
        </p>
      </div>

      {/* Tabs */}
      <div className="mb-6">
        <div className="flex space-x-4 border-b border-gray-200">
          <button
            onClick={() => setActiveTab('email')}
            className={`flex items-center px-4 py-3 font-medium border-b-2 transition-colors ${
              activeTab === 'email'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            <Mail className="w-5 h-5 mr-2" />
            Email Templates ({emailTemplates.length})
          </button>
          <button
            onClick={() => setActiveTab('sms')}
            className={`flex items-center px-4 py-3 font-medium border-b-2 transition-colors ${
              activeTab === 'sms'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            <MessageSquare className="w-5 h-5 mr-2" />
            SMS Templates ({smsTemplates.length})
          </button>
        </div>
      </div>

      {/* Templates Grid */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {templates.map((template) => (
            <div
              key={template.id}
              className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">
                    {template.name}
                  </h3>
                  <div className="flex items-center space-x-3 text-sm text-gray-600">
                    <span className="px-2 py-1 bg-gray-100 rounded">
                      {template.type}
                    </span>
                    {template.tone && (
                      <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded">
                        {template.tone}
                      </span>
                    )}
                    {template.character_count && (
                      <span className="text-gray-500">
                        {template.character_count} chars
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Template Preview */}
              <div className="mb-4">
                {activeTab === 'email' && template.subject_lines && (
                  <div className="mb-3">
                    <p className="text-xs font-medium text-gray-500 uppercase mb-1">
                      Subject Lines
                    </p>
                    <p className="text-sm text-gray-900">
                      {template.subject_lines[0]}
                    </p>
                  </div>
                )}

                <div>
                  <p className="text-xs font-medium text-gray-500 uppercase mb-1">
                    Body
                  </p>
                  <p className="text-sm text-gray-700 line-clamp-4">
                    {template.body}
                  </p>
                </div>
              </div>

              {/* Actions */}
              <div className="flex space-x-2 pt-4 border-t border-gray-200">
                <button
                  onClick={() => handlePreview(template)}
                  className="flex-1 flex items-center justify-center px-4 py-2 text-sm font-medium text-primary-600 bg-primary-50 rounded-lg hover:bg-primary-100"
                >
                  <Eye className="w-4 h-4 mr-2" />
                  Preview
                </button>
                <button className="flex-1 flex items-center justify-center px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200">
                  <Edit className="w-4 h-4 mr-2" />
                  Edit
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Preview Modal */}
      {previewTemplate && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto p-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900">
                {previewTemplate.name}
              </h2>
              <button
                onClick={() => setPreviewTemplate(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {activeTab === 'email' && previewTemplate.subject_lines && (
              <div className="mb-6">
                <h3 className="font-semibold text-gray-900 mb-3">Subject Lines:</h3>
                <ul className="space-y-2">
                  {previewTemplate.subject_lines.map((subject, idx) => (
                    <li key={idx} className="text-gray-700 pl-4 border-l-2 border-primary-600">
                      {subject}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div>
              <h3 className="font-semibold text-gray-900 mb-3">Body:</h3>
              <div className="bg-gray-50 rounded-lg p-4 whitespace-pre-wrap text-gray-700">
                {previewTemplate.body}
              </div>
            </div>

            <button
              onClick={() => setPreviewTemplate(null)}
              className="mt-6 w-full bg-primary-600 text-white py-3 rounded-lg font-semibold hover:bg-primary-700"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
