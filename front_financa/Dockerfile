FROM node:18-alpine AS build

WORKDIR /app

# Copy package files
COPY package*.json vite.config.js index.html ./
# Install dependencies
RUN npm install 


COPY src ./src
COPY public ./public

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy build output from build stage
COPY --from=build /app/dist /app/node_modules /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 5173

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
