
import { Injectable } from '@nestjs/common';
import { Transacao } from './transacao.entity';

@Injectable()
export class TransacaoService {
  private transacoes: Transacao[] = [];

  create(transacao: Transacao): Transacao {
    this.transacoes.push(transacao);
    return transacao;
  }

  findAll(): Transacao[] {
    return this.transacoes;
  }
}
