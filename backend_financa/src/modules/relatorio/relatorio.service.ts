

import { Injectable } from '@nestjs/common';
import { Relatorio } from './relatorio.entity';

@Injectable()
export class RelatorioService {
  private relatorios: Relatorio[] = [];

  create(relatorio: Relatorio): Relatorio {
    this.relatorios.push(relatorio);
    return relatorio;
  }

  findAll(): Relatorio[] {
    return this.relatorios;
  }
}
