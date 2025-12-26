# Kanori Service

Kanori is a productivity web application designed to help users bring order to their daily lives by integrating kanban task management, time blocking, focused work sessions, and note-taking into a single, cohesive system. This repository contains the **Django backend** for Kanori, providing the API and data models that power the app's core features.

## Video Demo

[https://www.youtube.com/watch?v=lY0hmQH6Bxs](https://www.youtube.com/watch?v=lY0hmQH6Bxs)

## Project Overview

The backend is structured to support the following main features:

- **Task Management**: Organize tasks into statuses (To Do, Doing, Today, Done) using a kanban-style workflow. Each task can have estimated time, color coding, and progress tracking.
- **Time Blocking**: Schedule tasks into blocks, allowing users to plan their day and visualize their time allocation.
- **Focus Sessions**: Track focused work sessions, including duration, notes, and success status. Sessions are aggregated into daily summaries for productivity insights.
- **Notes**: Simple note-taking with color coding for organization.
- **User Settings**: Store user preferences such as day boundaries and column colors.

## File Structure and Key Files

- **manage.py**: Django's command-line utility for administrative tasks.
- **config/**: Django project configuration (settings, URLs, WSGI/ASGI entry points).
- **core/**: Main app containing models, serializers, views, and migrations.
  - **models/**: Defines core entities:
    - `Task`: Kanban task with status, color, estimated minutes, and progress.
    - `FocusSession`: Tracks focused work sessions linked to tasks.
    - `DaySummary`: Aggregates daily focus data per user.
    - `Block`: Time blocks for scheduling tasks.
    - `Setting`: User preferences (day bounds, colors).
    - `Note`: User notes with color and content.
  - **serializers/**: DRF serializers for API representation.
  - **views/**: API endpoints for authentication and main app logic.
  - **migrations/**: Database schema migrations.

## API

The backend exposes a RESTful API (typically at `/api/`) for all core resources. It is designed to be consumed by the Kanori frontend (Vue 3, PWA), but can be used by any client.

## Design Decisions

- **Modular Models**: Each productivity concept (task, block, focus session, note) is a separate model, allowing for clear separation of concerns and easy extensibility.
- **Status Choices**: Task statuses are implemented using Django's `TextChoices` for clarity and validation.
- **Aggregations**: Use of Django ORM aggregations for efficient summary calculations (e.g., total focused minutes).
- **Color Validation**: Hex color fields are validated to ensure consistent theming.
- **Signals**: Post-save signals keep daily summaries in sync with focus session data.

## Project Setup

1. **Clone the repository**

   ```sh
   git clone <repo-url>
   cd Kanori-service
   ```

2. **Install dependencies**

   ```sh
   pip install -r requirements.txt
   ```

3. **Apply migrations**

   ```sh
   python manage.py migrate
   ```

5. **Run the development server**

   ```sh
   python manage.py runserver
   ```

