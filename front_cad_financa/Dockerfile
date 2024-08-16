# Use the official Node.js image as a base image
FROM jitesoft/node-yarn:20 AS builder

# Install tzdata, curl, and yarn via apk
RUN apk add --no-cache tzdata curl yarn

# Set the timezone
ENV TZ=America/Cuiaba

# Set the working directory in the image
WORKDIR /usr/src/app

# Copy only the package files needed for dependencies installation

COPY package.json yarn.lock index.html ./

# Install development dependencies and perform the build
RUN yarn install --ignore-scripts

RUN mkdir node_modules/.cache && chmod -R 777 node_modules/.cache

COPY  vite.config.js ./
COPY src ./src

RUN yarn build

# Use the same Node.js base image for the production image
FROM jitesoft/node-yarn:20 AS production

# Install tzdata, curl, and yarn via apk
RUN apk add --no-cache tzdata curl yarn

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
