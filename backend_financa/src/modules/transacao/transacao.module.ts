
import { Module } from '@nestjs/common';
import { TransacaoController } from './transacao.controller';
import { TransacaoService } from './transacao.service';

@Module({
  controllers: [TransacaoController],
  providers: [TransacaoService],
})
export class TransacaoModule {}
