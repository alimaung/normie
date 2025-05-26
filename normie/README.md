# Normie - Standards & Material Management System

A comprehensive platform for managing organizational standards, norms, and material request/release workflows built with Django and WebSockets for real-time communication.

## Features

- **Standards Management**: Create, maintain, and track organizational standards and norms with version control
- **Request Processing**: Submit and manage material requests with automated approval workflows
- **Material Tracking**: Monitor consumable materials, inventory levels, and usage patterns
- **Release Management**: Coordinate material releases with proper documentation and compliance
- **Approval Workflows**: Streamlined approval processes with role-based access and notifications
- **Inventory Control**: Real-time inventory tracking with automated reorder points and alerts
- **Analytics & Reports**: Comprehensive reporting and analytics for compliance and optimization
- **Audit Trail**: Complete audit trails for compliance and regulatory requirements
- **Real-time Communication**: WebSocket support for instant notifications and updates
- **Internationalization**: Multi-language support (English/German)
- **Modern UI**: Responsive design with dark mode support

## Setup Instructions

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd normie
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

6. Start the development server:
```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

## Project Structure

```
normie/
├── normie/                 # Main project directory
│   ├── settings.py        # Django settings with Channels configuration
│   ├── asgi.py           # ASGI configuration for WebSockets
│   ├── routing.py        # WebSocket routing
│   └── urls.py           # Main URL configuration
├── normieapp/            # Main application
│   ├── templates/        # HTML templates
│   ├── static/          # Static files (CSS, JS, images, fonts)
│   ├── consumers.py     # WebSocket consumers
│   ├── views.py         # Django views
│   └── urls.py          # App URL configuration
├── locale/              # Translation files
└── requirements.txt     # Python dependencies
```

## Module Overview

### Current Modules
- **Home Dashboard**: Overview of system status and quick access to key functions
- **Standards Management**: Create, edit, and maintain organizational standards
- **Request Processing**: Submit and track material requests
- **Materials Catalog**: Manage consumable materials and specifications
- **Release Management**: Coordinate and document material releases
- **Approval Workflows**: Handle approval processes with role-based access
- **Inventory Control**: Track inventory levels and manage stock
- **Reports & Analytics**: Generate compliance and operational reports
- **Audit Trail**: Maintain complete audit logs for regulatory compliance

### Planned Features
- User authentication and role-based permissions
- Real-time notifications for approvals and releases
- Advanced reporting with custom filters
- Integration with external inventory systems
- Automated compliance checking
- Document management and version control
- Mobile-responsive interface
- API for third-party integrations

## Technology Stack

- **Backend**: Django 5.1.7
- **WebSockets**: Django Channels 4.0.0
- **ASGI Server**: Daphne 4.1.0
- **Frontend**: HTML5, CSS3, JavaScript (jQuery)
- **Icons**: Font Awesome 6.4.0
- **Database**: SQLite (development)

## Development

### Running with WebSocket Support

The project is configured to run with Daphne for WebSocket support:

```bash
daphne -b 0.0.0.0 -p 8000 normie.asgi:application
```

### Adding New Features

1. Create views in `normieapp/views.py`
2. Add URL patterns in `normieapp/urls.py`
3. Create templates in `normieapp/templates/normieapp/`
4. Add static files in `normieapp/static/normieapp/`

### WebSocket Development

WebSocket consumers are defined in `normieapp/consumers.py`. Add new WebSocket routes in `normie/routing.py`.

## Use Cases

### Standards Management
- Create and maintain organizational standards
- Version control for standard documents
- Approval workflows for standard changes
- Distribution and notification of updates

### Material Request Workflow
1. User submits material request
2. Automated routing to appropriate approvers
3. Approval/rejection with comments
4. Inventory check and allocation
5. Release authorization and documentation
6. Audit trail maintenance

### Inventory Management
- Real-time inventory tracking
- Automated reorder points
- Usage analytics and forecasting
- Integration with procurement systems

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License. 