services:
  postgres:
    image: postgres:17-alpine
    environment:
      POSTGRES_DB: edgeboard
      POSTGRES_USER: edgeboard
      POSTGRES_PASSWORD: edgeboard
    ports:
      - "5432:5432"
    volumes:
      - edgeboard_postgres:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U edgeboard -d edgeboard"]
      interval: 5s
      timeout: 5s
      retries: 20

  api:
    build: ./apps/api
    env_file: .env
    environment:
      DATABASE_URL: postgresql+psycopg://edgeboard:edgeboard@postgres:5432/edgeboard
    command: sh -c "alembic upgrade head && fastapi run app/main.py --host 0.0.0.0 --port 8000 --reload"
    volumes:
      - ./apps/api:/code
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy

  web:
    build: ./apps/web
    env_file: .env
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
      INTERNAL_API_URL: http://api:8000
    command: npm run dev -- --hostname 0.0.0.0
    volumes:
      - ./apps/web:/app
      - /app/node_modules
      - /app/.next
    ports:
      - "3000:3000"
    depends_on:
      - api

volumes:
  edgeboard_postgres:
