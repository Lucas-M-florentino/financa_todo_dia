import { Controller, Get, UseGuards } from '@nestjs/common';
import { JwtAuthGuard } from '../../auth/jwt-auth.guard';

@Controller('transacao')
export class TransacaoController {
  @UseGuards(JwtAuthGuard)
  @Get()
  findAll() {
    // Lógica para retornar transações
  }
}
