# NoMoneyNoHoney - Personal Finance Tracker

## 📋 Description
NoMoneyNoHoney is a modern web application for personal finance management that helps you track income and expenses, analyze cash flows, and achieve financial goals.

## ✨ Features

- 📊 Income and expense tracking
- 📈 Financial statistics visualization
- 🏷 Transaction categorization
- 🔐 Secure user authentication
- 📱 Responsive interface
- 🔄 Cross-device synchronization

## 🚀 Technology Stack

- **Backend**: Python 3.13, FastAPI
- **Database**: PostgreSQL+asyncpg
- **Authentication**: JWT
- **Asynchronous**: async/await
- **Deployment**: Docker, Docker Compose

## 🛠 Installation and Setup

### Requirements
- Python 3.11+
- PostgreSQL 13+

### Environment Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/NoMoneyNoHoney.git
   cd NoMoneyNoHoney
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # OR
   .\venv\Scripts\activate  # Windows
   ```

3. Install dependencies:
   ```bash
   pip install poetry
   poetry install
   ```

4. Create a `.env` file in the project root:
   ```env
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_USER=your_username
   POSTGRES_PASSWORD=your_password
   POSTGRES_DB=nomoney_nohoney
   SECRET_KEY=your-secret-key
   ALGORITHM=HS256
   ```

5. Apply migrations:
   ```bash
   alembic upgrade head
   ```

6. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

### Running with Docker

1. Make sure you have Docker and Docker Compose installed
2. Run the following command:
   ```bash
   docker-compose up --build
   ```
3. The application will be available at: http://localhost:8000

## 📚 API Documentation

After starting the application, the API documentation will be available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🤝 How to Contribute

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## ✉️ Contact

Your Name - [@your_username](https://github.com/yourusername) - your.email@example.com

Project Link: [https://github.com/yourusername/NoMoneyNoHoney](https://github.com/yourusername/NoMoneyNoHoney)

---

<div align="center">
  <sub>Built with ❤️ for better personal finance management</sub>
</div>
