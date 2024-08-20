import { Controller, Get, UseGuards } from '@nestjs/common';
import { JwtAuthGuard } from '../../auth/jwt-auth.guard';

@Controller('relatorio')
export class RelatorioController {
  @UseGuards(JwtAuthGuard)
  @Get()
  findAll() {
    // Lógica para retornar relatórios
  }
}
