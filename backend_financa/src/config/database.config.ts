import { TypeOrmModuleOptions } from '@nestjs/typeorm';
import { join } from 'path';

export const typeOrmConfig: TypeOrmModuleOptions = {
  type: 'postgres',
  host: 'localhost', // Ou o nome do serviço do Docker, se for diferente
  port: 5432,
  username: 'nest_user',
  password: 'nest_password',
  database: 'nest_db',
  entities: [join(__dirname, '../**/*.entity.{ts,js}')],
  synchronize: false, // Desabilitar synchronize para utilizar migrations
};
