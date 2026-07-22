databases:
  - name: edgeboard-postgres
    plan: basic-256mb
    region: ohio
    postgresMajorVersion: "17"
    databaseName: edgeboard
    user: edgeboard
    connectionPool: pgbouncer

services:
  - type: web
    name: edgeboard-api
    runtime: docker
    region: ohio
    plan: starter
    rootDir: apps/api
    dockerfilePath: ./Dockerfile
    healthCheckPath: /healthz
    preDeployCommand: alembic upgrade head
    autoDeployTrigger: checksPass
    envVars:
      - key: ENVIRONMENT
        value: production
      - key: DATABASE_URL
        fromDatabase:
          name: edgeboard-postgres
          property: connectionPoolString
      - key: FRONTEND_URL
        sync: false
      - key: CORS_ORIGINS
        sync: false
      - key: JWT_SECRET
        generateValue: true
      - key: REFRESH_TOKEN_PEPPER
        generateValue: true
      - key: COOKIE_SECURE
        value: "true"
      - key: COOKIE_SAMESITE
        value: none
      - key: COOKIE_DOMAIN
        sync: false
      - key: ODDS_API_KEY
        sync: false
      - key: STRIPE_SECRET_KEY
        sync: false
      - key: STRIPE_WEBHOOK_SECRET
        sync: false
      - key: STRIPE_PRICE_PRO_MONTHLY
        sync: false
      - key: STRIPE_PRICE_ELITE_MONTHLY
        sync: false
      - key: RESEND_API_KEY
        sync: false
      - key: EMAIL_FROM
        sync: false
      - key: CRON_SECRET
        generateValue: true
      - key: ADMIN_EMAIL
        sync: false
      - key: ADMIN_PASSWORD
        sync: false
      - key: DEMO_MODE
        value: "false"

  - type: web
    name: edgeboard-web
    runtime: node
    region: ohio
    plan: starter
    rootDir: apps/web
    buildCommand: npm install && npm run build
    startCommand: npm run start
    healthCheckPath: /
    autoDeployTrigger: checksPass
    envVars:
      - key: NODE_VERSION
        value: 22.15.0
      - key: NEXT_PUBLIC_API_URL
        sync: false
      - key: INTERNAL_API_URL
        fromService:
          type: web
          name: edgeboard-api
          property: hostport

  - type: cron
    name: edgeboard-refresh
    runtime: docker
    region: ohio
    plan: starter
    rootDir: apps/api
    dockerfilePath: ./Dockerfile
    schedule: "*/30 * * * *"
    dockerCommand: python -m app.jobs.refresh
    envVars:
      - key: ENVIRONMENT
        value: production
      - key: DATABASE_URL
        fromDatabase:
          name: edgeboard-postgres
          property: connectionPoolString
      - key: ODDS_API_KEY
        sync: false
      - key: MODEL_VERSION
        value: 3.0.0
      - key: DEMO_MODE
        value: "false"

  - type: cron
    name: edgeboard-grade
    runtime: docker
    region: ohio
    plan: starter
    rootDir: apps/api
    dockerfilePath: ./Dockerfile
    schedule: "15 */2 * * *"
    dockerCommand: python -m app.jobs.grade
    envVars:
      - key: ENVIRONMENT
        value: production
      - key: DATABASE_URL
        fromDatabase:
          name: edgeboard-postgres
          property: connectionPoolString
      - key: DEMO_MODE
        value: "false"
