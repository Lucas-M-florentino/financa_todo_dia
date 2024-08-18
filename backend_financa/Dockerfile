# Dockerfile
# Use the official Node.js image as a base image
FROM node:21-alpine3.19 AS builder

# Install tzdata and curl
RUN apk add --no-cache tzdata curl

# Set the timezone
ENV TZ=America/Cuiaba

# Set the working directory in the image
WORKDIR /home/app

# Copy only the package files needed for dependencies installation
COPY package.json yarn.lock ./

# Install development dependencies
RUN yarn install --ignore-scripts

# Copy source code
COPY tsconfig.build.json tsconfig.json nest-cli.json .swcrc ./
COPY src ./src

# Build the application
RUN yarn build

# # Etapa 2: Imagem de produção
# FROM node:21-alpine3.19 AS production

# # Instalar pacotes necessários
# RUN apk add --no-cache tzdata curl

# # Configurar o fuso horário
# ENV TZ=America/Cuiaba

# # Definir o diretório de trabalho
# WORKDIR /home/app

# # Criar um usuário e grupo não-root
# RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# # Garantir que o diretório de trabalho tenha permissões adequadas
# RUN mkdir -p /home/app/dist && chown -R appuser:appgroup /home/app

# # Copiar a aplicação e as dependências da etapa de build
# COPY --from=builder /home/app/node_modules ./node_modules
# COPY --from=builder /home/app/package.json ./
# COPY --from=builder /home/app/yarn.lock ./
# COPY --from=builder /home/app/tsconfig.build.json ./
# COPY --from=builder /home/app/tsconfig.json ./
# COPY --from=builder /home/app/nest-cli.json ./
# COPY --from=builder /home/app/.swcrc ./
# COPY --from=builder /home/app/dist ./dist

# # Alterar o usuário para 'appuser'
# USER appuser

# # Iniciar o servidor usando a build de produção
# CMD [ "node", "dist/main.js" ]
