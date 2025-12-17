# Project: Add Automated Campaigns System to JarvisBot

## 🎯 Project Overview

**Objective**: Integrate a complete automated outreach campaigns system into JarvisBot central command, enabling users to manage email/SMS campaigns, leads, templates, and analytics from their existing dashboard.

**Context**: JarvisBot is a central command application where users manage AI chat, stores, automations, and agents. This project adds a "Campaigns" section that unifies outreach automation into the same interface.

**Target Repository**: `otto-dotcom/jarvisbot` (Lovable deployment)

**Backend API**: `http://localhost:8000` (or configure via environment variable)

---

## 🏗️ Architecture

### System Components

```
JarvisBot (Frontend - React)
    ↓ HTTP/REST
Backend API (FastAPI)
    ↓ JSON Payload
n8n Workflows (n8n.cloud)
    ↓ Webhooks
Airtable Database (Kronos)
    ↓ Data
Email/SMS Services (Mailchimp/Twilio)
```

### Tech Stack
- **Frontend**: React 18, React Router, Lucide React icons
- **Styling**: Tailwind CSS (assume already configured)
- **API Client**: Fetch API with error handling
- **State Management**: React hooks (useState, useEffect)
- **Backend**: FastAPI (separate service)

---

## 📁 File Structure to Create

Create these files in the JarvisBot repository:

```
jarvisbot/
├── src/
│   ├── pages/campaigns/
│   │   ├── Dashboard.jsx          # Campaign metrics overview
│   │   ├── Leads.jsx              # Lead management table
│   │   ├── LaunchCampaign.jsx     # 4-step campaign wizard
│   │   ├── ActiveCampaigns.jsx    # Monitor running campaigns
│   │   ├── Templates.jsx          # Email/SMS template library
│   │   └── Analytics.jsx          # Performance analytics
│   ├── api/
│   │   └── outreachAPI.js         # API client for backend
│   └── components/
│       └── campaigns/
│           ├── CampaignCard.jsx       # Campaign status card
│           ├── LeadTable.jsx          # Reusable lead table
│           ├── TemplateCard.jsx       # Template preview card
│           ├── MetricCard.jsx         # Dashboard metric card
│           └── CampaignWizard.jsx     # Multi-step wizard component
└── .env (add)
    └── VITE_OUTREACH_API_URL=http://localhost:8000
```

---

## 🎨 Design System

### Colors (use existing JarvisBot theme if available, otherwise use these)
```css
Primary Blue: #3B82F6
Success Green: #10B981
Warning Yellow: #F59E0B
Danger Red: #EF4444
Gray 50: #F9FAFB
Gray 100: #F3F4F6
Gray 200: #E5E7EB
Gray 600: #4B5563
Gray 900: #111827
```

### Icons (Lucide React)
- Mail, MessageSquare, Users, TrendingUp, BarChart3, Settings, Filter, Search, Plus, Send, Eye, CheckCircle, Clock, AlertCircle

### Layout Patterns
- Cards with shadow: `shadow-md rounded-lg p-6`
- Tables with hover: `hover:bg-gray-50 transition-colors`
- Buttons: `px-4 py-2 rounded-lg font-medium`
- Status badges: `px-2 py-1 rounded-full text-xs font-medium`

---

## 📋 Implementation Steps

### Step 1: Add Navigation to JarvisBot

**Location**: Find the sidebar/navigation component in JarvisBot

**Add this menu item**:
```jsx
{
  icon: <Mail className="w-5 h-5" />,
  label: "Campaigns",
  href: "/campaigns",
  children: [
    { label: "Dashboard", href: "/campaigns/dashboard" },
    { label: "Leads", href: "/campaigns/leads" },
    { label: "Launch", href: "/campaigns/launch" },
    { label: "Active", href: "/campaigns/active" },
    { label: "Templates", href: "/campaigns/templates" },
    { label: "Analytics", href: "/campaigns/analytics" }
  ]
}
```

### Step 2: Create API Client

