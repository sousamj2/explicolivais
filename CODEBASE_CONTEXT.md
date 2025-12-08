# Codebase Context: explicolivais

This document provides a high-level overview of the `explicolivais` web application, its architecture, and key components. It is intended to be a living document that can be updated as the codebase evolves.

## Project Summary

The project is a Flask-based web application, likely an educational platform named 'explicolivais' that offers quizzes and has a tiered subscription system.

## Architecture

*   **Application Core:** `explicolivais.py` is the heart of the application, using the factory pattern (`create_app`) to initialize Flask, load configuration from `config.py`, and register all routes.
*   **Routing:** The application is modularized using Flask Blueprints, located in the `blueprints/` directory. Each blueprint corresponds to a feature (e.g., `quiz.py`, `profile.py`). An interesting pattern is the use of routes suffixed with '314' (e.g., `/signin314`), which appear to be the active, functional versions of pages, while their non-suffixed counterparts are often placeholders.
*   **Data Layer:** The application uses a MySQL database. The schema is defined in raw SQL files within `SQLiteQueries/createHandlerMySQL/`. The `DBhelpers/` directory serves as a data access layer, containing Python functions to connect to the database, create tables, and run queries. It does not use an ORM like SQLAlchemy.
*   **Business Logic:** Core logic and utilities are placed in the `Funhelpers/` directory. This includes quiz scoring logic (`quiz_helpers.py`), email sending (`send_email.py`), and other miscellaneous functions.
*   **Deployment:** For development, `runFlask.sh` is used to initialize the database and start the Flask development server. For production, `server.py` is the entry point, using the `waitress` WSGI server.

## Key Insights

*   The application is an educational platform with user authentication, profiles, and a quiz system.
*   The use of a `tier` column in the `users` table suggests a subscription-based service.
*   The database schema is managed via raw SQL files, not an ORM.
*   The '314' routes are a convention for active endpoints, which is important for anyone navigating the frontend or API surface.
*   The project is well-structured, separating concerns into blueprints, helpers, and configuration files.

## Relevant Locations

| File/Directory | Reasoning | Key Symbols |
| :--- | :--- | :--- |
| `explicolivais.py` | Main application entry point. Creates the Flask app and registers blueprints. | `create_app`, `app` |
| `server.py` | Production entry point using the `waitress` WSGI server. | `serve` |
| `runFlask.sh` | Development server startup script. Sets environment and initializes the database. | |
| `blueprints/` | Contains Flask Blueprints for routing. Each file is a feature. | `bp_signin`, `quiz_bp`, `bp_profile` |
| `DBhelpers/` | Data access layer for database interactions. | `get_mysql_connection`, `setup_mysql_database`, `create_tables` |
| `SQLiteQueries/createHandlerMySQL/` | Contains raw SQL files for the database schema. | |
| `Funhelpers/` | Utility and business logic functions. | `calculate_score`, `send_email` |
| `config.py` | Configuration for different environments. | `config`, `DevelopmentConfig`, `ProductionConfig` |
