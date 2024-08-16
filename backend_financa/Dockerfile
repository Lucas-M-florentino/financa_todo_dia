# Dockerfile for backend_financa
# Use the official Node.js image as a base image
FROM node:20-alpine AS builder

# Install tzdata and curl
RUN apk add --no-cache tzdata curl

# Set the timezone
ENV TZ=America/Cuiaba

# Set the working directory in the image
WORKDIR /usr/src/app

# Copy only the package files needed for dependencies installation
COPY package.json ./
COPY yarn.lock ./

# Install development dependencies and perform the build
RUN yarn install

COPY tsconfig.build.json ./
COPY tsconfig.json ./
COPY nest-cli.json ./
COPY src ./src

RUN yarn build

# Use the same Node.js base image for the production image
FROM node:20-alpine AS production

# Install tzdata and curl
RUN apk add --no-cache tzdata curl

# Set the timezone
ENV TZ=America/Cuiaba

# Set the working directory in the production image
WORKDIR /usr/src/app

# Create a non-root user to run the app and make the app directory owned by this user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
RUN chown appuser:appgroup /usr/src/app

# Switch to user 'appuser'
USER appuser

# Copy the built application and dependencies from the builder stage
COPY --from=builder /usr/src/app/node_modules ./node_modules
COPY --from=builder /usr/src/app/dist ./dist


# Start the server using the production build
CMD [ "node", "dist/main.js" ]