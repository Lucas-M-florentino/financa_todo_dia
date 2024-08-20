import { Controller, Post, Body, Res } from '@nestjs/common';
import { AuthService } from './auth.service';
import { Response } from 'express';

@Controller('auth')
export class AuthController {
  constructor(private readonly authService: AuthService) {}

  @Post('login')
  async login(@Body() loginData, @Res() res: Response) {
    const jwtToken = await this.authService.login(loginData);

    res.cookie('jwt', jwtToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production', // Use HTTPS em produção
      maxAge: 3600000, // Expira em 1 hora
    });

    return res.send({ message: 'Login bem-sucedido' });
  }

  @Post('logout')
  logout(@Res() res: Response) {
    res.clearCookie('jwt');
    return res.send({ message: 'Logout bem-sucedido' });
  }
}
