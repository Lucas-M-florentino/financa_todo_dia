import { Entity, Column, PrimaryGeneratedColumn } from 'typeorm';

@Entity()
export class Transacao {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  descricao: string;

  @Column('decimal')
  valor: number;

  @Column()
  tipo: string; // receita ou despesa
}
