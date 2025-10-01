# PetID - Pet Identity Management System 🐾

A Django-based web application for pet identification and medical record management using QR codes.

## Features

- 🔐 **User Authentication**: Role-based access (Pet Owners & Veterinarians)
- 🐕 **Pet Management**: Complete pet profile management with photo upload
- 📱 **QR Code Generation**: Unique QR codes for each pet for quick identification
- 🏥 **Medical Records**: Comprehensive medical history tracking
- 📍 **Location Tracking**: GPS-based lost pet alerts via email
- 👨‍⚕️ **Doctor Access**: Veterinarians can access granted pet medical records
- 📧 **Email Notifications**: Automated alerts for lost pets with location data

## Tech Stack

- **Backend**: Django 5.2.6
- **Database**: PostgreSQL
- **Frontend**: HTML, CSS (Tailwind), JavaScript
- **Containerization**: Docker & Docker Compose
- **CI/CD**: Jenkins
- **Web Server**: Nginx
- **Caching**: Redis
- **Monitoring**: Prometheus & Grafana

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL (for local development)

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/Bss-bass/Pet-Identity.git
   cd Pet-Identity
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start the application**
   ```bash
   make docker-up
   # or
   docker-compose up -d
   ```

4. **Run migrations**
   ```bash
   make migrate
   # or
   docker-compose exec web python manage.py migrate
   ```

5. **Create superuser (optional)**
   ```bash
   make superuser
   # or
   docker-compose exec web python manage.py createsuperuser
   ```

6. **Access the application**
   - Web App: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin
   - Database: localhost:5432
   - Redis: localhost:6379

### Local Development

1. **Set up virtual environment**
   ```bash
   make dev-setup
   # or manually:
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure database**
   ```bash
   # Make sure PostgreSQL is running
   createdb petid_db
   ```

3. **Run migrations**
   ```bash
   python manage.py migrate
   ```

4. **Start development server**
   ```bash
   make dev-run
   # or
   python manage.py runserver
   ```

## Available Commands

Use the Makefile for common tasks:

```bash
# Development
make dev-setup          # Set up development environment
make dev-run            # Run development server

# Docker
make docker-build       # Build Docker images
make docker-up          # Start containers
make docker-down        # Stop containers
make docker-logs        # View logs

# Database
make migrate            # Run migrations
make makemigrations     # Create migrations
make db-backup          # Backup database

# Testing
make test              # Run tests
make test-coverage     # Run tests with coverage
make lint              # Run code linting

# Production
make prod-up           # Start production containers
make prod-down         # Stop production containers
```

## Project Structure

```
PetID/
├── core/                   # Main Django app
│   ├── models.py          # Database models
│   ├── views.py           # View controllers
│   ├── forms.py           # Django forms
│   ├── urls.py            # URL routing
│   └── templates/         # HTML templates
├── PetID/                 # Django project settings
├── media/                 # User uploaded files
├── static/                # Static files (CSS, JS, Images)
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Development Docker setup
├── docker-compose.prod.yml # Production Docker setup
├── Jenkinsfile           # CI/CD pipeline
├── nginx.conf            # Nginx configuration
└── Makefile             # Common commands
```

## API Endpoints

### Authentication
- `POST /core/register/` - User registration
- `POST /core/login/` - User login
- `GET /core/dashboard/` - User dashboard

### Pet Management
- `GET /core/create_pet/` - Create new pet
- `GET /core/pet/<pet_id>/edit/` - Edit pet profile
- `GET /core/pet/<qr_slug>/card/` - Public pet card (QR access)
- `GET /core/pet/<pet_id>/generate-qr/` - Generate QR code

### Medical Records
- `GET /core/pet/<pet_id>/medical-record/` - View medical records
- `POST /core/pet/<pet_id>/add-medical-record/` - Add medical record
- `GET /core/medical-record/<record_id>/edit/` - Edit medical record
- `POST /core/medical-record/<record_id>/delete/` - Delete medical record

### Location Services
- `POST /core/pet/<pet_id>/send-location-alert/` - Send location alert

## Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,yourdomain.com

# Database
DB_NAME=petid_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=db
DB_PORT=5432

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

## Deployment

### Production Deployment

1. **Set up production environment**
   ```bash
   cp .env.example .env.prod
   # Configure production variables
   ```

2. **Deploy with Docker Compose**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Set up SSL certificates**
   ```bash
   # Place SSL certificates in ./ssl/ directory
   # Update nginx.prod.conf with your domain
   ```

### CI/CD with Jenkins

The `Jenkinsfile` includes:
- Code quality checks (linting, security)
- Automated testing
- Docker image building
- Security scanning
- Automated deployment to staging/production
- Slack notifications

## Monitoring

Production setup includes:
- **Prometheus**: Metrics collection (http://localhost:9090)
- **Grafana**: Monitoring dashboards (http://localhost:3000)
- **Nginx**: Access and error logs
- **Django**: Application logs

## Security Features

- **Authentication**: Email-based login with role management
- **Authorization**: Role-based access control (Owner/Doctor)
- **HTTPS**: SSL/TLS encryption in production
- **Rate Limiting**: API and login rate limiting
- **Security Headers**: XSS, CSRF, clickjacking protection
- **File Upload**: Secure image upload with validation
- **Database**: PostgreSQL with prepared statements

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, email support@petid.com or create an issue on GitHub.

## Acknowledgments

- Django framework and community
- Tailwind CSS for styling
- QR code generation library
- All contributors and testers

---

Made with ❤️ for pet lovers everywhere 🐾