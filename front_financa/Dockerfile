FROM node:18-alpine AS build

WORKDIR /app

# Copy package files
COPY package.json vite.config.js index.html ./
COPY src ./src

# Install dependencies
RUN npm install -g pnpm && pnpm install

# Build the application
RUN pnpm run build

# Production stage
FROM nginx:alpine

# Copy build output from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 5173

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
