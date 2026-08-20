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

# Install backend dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend ./

# Copy built frontend to backend's static directory
COPY --from=frontend-builder /app/frontend/.next /app/public/.next
COPY --from=frontend-builder /app/frontend/public /app/public

# Start the backend API server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
