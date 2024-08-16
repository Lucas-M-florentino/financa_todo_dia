# Use the official Node.js image as a base image
FROM jitesoft/node-yarn:20 AS builder

# Install tzdata and curl
RUN apk add --no-cache tzdata curl

# Set the timezone
ENV TZ=America/Cuiaba

# RUN mkdir /app && chown node:node /app

# Set the working directory in the image
WORKDIR /usr/src/app

# Copy only the package files needed for dependencies installation
# USER node
# COPY --chown=node:node
COPY package.json yarn.lock ./

# Install development dependencies
RUN yarn install --ignore-scripts

# RUN mkdir node_modules/.cache && chmod -R 777 node_modules/.cache

# Copy source code
# COPY --chown=node:node 
COPY tsconfig.build.json tsconfig.json nest-cli.json .swcrc ./
# COPY --chown=node:node 
COPY src ./src

# Build the application
RUN yarn build

# Use the same Node.js base image for the production image
FROM jitesoft/node-yarn:20 AS production

# Install tzdata and curl
RUN apk add --no-cache tzdata curl

# Set the timezone
ENV TZ=America/Cuiaba

# Set the working directory in the production image
WORKDIR /usr/src/app

# Create a non-root user to run the app and make the app directory owned by this user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
RUN chown -R appuser:appgroup /usr/src/app

# Switch to user 'appuser'
USER appuser

# Copy the built application and dependencies from the builder stage
COPY --from=builder /usr/src/app/node_modules ./node_modules
COPY --from=builder /usr/src/app/dist ./dist

# Start the server using the production build
CMD [ "node", "dist/main.js" ]
