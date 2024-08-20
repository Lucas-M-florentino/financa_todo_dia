import { Controller, Get, UseGuards } from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';

@Controller('api')
export class AppController {
  @Get('dados')
  @UseGuards(AuthGuard('jwt'))
  getDados() {
    return { message: 'Dados protegidos por JWT!' };
  }
}
