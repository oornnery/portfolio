from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel import SQLModel, select

from app.config import settings

# Import all models to register them with SQLModel
from app.models.blog import Post, Reaction  # noqa: F401
from app.models.project import Project  # noqa: F401

engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)

async_session_factory = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with async_session_factory() as session:
        yield session


async def seed_db():
    async with async_session_factory() as session:
        # Check if we have posts
        result = await session.execute(select(Post))
        post = result.scalars().first()
        
        if not post:
            # Create sample posts
            posts = [
                Post(
                    title="Welcome to My Portfolio",
                    slug="welcome-to-my-portfolio",
                    description="A brief introduction to my new portfolio built with FastAPI and HTMX.",
                    content="""
# Welcome to My Portfolio

This is the first post on my new portfolio website. I decided to rebuild it using a modern stack that focuses on performance and simplicity.

## The Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Jinja2 Templates + HTMX
- **Database**: PostgreSQL
- **Styling**: Custom CSS with Dracula Theme

## Why HTMX?

HTMX allows me to build a dynamic, single-page-app-like experience without the complexity of a full JavaScript framework like React or Vue. It's perfect for a content-focused site like a portfolio.

Stay tuned for more updates!
                    """,
                    category="personal",
                    tags=["portfolio", "fastapi", "htmx"],
                    reading_time=2,
                    image="https://images.unsplash.com/photo-1499750310159-5b5f226932b7?auto=format&fit=crop&w=800&q=80"
                ),
                Post(
                    title="Building Scalable APIs with FastAPI",
                    slug="building-scalable-apis-fastapi",
                    description="Learn how to structure your FastAPI application for scale and maintainability.",
                    content="""
# Building Scalable APIs with FastAPI

FastAPI is an incredible framework, but as your application grows, you need to structure it correctly.

## Project Structure

I recommend a structure like this:

```
app/
  api/
    v1/
      endpoints/
  core/
  models/
  schemas/
  services/
  main.py
```

## Dependency Injection

FastAPI's dependency injection system is powerful. Use it for:

1. Database sessions
2. Authentication
3. Configuration settings

## Conclusion

With the right structure, FastAPI can handle massive scale while keeping your code clean and maintainable.
                    """,
                    category="tech",
                    tags=["fastapi", "python", "architecture"],
                    reading_time=5,
                    image="https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=800&q=80"
                ),
                Post(
                    title="The Power of HTMX",
                    slug="the-power-of-htmx",
                    description="Why I chose HTMX for my frontend and why you should consider it too.",
                    content="""
# The Power of HTMX

HTMX gives you access to AJAX, CSS Transitions, WebSockets and Server Sent Events directly in HTML, using attributes.

## Simplicity

You don't need a complex build step or a massive bundle size. Just include the script and start adding attributes to your HTML.

```html
<button hx-post="/clicked" hx-swap="outerHTML">
  Click Me
</button>
```

## Server-Driven UI

With HTMX, your server is the source of truth for the UI state. This simplifies your logic significantly.
                    """,
                    category="tech",
                    tags=["htmx", "frontend", "javascript"],
                    reading_time=3,
                    image="https://images.unsplash.com/photo-1627398242454-45a1465c2479?auto=format&fit=crop&w=800&q=80"
                ),
                Post(
                    title="My Journey as a Developer",
                    slug="my-journey-as-developer",
                    description="Reflecting on my path from Hello World to Senior Engineer.",
                    content="""
# My Journey as a Developer

It started with a simple HTML file...

## The Beginning

I remember writing my first line of code. It was magical.

## The Struggles

Learning wasn't always easy. I struggled with:

- Asynchronous programming
- CSS centering (who hasn't?)
- Deployment

## The Future

I'm excited about the future of web development, especially with tools like AI assisting us.
                    """,
                    category="career",
                    tags=["career", "personal", "reflection"],
                    reading_time=4,
                    image="https://images.unsplash.com/photo-1517694712202-14dd9538aa97?auto=format&fit=crop&w=800&q=80"
                )
            ]
            
            session.add_all(posts)
            await session.commit()

        # Check if we have projects
        result = await session.execute(select(Project))
        project = result.scalars().first()
        
        if not project:
            projects = [
                Project(
                    title="AI Portfolio Assistant",
                    slug="ai-portfolio-assistant",
                    description="An intelligent assistant that helps you build and manage your portfolio.",
                    content="""
# AI Portfolio Assistant

This project leverages the power of LLMs to help developers create stunning portfolios.

## Features

- **Code Generation**: Automatically generates boilerplate code.
- **Content Writing**: Helps write blog posts and project descriptions.
- **Theme Customization**: Suggests color palettes and layouts.

## Tech Stack

- Python
- LangChain
- OpenAI API
- FastAPI
                    """,
                    image="https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&w=800&q=80",
                    tech_stack=["Python", "LangChain", "OpenAI", "FastAPI"],
                    category="ai",
                    github_url="https://github.com/oornnery/ai-portfolio",
                    demo_url="https://ai-portfolio.example.com",
                    featured=True,
                    github_stars=120,
                    github_forks=30
                ),
                Project(
                    title="E-Commerce Microservices",
                    slug="ecommerce-microservices",
                    description="A scalable e-commerce backend built with microservices architecture.",
                    content="""
# E-Commerce Microservices

A robust backend system for a high-traffic e-commerce platform.

## Architecture

The system is divided into several services:

- **Auth Service**: Handles user authentication and authorization.
- **Product Service**: Manages product catalog and inventory.
- **Order Service**: Processes orders and payments.
- **Notification Service**: Sends emails and push notifications.

## Technologies

- Go
- gRPC
- Kafka
- Kubernetes
                    """,
                    image="https://images.unsplash.com/photo-1556742049-0cfed4f7a07d?auto=format&fit=crop&w=800&q=80",
                    tech_stack=["Go", "gRPC", "Kafka", "Kubernetes", "Docker"],
                    category="backend",
                    github_url="https://github.com/oornnery/ecommerce-microservices",
                    featured=True,
                    github_stars=85,
                    github_forks=12
                ),
                Project(
                    title="Task Master",
                    slug="task-master",
                    description="A productivity app for managing tasks and projects.",
                    content="""
# Task Master

Stay organized and productive with Task Master.

## Key Features

- **Kanban Boards**: Visualize your workflow.
- **Time Tracking**: Keep track of time spent on tasks.
- **Collaboration**: Work with your team in real-time.

## Built With

- React
- Redux
- Node.js
- MongoDB
                    """,
                    image="https://images.unsplash.com/photo-1484480974693-6ca0a78fb36b?auto=format&fit=crop&w=800&q=80",
                    tech_stack=["React", "Node.js", "MongoDB", "Socket.io"],
                    category="web",
                    github_url="https://github.com/oornnery/task-master",
                    demo_url="https://taskmaster.example.com",
                    featured=False,
                    github_stars=45,
                    github_forks=5
                ),
                Project(
                    title="Weather CLI",
                    slug="weather-cli",
                    description="A command-line interface for checking the weather.",
                    content="""
# Weather CLI

Get the weather forecast directly in your terminal.

## Usage

```bash
weather city london
```

## Features

- **Fast**: Written in Rust for maximum performance.
- **Accurate**: Uses OpenWeatherMap API.
- **Beautiful**: Colorful output with ASCII art.
                    """,
                    image="https://images.unsplash.com/photo-1592210454359-9043f067919b?auto=format&fit=crop&w=800&q=80",
                    tech_stack=["Rust", "CLI", "API"],
                    category="tool",
                    github_url="https://github.com/oornnery/weather-cli",
                    featured=False,
                    github_stars=230,
                    github_forks=40
                )
            ]
            
            session.add_all(projects)
            await session.commit()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    await seed_db()
