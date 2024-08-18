import { Module } from '@nestjs/common';
import { TransacaoModule } from './modules/transacao/transacao.module';
// import { RelatorioModule } from './modules/relatorio/relatorio.module';

@Module({
  imports: [
    TransacaoModule,
    // RelatorioModule,
  ],
})
export class AppModule {}
