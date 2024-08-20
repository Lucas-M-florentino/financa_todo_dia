import { Entity, Column, PrimaryGeneratedColumn } from 'typeorm';

@Entity()
export class Financa {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  descricao: string;

  @Column('decimal')
  valor: number;

  @Column()
  tipo: string;
}
