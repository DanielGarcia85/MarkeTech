# frontend/Dockerfile
#
# Frontend image — Vue application compiled, then served by Nginx
# ─────────────────────────────────────────────────────────────────────────────
# Built in two stages: the first one compiles the application with Node.js,
# the second one only keeps the compiled files and Nginx. Node.js, the source
# code and the dependencies are not part of the final image.

# ── Stage 1: compile the application ─────────────────────────────────────────

# Official Node.js image, same major version as the development workstations
FROM node:22-alpine AS build

# Folder of the application inside this stage
WORKDIR /app

# Dependencies first, on their own: Docker reuses this step from its cache
# as long as the two package files do not change. "npm ci" installs exactly
# the versions recorded in package-lock.json.
COPY package.json package-lock.json ./
RUN npm ci

# Source code, except what .dockerignore lists
COPY . .

# Check the types, then compile into static files in /app/dist
RUN npm run build

# ── Stage 2: serve the compiled files ────────────────────────────────────────

# Official Nginx image, stable branch
FROM nginx:stable-alpine

# Compiled application, taken from the first stage
COPY --from=build /app/dist /usr/share/nginx/html

# Our configuration replaces the default site of the image
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Port Nginx listens on. Declared for documentation: nothing is published
# to the outside from here.
EXPOSE 80
