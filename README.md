# Multi-tenant Todo App

Let's start with the most important thing, theory about what we're going to build.

## From Single-User to Multi-Tenant

Earlier, we built a todo app with FastAPI, SQLModel, and PostgreSQL. While a great starting point, a single-user app has limited real-world applications. It's time to level up! We're now building a multi-tenant todo app where multiple users can securely register, manage their own tasks.

### Key Considerations in a Multi-Tenant Todo App

*  **User Isolation:** Crucially, one user cannot access or modify tasks belonging to another user. This strict isolation is a fundamental requirement in multi-tenant systems.

*  **Authentication:** We'll implement the robust OAuth2 standard for secure user authentication and authorization.

## Main Steps
1. **Setup** a new project with poetry.
	~~~
	poetry new my-todo-app
	~~~ 
change path to project directory `cd my-todo-app`

2. **Create** FastAPI:
Create a FastAPI application with necessary dependencies.
	~~~
	poetry add fastapi sqlmodel psycopg 'uvicorn[standard]' "psycopg[binary]"
	~~~
	For the initial setup, we only need these dependencies. But we'll add more as we 				progress on our project.

  

3. **Signup/Login** on [Neon Serverless Postgres](https://neon.tech/), and create your database. Neon is a fully managed serverless Postgres with a generous free tier.
Create a .env file in project root directory, copy the connection string provided in neon.tech dashboard (after unmasking), and paste in .env file like so.
	~~~
	DEBUG = True
	DATABASE_URL = postgresql://todos_owner:BxroAE39fQgY@ep-old-bar-a1rynmsu-	pooler.ap-southeast-1.aws.neon.tech/todo?sslmode=require
	~~~
	***Note:** This URL won't work when you clone. I intentionally changed it. Make sure to replace it with your own*