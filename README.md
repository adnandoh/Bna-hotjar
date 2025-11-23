# Hotjar Clone - Backend

Django-based backend for a Hotjar-like analytics platform.

## Features

- **User Authentication & Teams**: Multi-user support with team management
- **Event Tracking**: Capture and store user interactions
- **Heatmaps**: Visual representation of user clicks and interactions
- **Session Recordings**: Record and replay user sessions
- **Form Analytics**: Track form submissions and conversions
- **Funnels**: Analyze user journey through conversion funnels
- **Surveys**: Create and manage user feedback surveys
- **Site Management**: Manage multiple websites and tracking

## Tech Stack

- **Framework**: Django 4.2.7
- **Database**: SQLite (development) - can be switched to PostgreSQL for production
- **API**: Django REST Framework

## Setup Instructions

### Prerequisites
- Python 3.8+
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/adnandoh/Bna-hotjar.git
cd Bna-hotjar
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- Windows: `venv\Scripts\activate`
- Mac/Linux: `source venv/bin/activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

The backend will be available at `http://127.0.0.1:8000/`

## API Endpoints

- `/api/accounts/` - User authentication and management
- `/api/sites/` - Website management
- `/api/events/` - Event tracking
- `/api/heatmaps/` - Heatmap data
- `/api/recordings/` - Session recordings
- `/api/forms/` - Form analytics
- `/api/funnels/` - Funnel analytics
- `/api/surveys/` - Survey management
- `/api/teams/` - Team management

## Project Structure

```
backend/
├── accounts/       # User authentication
├── analytics/      # Analytics engine
├── config/         # Django settings
├── events/         # Event tracking
├── forms/          # Form analytics
├── funnels/        # Funnel tracking
├── heatmaps/       # Heatmap generation
├── recordings/     # Session recordings
├── sites/          # Site management
├── surveys/        # Survey system
├── teams/          # Team management
└── manage.py       # Django management script
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is for educational purposes.
