// API Configuration and Utility Functions

const API_BASE_URL = 'http://localhost:5000/api';

// Get auth token from localStorage
function getAuthToken() {
    return localStorage.getItem('authToken');
}

// Set auth token in localStorage
function setAuthToken(token) {
    localStorage.setItem('authToken', token);
}

// Remove auth token
function removeAuthToken() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userName');
    localStorage.removeItem('userEmail');
}

// Check if user is authenticated
function isAuthenticated() {
    return !!getAuthToken();
}

// Generic API call function
async function apiCall(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const token = getAuthToken();
    
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const config = {
        ...options,
        headers
    };
    
    try {
        const response = await fetch(url, config);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || data.message || 'API request failed');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Authentication APIs
const AuthAPI = {
    async register(userData) {
        return await apiCall('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    },
    
    async login(credentials) {
        return await apiCall('/auth/login', {
            method: 'POST',
            body: JSON.stringify(credentials)
        });
    },
    
    async logout() {
        removeAuthToken();
    }
};

// Companies APIs
const CompaniesAPI = {
    async getAll() {
        return await apiCall('/companies');
    },
    
    async getById(id) {
        return await apiCall(`/companies/${id}`);
    },
    
    async getStats() {
        return await apiCall('/companies/stats');
    }
};

// Transactions APIs
const TransactionsAPI = {
    async getAll(page = 1, limit = 25) {
        return await apiCall(`/transactions?page=${page}&limit=${limit}`);
    },
    
    async getStats() {
        return await apiCall('/transactions/stats');
    }
};

// Recommendations APIs
const RecommendationsAPI = {
    async getAll() {
        return await apiCall('/recommendations');
    }
};

// Upload API
const UploadAPI = {
    async uploadCSV(formData) {
        const token = getAuthToken();
        
        try {
            const response = await fetch(`${API_BASE_URL}/upload`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || data.error || `Upload failed with status ${response.status}`);
            }
            
            return data;
        } catch (error) {
            // If it's already an Error with a message, rethrow it
            if (error.message && !error.message.includes('Failed to fetch')) {
                throw error;
            }
            // Network error or CORS issue
            throw new Error(`Network error: Cannot connect to backend at ${API_BASE_URL}. Make sure the backend server is running.`);
        }
    },
    
    async analyzeData() {
        return await apiCall('/analyze', {
            method: 'POST'
        });
    }
};

// Show loading spinner
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
    }
}

// Hide loading spinner
function hideLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '';
    }
}

// Show error message
function showError(message, elementId = 'errorContainer') {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="alert alert-error">
                <i class="fas fa-exclamation-circle"></i>
                <span>${message}</span>
            </div>
        `;
        setTimeout(() => {
            element.innerHTML = '';
        }, 5000);
    }
}

// Show success message
function showSuccess(message, elementId = 'successContainer') {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="alert alert-success">
                <i class="fas fa-check-circle"></i>
                <span>${message}</span>
            </div>
        `;
        setTimeout(() => {
            element.innerHTML = '';
        }, 5000);
    }
}

// Format number with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Format percentage
function formatPercentage(num, decimals = 1) {
    return `${num.toFixed(decimals)}%`;
}

// Get cluster name from tier
function getClusterName(tier) {
    const tierMap = {
        'High Performance': 'High',
        'Mid Performance': 'Medium',
        'Low Performance': 'Low'
    };
    return tierMap[tier] || tier;
}

// Get cluster badge class
function getClusterBadgeClass(tier) {
    const clusterName = getClusterName(tier).toLowerCase();
    if (clusterName.includes('high')) return 'badge-high';
    if (clusterName.includes('medium') || clusterName.includes('mid')) return 'badge-medium';
    return 'badge-low';
}
