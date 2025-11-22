# Sales Analytics Dashboard

A comprehensive end-to-end sales analytics platform featuring an interactive Streamlit dashboard, professional REST API with JWT authentication, and ML-powered revenue forecasting.

## Features

### Dashboard
- **Interactive Streamlit UI** with real-time analytics
- **KPI Overview** - Revenue, transactions, AOV, customers, products
- **Revenue Analytics** - Daily trends, monthly breakdown, growth rates
- **Customer Insights** - Segmentation, lifetime value, top customers
- **Product Analysis** - Top products, performance metrics
- **Geographic Analytics** - Sales by country with detailed metrics
- **ML Forecasting** - Prophet-based revenue predictions (63.6% accuracy)

### REST API
- **JWT Authentication** with bcrypt password hashing
- **Email Verification** workflow
- **17 Protected Endpoints** for comprehensive analytics
- **Auto-generated Documentation** (Swagger UI & ReDoc)
- **CORS Support** for frontend integration
- **Global Error Handling** with detailed logging

## Technology Stack

**Backend:**
- FastAPI - Modern REST API framework
- PostgreSQL - Production database
- psycopg2 - Database connector

**Authentication:**
- python-jose - JWT tokens
- passlib[bcrypt] - Secure password hashing
- OAuth2 with Bearer tokens

**Data & ML:**
- pandas & numpy - Data manipulation
- Facebook Prophet - Time series forecasting
- scikit-learn - Model evaluation

**Frontend:**
- Streamlit - Interactive dashboard
- Plotly - Dynamic visualizations

## Project Structure

```
sales_analytics_dashboard/
├── src/
│   ├── analytics/          # Analytics modules
│   │   ├── customer.py     # Customer analytics
│   │   ├── product.py      # Product analytics
│   │   ├── geographic.py   # Geographic analytics
│   │   ├── revenue.py      # Revenue analytics
│   │   ├── kpis.py         # KPI calculations
│   │   └── forecasting.py  # Prophet ML model
│   ├── api/                # REST API
│   │   ├── main.py         # FastAPI app
│   │   ├── auth.py         # JWT authentication
│   │   ├── users.py        # User database operations
│   │   ├── dependencies.py # Auth dependencies
│   │   └── routers/        # API endpoints
│   │       ├── auth.py     # Auth endpoints
│   │       ├── users.py    # User management
│   │       ├── analytics.py # General analytics
│   │       ├── customers.py # Customer analytics
│   │       ├── products.py  # Product analytics
│   │       ├── geographic.py # Geographic analytics
│   │       └── revenue.py   # Revenue analytics
│   ├── config/             # Configuration
│   │   └── settings.py     # Environment settings
│   ├── database/           # Database layer
│   │   └── connection.py   # DB connection pool
│   ├── etl/                # ETL pipeline
│   │   ├── load.py         # Data loading
│   │   └── transform.py    # Data transformation
│   ├── ml/                 # Machine learning
│   │   └── forecasting.py  # Prophet model training
│   ├── utils/              # Utilities
│   │   └── logger.py       # Logging configuration
│   └── visualization/      # Plotly charts
│       └── charts.py       # Chart generation
├── sql/                    # SQL scripts
│   ├── create_tables.sql   # Table schema
│   └── create_users_table.sql # Users table
├── data/                   # Data files
│   ├── raw/                # Raw CSV data
│   └── sample/             # Sample data
├── logs/                   # Application logs
├── .env                    # Environment variables (not in Git)
├── .env.example            # Environment template
├── requirements.txt        # Python dependencies
├── dashboard.py            # Streamlit dashboard
├── run_api.py              # API server startup
└── README.md               # This file
```

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- pip

### 1. Clone the Repository
```bash
git clone <repository-url>
cd sales_analytics_dashboard
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Database

**Create PostgreSQL database:**
```sql
CREATE DATABASE sales_analytics;
```

**Run SQL scripts:**
```bash
psql -U postgres -d sales_analytics -f sql/create_tables.sql
psql -U postgres -d sales_analytics -f sql/create_users_table.sql
```

### 5. Configure Environment Variables

Copy `.env.example` to `.env` and update values:
```bash
cp .env.example .env
```

Edit `.env`:
```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sales_analytics
DB_USER=postgres
DB_PASSWORD=your_password_here

# API Configuration
API_SECRET_KEY=generate-with-openssl-rand-hex-32
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Generate secure API secret key:**
```bash
openssl rand -hex 32
```

### 6. Load Sample Data
```bash
python -m src.etl.load
```

## Usage

### Running the Dashboard
```bash
streamlit run dashboard.py
```
Access at: http://localhost:8501

