import { Injectable, OnModuleInit } from '@nestjs/common';
import { InjectConnection } from '@nestjs/typeorm';
import { Connection } from 'typeorm';

@Injectable()
export class AppService implements OnModuleInit {
  constructor(@InjectConnection() private readonly connection: Connection) {}

  async onModuleInit() {
    const queryRunner = this.connection.createQueryRunner();
    await queryRunner.connect();

    await queryRunner.query(`
      CREATE TABLE IF NOT EXISTS financa (
        id SERIAL PRIMARY KEY,
        descricao VARCHAR(255) NOT NULL,
        valor DECIMAL NOT NULL,
        tipo VARCHAR(255) NOT NULL
      );
    `);

    await queryRunner.release();
  }
}
