/**
 * Outreach Campaign API Client
 * Drop this file into JarvisBot to connect to the outreach backend
 */

// Configure your backend URL here
const API_BASE_URL = import.meta.env.VITE_OUTREACH_API_URL || 'http://localhost:8000';

/**
 * Generic API request handler
 */
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

/**
 * Outreach Campaign API
 */
export const outreachAPI = {
  /**
   * Get all leads with optional filters
   * @param {Object} filters - { status, industry, location }
   * @returns {Promise<{leads: Array, total: number}>}
   */
  getLeads: async (filters = {}) => {
    const queryParams = new URLSearchParams(filters).toString();
    const endpoint = queryParams ? `/api/leads?${queryParams}` : '/api/leads';
    return apiRequest(endpoint);
  },

  /**
   * Get single lead by ID
   * @param {string} leadId
   * @returns {Promise<Object>}
   */
  getLead: async (leadId) => {
    return apiRequest(`/api/leads/${leadId}`);
  },

  /**
   * Get all email and SMS templates
   * @returns {Promise<{templates: Array}>}
   */
  getTemplates: async () => {
    return apiRequest('/api/templates');
  },

  /**
   * Launch a new campaign
   * @param {Object} campaignData
   * @param {string} campaignData.campaign_name - Name of the campaign
   * @param {string} campaignData.campaign_type - "email" | "sms" | "both"
   * @param {string} campaignData.template_id - Template to use
   * @param {string[]} campaignData.lead_ids - Array of lead IDs
   * @param {boolean} campaignData.dry_run - If true, simulate without sending
   * @returns {Promise<{success: boolean, campaign_id: string}>}
   */
  launchCampaign: async (campaignData) => {
    return apiRequest('/api/campaigns/launch', {
      method: 'POST',
      body: JSON.stringify(campaignData),
    });
  },

  /**
   * Get all campaigns
   * @returns {Promise<{campaigns: Array}>}
   */
  getCampaigns: async () => {
    return apiRequest('/api/campaigns');
  },

  /**
   * Get campaign analytics
   * @returns {Promise<Object>}
   */
  getAnalytics: async () => {
    return apiRequest('/api/analytics');
  },

  /**
   * Get system health status
   * @returns {Promise<Object>}
   */
  getHealth: async () => {
    return apiRequest('/health');
  },
};

/**
 * React hook for using the API with loading states
 */
export function useOutreachAPI() {
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState(null);

  const execute = async (apiMethod, ...args) => {
    setLoading(true);
    setError(null);

    try {
      const result = await apiMethod(...args);
      setLoading(false);
      return result;
    } catch (err) {
      setError(err.message);
      setLoading(false);
      throw err;
    }
  };

  return { loading, error, execute };
}

export default outreachAPI;