### Running the API
```bash
python run_api.py
```
Access at: http://localhost:8000

**API Documentation:**
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## API Documentation

### Authentication

#### Register New User
```bash
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123",
  "full_name": "John Doe"
}
```

#### Verify Email
```bash
POST /api/auth/verify-email?verification_token=<token>
```

#### Login
```bash
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Protected Endpoints

All analytics endpoints require JWT authentication:
```bash
Authorization: Bearer <your_token>
```

#### General Analytics
- `GET /api/analytics/kpis` - Key performance indicators
- `GET /api/analytics/revenue/monthly` - Monthly revenue
- `GET /api/analytics/forecast/revenue?periods=30` - Revenue forecast

#### Customer Analytics
- `GET /api/customers/top?limit=10` - Top customers by spending
- `GET /api/customers/segments` - Customer segmentation
- `GET /api/customers/lifetime-value` - CLV analysis

#### Product Analytics
- `GET /api/products/top?limit=10` - Top products by revenue

#### Geographic Analytics
- `GET /api/geographic/revenue-by-country` - Top 10 countries
- `GET /api/geographic/country-performance` - Detailed country metrics

#### Revenue Analytics
- `GET /api/revenue/daily-trend` - Daily revenue trend
- `GET /api/revenue/monthly` - Monthly revenue with orders
- `GET /api/revenue/growth` - Month-over-month growth
- `GET /api/revenue/by-hour` - Sales patterns by hour
- `GET /api/revenue/by-day-of-week` - Sales patterns by day

#### User Management
- `GET /api/users/me` - Current user profile

#### System
- `GET /` - API root
- `GET /api/health` - Health check with DB status

### Example: Get Top Customers

```bash
curl -X GET "http://localhost:8000/api/customers/top?limit=5" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

Response:
```json
{
  "top_customers": [
    {
      "customer_id": "14646",
      "total_spent": 280206.02,
      "orders": 1,
      "avg_transaction": 280206.02
    }
  ],
  "count": 5,
  "requested_by": "user@example.com"
}
```

## ML Forecasting

The Prophet model provides revenue forecasting with:
- **63.6% accuracy** on validation set
- **30-day default forecast** (customizable)
- **Confidence intervals** (upper/lower bounds)
- **Trained on 80/20 split** for validation

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | Database host | localhost |
| `DB_PORT` | Database port | 5432 |
| `DB_NAME` | Database name | sales_analytics |
| `DB_USER` | Database user | postgres |
| `DB_PASSWORD` | Database password | - |
| `API_HOST` | API server host | 0.0.0.0 |
| `API_PORT` | API server port | 8000 |
| `API_SECRET_KEY` | JWT secret key | - |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration | 30 |
| `ENVIRONMENT` | Environment mode | development |
| `DEBUG` | Debug mode | True |
| `LOG_LEVEL` | Logging level | INFO |

### Default Admin User

The system creates a default admin user:
- **Email:** admin@salesanalytics.com
- **Password:** admin123

**⚠️ Change this password in production!**

## Development

### Running Tests
```bash
pytest tests/ -v
```

### Code Style
```bash
# Format code
black src/

# Lint code
flake8 src/
```

## Production Deployment

### Security Checklist
- [ ] Change `API_SECRET_KEY` to secure random value
- [ ] Update default admin password
- [ ] Set `ENVIRONMENT=production`
- [ ] Set `DEBUG=False`
- [ ] Configure `allow_origins` in CORS middleware
- [ ] Use HTTPS
- [ ] Set up firewall rules
- [ ] Enable database SSL
- [ ] Implement rate limiting
- [ ] Set up monitoring and alerts

### Deployment Options
- **Cloud Platforms:** Heroku, AWS (ECS/Elastic Beanstalk), Azure, DigitalOcean
- **Containerization:** Docker + Docker Compose
- **Process Manager:** PM2, Supervisor, systemd
- **Reverse Proxy:** Nginx, Apache
- **Database:** AWS RDS, Azure Database, DigitalOcean Managed Databases

## Troubleshooting

### Database Connection Issues
```bash
# Test PostgreSQL connection
psql -U postgres -d sales_analytics -c "SELECT 1"

# Check if PostgreSQL is running
# Linux/Mac: sudo service postgresql status
# Windows: Check Services panel
```

### API Server Won't Start
```bash
# Check if port 8000 is in use
# Linux/Mac: lsof -i :8000
# Windows: netstat -ano | findstr :8000

# Kill process if needed
# Linux/Mac: kill -9 <PID>
# Windows: taskkill /F /PID <PID>
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Contact

For questions or support, please open an issue on GitHub.

---

**Built with FastAPI, Streamlit, PostgreSQL, and Facebook Prophet**