**File**: `src/api/outreachAPI.js`

```javascript
const API_BASE_URL = import.meta.env.VITE_OUTREACH_API_URL || 'http://localhost:8000';

async function apiRequest(endpoint, options = {}) {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API Request Failed: ${endpoint}`, error);
    throw error;
  }
}

export const outreachAPI = {
  getLeads: async (filters = {}) => {
    const queryParams = new URLSearchParams(filters).toString();
    const endpoint = queryParams ? `/api/leads?${queryParams}` : '/api/leads';
    return apiRequest(endpoint);
  },

  getLead: async (leadId) => {
    return apiRequest(`/api/leads/${leadId}`);
  },

  getTemplates: async () => {
    return apiRequest('/api/templates');
  },

  launchCampaign: async (campaignData) => {
    return apiRequest('/api/campaigns/launch', {
      method: 'POST',
      body: JSON.stringify(campaignData),
    });
  },

  getCampaigns: async () => {
    return apiRequest('/api/campaigns');
  },

  getAnalytics: async () => {
    return apiRequest('/api/analytics');
  },

  getHealth: async () => {
    return apiRequest('/health');
  },
};

export default outreachAPI;
```

### Step 3: Create Dashboard Page

**File**: `src/pages/campaigns/Dashboard.jsx`

```jsx
import React, { useState, useEffect } from 'react';
import { Users, Mail, MessageSquare, TrendingUp, Activity } from 'lucide-react';
import { outreachAPI } from '../../api/outreachAPI';

