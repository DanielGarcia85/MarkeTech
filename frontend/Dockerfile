# ---- 1. Build stage ----

# Image for building the frontend application
# Uses Node.js 20 on Alpine Linux for a lightweight build environment
FROM node:20-alpine AS build

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json files
COPY package*.json ./

# Install dependencies using npm ci for a clean install based on package-lock.json
RUN npm ci

# Copy the rest of the application source code
COPY . .

# Build the Vue.js frontend application
# This will create a 'dist' directory with the production-ready files
RUN npm run build

# ---- 2. Runtime stage ----

# Image for serving the built frontend application
# Uses Nginx on Alpine Linux for a lightweight web server
FROM nginx:stable-alpine AS production

# Copy built files from the build stage to nginx's public folder
COPY --from=build /app/dist /usr/share/nginx/html

# Optional: copy custom nginx config (if needed) -> Yes, we need it to handle SPA routing
COPY ./nginx.conf /etc/nginx/conf.d/default.conf

# Expose port (useful if running directly, not needed with docker-compose)
EXPOSE 80

# Start nginx server (default in nginx image)
CMD ["nginx", "-g", "daemon off;"]
