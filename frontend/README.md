# SupplierIQ - Frontend Application

## 📁 Project Structure

```
frontend/
├── css/
│   ├── common.css          # Shared styles for all pages
│   └── auth.css            # Authentication pages styles
├── js/
│   ├── api.js              # API calls and utility functions
│   └── auth-check.js       # Authentication protection for pages
├── pages/
│   ├── dashboard.html      # Dashboard with company clustering
│   ├── transactions.html   # Transactions analysis with pagination
│   ├── upload.html         # CSV upload and clustering analysis
│   └── recommendations.html # Strategic recommendations
├── login.html              # Login page
└── register.html           # Registration page
```

## 🚀 Getting Started

### Prerequisites

1. **Backend API running** at `http://localhost:5000`
   - Navigate to `backend/` folder
   - Run: `python src/app.py`

2. **MongoDB running** with data loaded
   - Ensure MongoDB is running
   - Load data: `python backend/database/load_data.py`

### Running the Frontend

1. **Option 1: Using Live Server (Recommended)**
   ```bash
   # Install Live Server extension in VS Code
   # Right-click on login.html → "Open with Live Server"
   ```

2. **Option 2: Python HTTP Server**
   ```bash
   cd frontend
   python -m http.server 8000
   # Open browser: http://localhost:8000/login.html
   ```

3. **Option 3: Direct File Opening**
   ```bash
   # Simply open login.html in your browser
   # Note: Some features may not work due to CORS
   ```

## 📋 Features Overview

### 1. **Authentication System**
- **Login Page** (`login.html`)
  - Email and password login
  - JWT token storage
  - Auto-redirect if already logged in

- **Register Page** (`register.html`)
  - New user registration
  - Form validation
  - Auto-redirect after successful registration

### 2. **Dashboard** (`pages/dashboard.html`)
- **Metrics Cards (Row 1)**
  - Total Companies
  - High Performers
  - Mid Performers
  - Low Performers

- **Charts (Row 2)**
  - Bar chart: Cluster distribution
  - Pie chart: Performance breakdown

- **Data Table (Row 3)**
  - Supplier ID
  - Company Name
  - Overall Score
  - Quality Score
  - Delivery Reliability
  - Cost Efficiency
  - Cluster (High/Mid/Low badge)
  - Search functionality

### 3. **Transactions** (`pages/transactions.html`)
- **Metrics Cards (Row 1)**
  - Total Transactions
  - High Performance Transactions
  - Mid Performance Transactions
  - Low Performance Transactions

- **Charts (Row 2)**
  - Bar chart: Transaction distribution
  - Pie chart: Performance breakdown

- **Data Table (Row 3)**
  - Date
  - Supplier ID
  - Company Name
  - Performance Metrics
  - Cluster badge
  - **Pagination**: 25 items per page
  - Search functionality

### 4. **Upload** (`pages/upload.html`)
- **File Upload Section**
  - Drag & drop CSV upload
  - File validation
  - Required columns display:
    - supplier_id
    - company_name
    - overall_score
    - quality_score
    - delivery_reliability
    - cost_efficiency
    - customer_satisfaction
    - defect_rate

- **Processing**
  - Upload CSV to backend
  - Trigger ensemble clustering (K-Means + DBSCAN + Hierarchical)
  - Display results in same format as dashboard

- **Results Display**
  - Metrics cards
  - Charts
  - Clustered data table

### 5. **Recommendations** (`pages/recommendations.html`)
- **Strategic Recommendations Cards**
  - One card per cluster (High/Mid/Low)
  - Cluster profile and statistics
  - Key strengths (green tags)
  - Areas for improvement (orange tags)
  - Strategic recommendation text

## 🔧 API Endpoints Used

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user

### Companies
- `GET /api/companies` - Get all companies
- `GET /api/companies/:id` - Get single company
- `GET /api/companies/stats` - Get statistics

### Transactions
- `GET /api/transactions?page=1&limit=25` - Get paginated transactions
- `GET /api/transactions/stats` - Get statistics

