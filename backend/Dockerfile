# syntax=docker/dockerfile:1

# Use an LTS node image as the base for the backend service
FROM node:18-alpine

# Configure the work directory and copy dependency manifests first to leverage Docker layer caching
WORKDIR /app
COPY package*.json ./

# Install dependencies separately to reuse this layer when code changes but dependencies do not
RUN npm ci --omit=dev || npm install --omit=dev

# Copy the rest of the backend source code into the container image
COPY . .

# Expose the default port used by the backend server
EXPOSE 3000

# Provide the default start command for Railway deployments
CMD ["npm", "run", "start"]
