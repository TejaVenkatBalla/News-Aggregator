# News-Aggregator

A full-stack application for fetching and Scraping news Articles related 2025 Super Bowl from various sources and displaying them in a user-friendly interface.

## Technologies Used

### Backend
- FastAPI
- Celery
- BeautifulSoup4 

### Frontend
- React
- React Router

## Database
- MySQL
- Redis 

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/TejaVenkatBalla/News-Aggregator.git
   cd News-Aggregator
   ```

2. Use given sample .env file or Create a `.env` file in the root directory with the following environment variables:
   ```
   DB_NAME=your_database_name
   DB_USER=your_database_user
   DB_PASSWORD=your_database_password
   DB_PORT=3306
   REDIS_URL=redis://redis:6379/0
   ```

3. Start the application using Docker:
   ```bash
   docker-compose up
   ```

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

## Project Structure

```
News-Aggregator/
├── backend/          # FastAPI backend
├── frontend/         # React frontend
├── docker-compose.yml # Docker configuration
└── README.md          # Project documentation
```

## Running Tests

To run backend tests:
```bash
docker-compose exec backend pytest
```
