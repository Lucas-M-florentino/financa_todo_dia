# Dockerfile for front_cad_financa

# Build Stage
FROM node:20-alpine AS builder

# Set the timezone
ENV TZ=America/Cuiaba

# Working directory
WORKDIR /usr/src/app

# Install dependencies and build the project
COPY package.json ./
COPY yarn.lock ./
RUN yarn install
COPY vite.config.js ./
COPY src ./src
COPY index.html ./
RUN yarn build

# Production Stage
FROM nginx:alpine AS production

# Copy build output to NGINX html folder
COPY --from=builder /usr/src/app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start NGINX server
CMD ["nginx", "-g", "daemon off;"]