export default function CampaignsDashboard() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      const data = await outreachAPI.getAnalytics();
      setAnalytics(data);
    } catch (error) {
      console.error('Failed to load analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-8">Loading...</div>;
  }

  const metrics = [
    {
      label: 'Total Leads',
      value: analytics?.total_leads || 0,
      icon: Users,
      color: 'blue',
      bgColor: 'bg-blue-100',
      textColor: 'text-blue-600'
    },
    {
      label: 'Emails Sent',
      value: analytics?.emails_sent || 0,
      icon: Mail,
      color: 'green',
      bgColor: 'bg-green-100',
      textColor: 'text-green-600'
    },
    {
      label: 'SMS Sent',
      value: analytics?.sms_sent || 0,
      icon: MessageSquare,
      color: 'purple',
      bgColor: 'bg-purple-100',
      textColor: 'text-purple-600'
    },
    {
      label: 'Response Rate',
      value: `${Math.round((analytics?.response_rate || 0) * 100)}%`,
      icon: TrendingUp,
      color: 'orange',
      bgColor: 'bg-orange-100',
      textColor: 'text-orange-600'
    }
  ];

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Campaign Dashboard</h1>
        <p className="text-gray-600 mt-2">Monitor your outreach campaigns and performance</p>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {metrics.map((metric, index) => (
          <div key={index} className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">{metric.label}</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{metric.value}</p>
              </div>
              <div className={`${metric.bgColor} p-3 rounded-lg`}>
                <metric.icon className={`w-6 h-6 ${metric.textColor}`} />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Status Breakdown */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Lead Status Breakdown</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {analytics?.status_breakdown && Object.entries(analytics.status_breakdown).map(([status, count]) => (
            <div key={status} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-600 capitalize">{status}</span>
                <span className="text-2xl font-bold text-gray-900">{count}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="mt-8 bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center mb-4">
          <Activity className="w-5 h-5 text-gray-600 mr-2" />
          <h2 className="text-xl font-bold text-gray-900">Recent Activity</h2>
        </div>
        <div className="space-y-3">
          <div className="text-gray-600 text-sm">
            <span className="font-medium">Campaign launched:</span> Test Campaign - 25 leads
          </div>
          <div className="text-gray-600 text-sm">
            <span className="font-medium">Templates updated:</span> Discovery Email v2
          </div>
          <div className="text-gray-600 text-sm">
            <span className="font-medium">Leads imported:</span> 15 new leads from Airtable
          </div>
        </div>
      </div>
    </div>
  );
}
```

### Step 4: Create Leads Management Page

**File**: `src/pages/campaigns/Leads.jsx`

```jsx
import React, { useState, useEffect } from 'react';
import { Search, Filter, Users } from 'lucide-react';
import { outreachAPI } from '../../api/outreachAPI';

export default function LeadsPage() {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    status: '',
    industry: '',
    location: '',
    search: ''
  });

  useEffect(() => {
    loadLeads();
  }, [filters.status, filters.industry, filters.location]);

  const loadLeads = async () => {
    try {
      const { leads } = await outreachAPI.getLeads({
        status: filters.status,
        industry: filters.industry,
        location: filters.location
      });
      setLeads(leads);
    } catch (error) {
      console.error('Failed to load leads:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredLeads = leads.filter(lead =>
    filters.search === '' ||
    lead.name.toLowerCase().includes(filters.search.toLowerCase()) ||
    lead.email.toLowerCase().includes(filters.search.toLowerCase())
  );

  const getStatusBadgeColor = (status) => {
    switch (status) {
      case 'responded': return 'bg-green-100 text-green-800';
      case 'contacted': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Leads Management</h1>
        <p className="text-gray-600 mt-2">Manage and organize your outreach leads</p>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search leads..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
            />
          </div>

          {/* Status Filter */}
          <select
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            value={filters.status}
            onChange={(e) => setFilters({ ...filters, status: e.target.value })}
          >
            <option value="">All Statuses</option>
            <option value="new">New</option>
            <option value="contacted">Contacted</option>
            <option value="responded">Responded</option>
          </select>

          {/* Industry Filter */}
          <select
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            value={filters.industry}
            onChange={(e) => setFilters({ ...filters, industry: e.target.value })}
          >
            <option value="">All Industries</option>
            <option value="Tech">Tech</option>
            <option value="Retail">Retail</option>
            <option value="Services">Services</option>
          </select>

          {/* Location Filter */}
          <select
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            value={filters.location}
            onChange={(e) => setFilters({ ...filters, location: e.target.value })}
          >
            <option value="">All Locations</option>
            <option value="New York">New York</option>
            <option value="San Francisco">San Francisco</option>
            <option value="Chicago">Chicago</option>
          </select>
        </div>
      </div>

      {/* Leads Table */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Name
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Email
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Phone
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Industry
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Location
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {loading ? (
              <tr>
                <td colSpan="6" className="px-6 py-4 text-center text-gray-500">
                  Loading leads...
                </td>
              </tr>
            ) : filteredLeads.length === 0 ? (
              <tr>
                <td colSpan="6" className="px-6 py-4 text-center text-gray-500">
                  No leads found
                </td>
              </tr>
            ) : (
              filteredLeads.map((lead) => (
                <tr key={lead.id} className="hover:bg-gray-50 transition-colors cursor-pointer">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{lead.name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-600">{lead.email}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-600">{lead.phone}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-600">{lead.industry}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-600">{lead.location}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusBadgeColor(lead.status)}`}>
                      {lead.status}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Lead Count */}
      <div className="mt-4 text-sm text-gray-600">
        Showing {filteredLeads.length} of {leads.length} leads
      </div>
    </div>
  );
}
```

### Step 5: Create Campaign Launch Wizard

**File**: `src/pages/campaigns/LaunchCampaign.jsx`

```jsx
import React, { useState, useEffect } from 'react';
import { ChevronRight, ChevronLeft, Send, AlertCircle } from 'lucide-react';
import { outreachAPI } from '../../api/outreachAPI';
import { useNavigate } from 'react-router-dom';

export default function LaunchCampaign() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [leads, setLeads] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [campaignData, setCampaignData] = useState({
    campaign_name: '',
    campaign_type: 'email',
    template_id: '',
    lead_ids: [],
    dry_run: true
  });
  const [launching, setLaunching] = useState(false);

  useEffect(() => {
    loadLeads();
    loadTemplates();
  }, []);

  const loadLeads = async () => {
    const { leads } = await outreachAPI.getLeads();
    setLeads(leads);
  };

  const loadTemplates = async () => {
    const { templates } = await outreachAPI.getTemplates();
    setTemplates(templates);
  };

  const handleLaunch = async () => {
    setLaunching(true);
    try {
      const result = await outreachAPI.launchCampaign(campaignData);
      alert(`Campaign launched successfully! ${campaignData.dry_run ? '(Dry run mode - no emails sent)' : ''}`);
      navigate('/campaigns/active');
    } catch (error) {
      alert('Failed to launch campaign: ' + error.message);
    } finally {
      setLaunching(false);
    }
  };

  const canProceed = () => {
    switch (step) {
      case 1: return campaignData.campaign_name.trim() !== '';
      case 2: return campaignData.lead_ids.length > 0;
      case 3: return campaignData.template_id !== '';
      case 4: return true;
      default: return false;
    }
  };

  const selectedTemplate = templates.find(t => t.id === campaignData.template_id);
  const selectedLeads = leads.filter(l => campaignData.lead_ids.includes(l.id));

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Launch Campaign</h1>
        <p className="text-gray-600 mt-2">Create and launch a new outreach campaign</p>
      </div>

      {/* Progress Indicator */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {['Setup', 'Select Leads', 'Template', 'Review'].map((label, index) => (
            <div key={index} className="flex items-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                step > index + 1 ? 'bg-green-500 text-white' :
                step === index + 1 ? 'bg-blue-500 text-white' :
                'bg-gray-200 text-gray-600'
              }`}>
                {index + 1}
              </div>
              <span className={`ml-2 text-sm ${step === index + 1 ? 'font-bold' : ''}`}>{label}</span>
              {index < 3 && <ChevronRight className="w-5 h-5 text-gray-400 mx-2" />}
            </div>
          ))}
        </div>
      </div>

      {/* Step Content */}
      <div className="bg-white rounded-lg shadow-md p-8">
        {/* Step 1: Campaign Setup */}
        {step === 1 && (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Campaign Name
              </label>
              <input
                type="text"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., Q1 Discovery Outreach"
                value={campaignData.campaign_name}
                onChange={(e) => setCampaignData({ ...campaignData, campaign_name: e.target.value })}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Campaign Type
              </label>
              <div className="flex gap-4">
                {['email', 'sms', 'both'].map((type) => (
                  <button
                    key={type}
                    className={`px-6 py-3 rounded-lg border-2 font-medium capitalize ${
                      campaignData.campaign_type === type
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-300 text-gray-700 hover:border-gray-400'
                    }`}
                    onClick={() => setCampaignData({ ...campaignData, campaign_type: type })}
                  >
                    {type}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="dry_run"
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                checked={campaignData.dry_run}
                onChange={(e) => setCampaignData({ ...campaignData, dry_run: e.target.checked })}
              />
              <label htmlFor="dry_run" className="ml-2 text-sm text-gray-700">
                Dry run mode (test without sending)
              </label>
            </div>
          </div>
        )}

        {/* Step 2: Select Leads */}
        {step === 2 && (
          <div>
            <div className="mb-4">
              <p className="text-sm text-gray-600">
                Selected: {campaignData.lead_ids.length} leads
              </p>
            </div>
            <div className="max-h-96 overflow-y-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50 sticky top-0">
                  <tr>
                    <th className="px-4 py-2">
                      <input
                        type="checkbox"
                        checked={campaignData.lead_ids.length === leads.length}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setCampaignData({ ...campaignData, lead_ids: leads.map(l => l.id) });
                          } else {
                            setCampaignData({ ...campaignData, lead_ids: [] });
                          }
                        }}
                      />
                    </th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Industry</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {leads.map((lead) => (
                    <tr key={lead.id} className="hover:bg-gray-50">
                      <td className="px-4 py-2">
                        <input
                          type="checkbox"
                          checked={campaignData.lead_ids.includes(lead.id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setCampaignData({
                                ...campaignData,
                                lead_ids: [...campaignData.lead_ids, lead.id]
                              });
                            } else {
                              setCampaignData({
                                ...campaignData,
                                lead_ids: campaignData.lead_ids.filter(id => id !== lead.id)
                              });
                            }
                          }}
                        />
                      </td>
                      <td className="px-4 py-2 text-sm">{lead.name}</td>
                      <td className="px-4 py-2 text-sm text-gray-600">{lead.industry}</td>
                      <td className="px-4 py-2 text-sm">
                        <span className="px-2 py-1 rounded-full text-xs bg-gray-100">
                          {lead.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Step 3: Choose Template */}
        {step === 3 && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {templates
              .filter(t => campaignData.campaign_type === 'both' || t.type === campaignData.campaign_type)
              .map((template) => (
                <div
                  key={template.id}
                  className={`border-2 rounded-lg p-4 cursor-pointer transition-all ${
                    campaignData.template_id === template.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setCampaignData({ ...campaignData, template_id: template.id })}
                >
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-medium text-gray-900">{template.name}</h3>
                    <span className="px-2 py-1 rounded-full text-xs bg-gray-100">
                      {template.type}
                    </span>
                  </div>
                  {template.subject && (
                    <p className="text-sm text-gray-600 mb-2">
                      <span className="font-medium">Subject:</span> {template.subject}
                    </p>
                  )}
                  <p className="text-sm text-gray-600 line-clamp-3">
                    {template.body}
                  </p>
                </div>
              ))}
          </div>
        )}

        {/* Step 4: Review */}
        {step === 4 && (
          <div className="space-y-6">
            {!campaignData.dry_run && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-start">
                <AlertCircle className="w-5 h-5 text-yellow-600 mr-3 mt-0.5" />
                <div>
                  <h4 className="font-medium text-yellow-900">Live Campaign Warning</h4>
                  <p className="text-sm text-yellow-800 mt-1">
                    Dry run is OFF. This will send real emails/SMS to {selectedLeads.length} leads.
                  </p>
                </div>
              </div>
            )}

            <div className="space-y-4">
              <div>
                <h3 className="font-medium text-gray-900">Campaign Details</h3>
                <div className="mt-2 space-y-1 text-sm text-gray-600">
                  <p><span className="font-medium">Name:</span> {campaignData.campaign_name}</p>
                  <p><span className="font-medium">Type:</span> {campaignData.campaign_type}</p>
                  <p><span className="font-medium">Mode:</span> {campaignData.dry_run ? 'Dry Run (Test)' : 'Live'}</p>
                </div>
              </div>

              <div>
                <h3 className="font-medium text-gray-900">Selected Leads</h3>
                <p className="text-sm text-gray-600 mt-1">
                  {selectedLeads.length} leads selected
                </p>
              </div>

              <div>
                <h3 className="font-medium text-gray-900">Template</h3>
                <p className="text-sm text-gray-600 mt-1">
                  {selectedTemplate?.name}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Navigation Buttons */}
      <div className="mt-8 flex items-center justify-between">
        <button
          className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 disabled:opacity-50"
          onClick={() => setStep(step - 1)}
          disabled={step === 1}
        >
          <ChevronLeft className="w-5 h-5 inline mr-1" />
          Previous
        </button>

        {step < 4 ? (
          <button
            className="px-6 py-2 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 disabled:opacity-50"
            onClick={() => setStep(step + 1)}
            disabled={!canProceed()}
          >
            Next
            <ChevronRight className="w-5 h-5 inline ml-1" />
          </button>
        ) : (
          <button
            className="px-6 py-2 bg-green-500 text-white rounded-lg font-medium hover:bg-green-600 disabled:opacity-50 flex items-center"
            onClick={handleLaunch}
            disabled={launching || !canProceed()}
          >
            {launching ? 'Launching...' : (
              <>
                <Send className="w-5 h-5 mr-2" />
                Launch Campaign
              </>
            )}
          </button>
        )}
      </div>
    </div>
  );
}
```

### Step 6: Create Active Campaigns Page

**File**: `src/pages/campaigns/ActiveCampaigns.jsx`

```jsx
import React, { useState, useEffect } from 'react';
import { Clock, CheckCircle, Mail, MessageSquare } from 'lucide-react';
import { outreachAPI } from '../../api/outreachAPI';

export default function ActiveCampaigns() {
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCampaigns();
  }, []);

  const loadCampaigns = async () => {
    try {
      const { campaigns } = await outreachAPI.getCampaigns();
      setCampaigns(campaigns);
    } catch (error) {
      console.error('Failed to load campaigns:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'running':
        return <span className="px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">Running</span>;
      case 'completed':
        return <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">Completed</span>;
      case 'dry_run':
        return <span className="px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">Dry Run</span>;
      default:
        return <span className="px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">{status}</span>;
    }
  };

  const getTypeIcon = (type) => {
    if (type === 'email') return <Mail className="w-4 h-4" />;
    if (type === 'sms') return <MessageSquare className="w-4 h-4" />;
    return <Mail className="w-4 h-4" />;
  };

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Active Campaigns</h1>
        <p className="text-gray-600 mt-2">Monitor your running and completed campaigns</p>
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-500">Loading campaigns...</div>
      ) : campaigns.length === 0 ? (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <Clock className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No campaigns yet</h3>
          <p className="text-gray-600">Launch your first campaign to get started</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {campaigns.map((campaign) => (
            <div key={campaign.id} className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="font-bold text-gray-900">{campaign.name}</h3>
                  <div className="flex items-center mt-1 text-sm text-gray-600">
                    {getTypeIcon(campaign.type)}
                    <span className="ml-1 capitalize">{campaign.type}</span>
                  </div>
                </div>
                {getStatusBadge(campaign.status)}
              </div>

              {/* Progress Bar */}
              <div className="mb-4">
                <div className="flex justify-between text-sm text-gray-600 mb-1">
                  <span>Progress</span>
                  <span>{campaign.sent || 0} / {campaign.lead_count || 0}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full transition-all"
                    style={{ width: `${((campaign.sent || 0) / (campaign.lead_count || 1)) * 100}%` }}
                  />
                </div>
              </div>

              {/* Metrics */}
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-600">Sent</p>
                  <p className="text-lg font-bold text-gray-900">{campaign.sent || 0}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-600">Delivered</p>
                  <p className="text-lg font-bold text-gray-900">{campaign.delivered || 0}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-600">Opened</p>
                  <p className="text-lg font-bold text-gray-900">{campaign.opened || 0}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-600">Responded</p>
                  <p className="text-lg font-bold text-gray-900">{campaign.responded || 0}</p>
                </div>
              </div>

              {/* Created Date */}
              <div className="mt-4 pt-4 border-t border-gray-200">
                <p className="text-xs text-gray-500">
                  Created {new Date(campaign.created_at).toLocaleDateString()}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

### Step 7: Create Templates Page

**File**: `src/pages/campaigns/Templates.jsx`

```jsx
import React, { useState, useEffect } from 'react';
import { Mail, MessageSquare, Eye } from 'lucide-react';
import { outreachAPI } from '../../api/outreachAPI';

export default function TemplatesPage() {
  const [templates, setTemplates] = useState([]);
  const [activeTab, setActiveTab] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const { templates } = await outreachAPI.getTemplates();
      setTemplates(templates);
    } catch (error) {
      console.error('Failed to load templates:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredTemplates = templates.filter(template =>
    activeTab === 'all' || template.type === activeTab
  );

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Campaign Templates</h1>
        <p className="text-gray-600 mt-2">Browse and manage your email and SMS templates</p>
      </div>

      {/* Tabs */}
      <div className="mb-6 border-b border-gray-200">
        <div className="flex space-x-8">
          {['all', 'email', 'sms'].map((tab) => (
            <button
              key={tab}
              className={`pb-4 px-1 border-b-2 font-medium text-sm capitalize ${
                activeTab === tab
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
              onClick={() => setActiveTab(tab)}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* Templates Grid */}
      {loading ? (
        <div className="text-center py-12 text-gray-500">Loading templates...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTemplates.map((template) => (
            <div key={template.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center">
                  {template.type === 'email' ? (
                    <Mail className="w-5 h-5 text-blue-500 mr-2" />
                  ) : (
                    <MessageSquare className="w-5 h-5 text-purple-500 mr-2" />
                  )}
                  <h3 className="font-bold text-gray-900">{template.name}</h3>
                </div>
                <span className="px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600 capitalize">
                  {template.type}
                </span>
              </div>

              {template.subject && (
                <div className="mb-3">
                  <p className="text-xs text-gray-500 mb-1">Subject</p>
                  <p className="text-sm font-medium text-gray-700">{template.subject}</p>
                </div>
              )}

              <div className="mb-4">
                <p className="text-xs text-gray-500 mb-1">Preview</p>
                <p className="text-sm text-gray-600 line-clamp-3">{template.body}</p>
              </div>

              <button className="w-full px-4 py-2 border border-blue-500 text-blue-500 rounded-lg font-medium hover:bg-blue-50 transition-colors flex items-center justify-center">
                <Eye className="w-4 h-4 mr-2" />
                Preview Template
              </button>
            </div>
          ))}
        </div>
      )}

      {filteredTemplates.length === 0 && !loading && (
        <div className="text-center py-12 text-gray-500">
          No {activeTab !== 'all' ? activeTab : ''} templates found
        </div>
      )}
    </div>
  );
}
```

### Step 8: Create Analytics Page

**File**: `src/pages/campaigns/Analytics.jsx`

```jsx
import React, { useState, useEffect } from 'react';
import { TrendingUp, Mail, MessageSquare, Users, BarChart3 } from 'lucide-react';
import { outreachAPI } from '../../api/outreachAPI';

export default function AnalyticsPage() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      const data = await outreachAPI.getAnalytics();
      setAnalytics(data);
    } catch (error) {
      console.error('Failed to load analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-gray-500">Loading analytics...</div>;
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Campaign Analytics</h1>
        <p className="text-gray-600 mt-2">Track performance and insights across all campaigns</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Leads</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">{analytics?.total_leads || 0}</p>
            </div>
            <div className="bg-blue-100 p-3 rounded-lg">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Emails Sent</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">{analytics?.emails_sent || 0}</p>
            </div>
            <div className="bg-green-100 p-3 rounded-lg">
              <Mail className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">SMS Sent</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">{analytics?.sms_sent || 0}</p>
            </div>
            <div className="bg-purple-100 p-3 rounded-lg">
              <MessageSquare className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Response Rate</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                {Math.round((analytics?.response_rate || 0) * 100)}%
              </p>
            </div>
            <div className="bg-orange-100 p-3 rounded-lg">
              <TrendingUp className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Charts Placeholder */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Campaigns Over Time</h3>
          <div className="flex items-center justify-center h-64 bg-gray-50 rounded-lg">
            <div className="text-center text-gray-500">
              <BarChart3 className="w-12 h-12 mx-auto mb-2 text-gray-400" />
              <p className="text-sm">Chart visualization would go here</p>
              <p className="text-xs mt-1">Integrate a charting library like Chart.js or Recharts</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Response Rates by Type</h3>
          <div className="flex items-center justify-center h-64 bg-gray-50 rounded-lg">
            <div className="text-center text-gray-500">
              <BarChart3 className="w-12 h-12 mx-auto mb-2 text-gray-400" />
              <p className="text-sm">Chart visualization would go here</p>
              <p className="text-xs mt-1">Integrate a charting library like Chart.js or Recharts</p>
            </div>
          </div>
        </div>
      </div>

      {/* Active Campaigns Summary */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Active Campaigns Summary</h3>
        <p className="text-sm text-gray-600">
          {analytics?.campaigns_active || 0} campaigns currently running
        </p>
      </div>
    </div>
  );
}
```

### Step 9: Add Routes to JarvisBot Router

**Location**: Find your React Router configuration in JarvisBot (usually `App.jsx` or `routes.jsx`)

**Add these routes**:
```jsx
import CampaignsDashboard from './pages/campaigns/Dashboard';
import LeadsPage from './pages/campaigns/Leads';
import LaunchCampaign from './pages/campaigns/LaunchCampaign';
import ActiveCampaigns from './pages/campaigns/ActiveCampaigns';
import TemplatesPage from './pages/campaigns/Templates';
import AnalyticsPage from './pages/campaigns/Analytics';

// In your Routes:
<Route path="/campaigns/dashboard" element={<CampaignsDashboard />} />
<Route path="/campaigns/leads" element={<LeadsPage />} />
<Route path="/campaigns/launch" element={<LaunchCampaign />} />
<Route path="/campaigns/active" element={<ActiveCampaigns />} />
<Route path="/campaigns/templates" element={<TemplatesPage />} />
<Route path="/campaigns/analytics" element={<AnalyticsPage />} />
```

### Step 10: Add Environment Variable

**File**: `.env` (or `.env.local`)

```env
VITE_OUTREACH_API_URL=http://localhost:8000
```

---

## 🧪 Testing

### Test Backend Connection
1. Start the demo backend:
```bash
cd /path/to/outreach-automation/webapp/backend
python3 demo_server.py
```

2. Verify API is running:
```bash
curl http://localhost:8000/health
```

### Test Frontend Integration
1. Navigate to http://localhost:3000/campaigns/dashboard
2. Verify metrics load
3. Go to /campaigns/leads - should show 50 demo leads
4. Go to /campaigns/launch - test the wizard
5. Launch a test campaign in dry-run mode
6. Verify campaign appears in /campaigns/active

---

## 🎯 API Endpoints Reference

```
GET  /api/leads?status=&industry=&location=
GET  /api/leads/:id
GET  /api/templates
GET  /api/campaigns
POST /api/campaigns/launch
GET  /api/analytics
GET  /health
```

---

## 📝 Implementation Checklist

- [ ] Create API client (`src/api/outreachAPI.js`)
- [ ] Create Dashboard page
- [ ] Create Leads page
- [ ] Create Launch Campaign page
- [ ] Create Active Campaigns page
- [ ] Create Templates page
- [ ] Create Analytics page
- [ ] Add navigation menu items
- [ ] Add routes to router
- [ ] Add environment variable
- [ ] Test backend connection
- [ ] Test all pages load
- [ ] Test campaign launch flow
- [ ] Verify data displays correctly

---

## 🚀 Deployment Notes

**Frontend (JarvisBot on Lovable):**
- Lovable will auto-deploy when you push to GitHub
- Add `VITE_OUTREACH_API_URL` to Lovable environment variables

**Backend (Separate Deployment):**
- Deploy to Railway, Render, or Vercel
- Update `VITE_OUTREACH_API_URL` to production API URL
- Add CORS for Lovable domain

---

## 🆘 Troubleshooting

**Problem**: API calls fail with CORS error
**Solution**: Update backend CORS to include JarvisBot domain

**Problem**: Pages show "Loading..." forever
**Solution**: Check backend is running and API URL is correct

**Problem**: Templates/Leads not showing
**Solution**: Verify backend demo_server.py is running

**Problem**: Campaign launch fails
**Solution**: Check console for errors, verify all required fields are filled

---

## 📚 Additional Resources

- Backend source: `/outreach-automation/webapp/backend/`
- React components: `/outreach-automation/webapp/frontend/src/`
- n8n workflows: `/outreach-automation/n8n_workflows/`
- Full documentation: `/outreach-automation/COMPLETE_SYSTEM_GUIDE.md`

---

**Success Criteria**: User can navigate to "Campaigns" in JarvisBot, view leads, launch a test campaign, and see it in active campaigns - all within the unified JarvisBot interface.
