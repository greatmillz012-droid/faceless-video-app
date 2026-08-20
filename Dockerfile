# Build frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend .
RUN npm run build

# Build backend
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend ./
COPY --from=frontend-builder /app/frontend/.next /app/public/.next
COPY --from=frontend-builder /app/frontend/public /app/public
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
