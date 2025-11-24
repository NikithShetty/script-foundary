FROM node:20-alpine

WORKDIR /app

# Install dependencies
RUN apk add --no-cache libc6-compat

# Copy package files
COPY package.json package-lock.json* ./
RUN npm ci

# Copy application code
COPY . .

# Set environment variable
ENV NEXT_TELEMETRY_DISABLED 1

EXPOSE 3000

# For development, use dev server
CMD ["npm", "run", "dev"]

