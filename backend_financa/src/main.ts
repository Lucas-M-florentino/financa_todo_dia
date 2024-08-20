import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import * as cookieParser from 'cookie-parser';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  app.use(cookieParser());

  app.enableCors({
    origin: 'http://localhost:5173', // URL do frontend
    credentials: true, // Permite cookies e headers com credenciais
  });

  await app.listen(3001);
}
bootstrap();
