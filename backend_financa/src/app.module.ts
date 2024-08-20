import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { typeOrmConfig } from './config/database.config';
import { AuthModule } from './auth/auth.module';
import { TransacaoModule } from './modules/transacao/transacao.module';
import { RelatorioModule } from './modules/relatorio/relatorio.module';
import { AppService } from './app.service';

@Module({
  imports: [
    TypeOrmModule.forRoot(typeOrmConfig), // Configuração do banco de dados
    AuthModule,
    TransacaoModule,
    RelatorioModule,
  ],
  providers: [AppService], // Serviços globais do módulo
})
export class AppModule {}
