# Django Todo App

Welcome to the Django Todo App! This is a simple, efficient application designed to help you manage your daily tasks and stay organized.

## 🚀 Features

- **Task Management**: Create, view, update, and delete tasks easily.
- **Clean Interface**: Simple and user-friendly design.
- **Django Powered**: Built using the robust Django web framework.

## 🛠 Installation & Setup

Follow these steps to get the project running locally on your machine.

### Prerequisites

- Python 3.8 or higher
- `pip` (Python package installer)
- `virtualenv` (recommended)

### Steps

1.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd todo-app-vibecode
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    # Create virtual environment
    virtualenv venv

    # Activate on Windows
    venv\Scripts\activate

    # Activate on macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install django
    ```

4.  **Apply migrations:**

    Initialize the database structure.

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5. **Run test:**

    ```bash
    python manage.py test todos
    ```
   
6. **Run the development server:**

    ```bash
    python manage.py runserver
    ```

7**Access the application:**

    Open your browser and go to `http://127.0.0.1:8000/`.

## 📁 Project Structure

- `todo_claude/`: Project configuration settings.
- `todos/`: Main application containing models, views, and logic for the todo list.
- `templates/`: HTML templates for the application.
- `manage.py`: Django's command-line utility for administrative tasks.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

*Built with Django*