### Upload & Analysis
- `POST /api/upload` - Upload CSV file
- `POST /api/analyze` - Run ensemble clustering

### Recommendations
- `GET /api/recommendations` - Get all recommendations

## 🎨 Design System

### Colors
- **Primary**: Purple gradient (#667eea → #764ba2)
- **Success/High**: Green (#48bb78, #38a169)
- **Warning/Mid**: Orange (#ed8936, #dd6b20)
- **Danger/Low**: Red (#f56565, #e53e3e)
- **Info**: Blue (#4299e1, #3182ce)

### Typography
- **Font**: Inter (Google Fonts)
- **Weights**: 300, 400, 500, 600, 700

### Components
- Metric cards with hover effects
- Charts using Chart.js
- Responsive data tables
- Pagination controls
- Badge system (High/Mid/Low)
- Loading spinners
- Alert messages (success/error)

## 🔐 Authentication Flow

1. **First Visit**: User lands on `login.html`
2. **No Account**: Click "Register here" → Fill form → Auto-redirect to login
3. **Login**: Enter credentials → Store JWT token → Redirect to dashboard
4. **Protected Pages**: All pages in `/pages/` check for token
5. **No Token**: Auto-redirect to login
6. **Logout**: Click logout button → Clear token → Redirect to login

## 📊 Data Flow

### Dashboard
```
User → Dashboard Page
  → API: GET /api/companies
  → Display metrics, charts, table
  → Enable search
```

### Transactions
```
User → Transactions Page
  → API: GET /api/transactions
  → Display metrics, charts, table
  → Enable search & pagination
```

### Upload
```
User → Upload Page
  → Select CSV file
  → Click "Upload & Analyze"
  → API: POST /api/upload (with FormData)
  → API: POST /api/analyze (trigger clustering)
  → Display results (metrics, charts, table)
```

### Recommendations
```
User → Recommendations Page
  → API: GET /api/recommendations
  → Display recommendation cards
  → Show strengths, improvements, strategies
```

## 🔍 Search & Filter

- **Dashboard**: Search by Supplier ID or Company Name
- **Transactions**: Search by Supplier ID or Company Name + Pagination

## 📱 Responsive Design

- **Desktop**: Full layout with sidebars
- **Tablet**: Adjusted grid layouts
- **Mobile**: Stacked layouts, hamburger menu

## 🐛 Error Handling

- API errors displayed in red alert boxes
- Success messages in green alert boxes
- Auto-dismiss after 5 seconds
- Loading spinners during API calls
- Form validation errors

## 🔄 State Management

- **JWT Token**: Stored in `localStorage`
- **User Info**: Name and email in `localStorage`
- **Current Page**: Managed by URL
- **Charts**: Destroyed and recreated on data refresh

## 📝 Notes

1. **CORS**: Make sure backend has CORS enabled for `http://localhost:8000` or your frontend URL
2. **API Base URL**: Configured in `js/api.js` as `http://localhost:5000/api`
3. **File Upload**: Only CSV files accepted
4. **Pagination**: Fixed at 25 items per page on transactions
5. **Charts**: Using Chart.js v3+ (loaded from CDN)

## 🚨 Troubleshooting

### "Failed to load data"
- Check if backend is running on port 5000
- Verify MongoDB is running and data is loaded
- Check browser console for CORS errors

### "Login failed"
- Verify backend auth routes are working
- Check if users collection exists in MongoDB
- Ensure email/password are correct

### Charts not displaying
- Check browser console for errors
- Verify Chart.js CDN is accessible
- Ensure canvas elements have proper IDs

### Upload not working
- Verify CSV format matches required columns
- Check file size limits
- Ensure backend upload endpoint is accessible

## 📧 Support

For issues or questions, check:
1. Browser console (F12) for errors
2. Network tab for API call failures
3. Backend terminal for server errors

## 🎯 Next Steps

To enhance the application:
1. Add user profile management
2. Implement data export (CSV/PDF)
3. Add email notifications
4. Create admin vs user roles
5. Add data visualization filters
6. Implement real-time updates (WebSockets)
7. Add dark mode toggle
8. Create mobile app version
