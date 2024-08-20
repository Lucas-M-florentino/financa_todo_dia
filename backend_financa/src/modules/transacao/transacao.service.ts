import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Transacao } from './transacao.entity';

@Injectable()
export class TransacaoService {
  constructor(
    @InjectRepository(Transacao)
    private transacaoRepository: Repository<Transacao>,
  ) {}

  findAll(): Promise<Transacao[]> {
    return this.transacaoRepository.find();
  }

  create(transacao: Transacao): Promise<Transacao> {
    return this.transacaoRepository.save(transacao);
  }
}
