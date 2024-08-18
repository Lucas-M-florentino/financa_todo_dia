import { Body, Controller, Get, Post } from '@nestjs/common';
import { TransacaoService } from './transacao.service';
import { Transacao } from './transacao.entity';

@Controller('transacoes')
export class TransacaoController {
  constructor(private readonly transacaoService: TransacaoService) {}

  @Post()
  create(@Body() transacao: Transacao) {
    return this.transacaoService.create(transacao);
  }

  @Get()
  findAll() {
    return this.transacaoService.findAll();
  }
}
