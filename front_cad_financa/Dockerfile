# Use the official Node.js image as a base image
FROM jitesoft/node-yarn:20 AS builder

# Install tzdata, curl, and yarn via apk
RUN apk add --no-cache tzdata curl yarn

# Set the timezone
ENV TZ=America/Cuiaba

# Set the working directory in the image
WORKDIR /home/app

# Copy only the package files needed for dependencies installation

COPY package.json yarn.lock ./

# Install development dependencies and perform the build
RUN yarn install --ignore-scripts

# RUN mkdir node_modules/.cache && chmod -R 777 node_modules/.cache

COPY  vite.config.js jsconfig.json index.html ./
COPY src ./src
COPY public ./public

RUN yarn build
