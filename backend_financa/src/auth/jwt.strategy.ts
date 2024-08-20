import { Strategy } from 'passport-jwt';
import { PassportStrategy } from '@nestjs/passport';
import { Injectable, UnauthorizedException } from '@nestjs/common';
import { Request } from 'express';

@Injectable()
export class JwtStrategy extends PassportStrategy(Strategy) {
  constructor() {
    super({
      jwtFromRequest: (req: Request) => {
        const token = req.cookies.jwt; // Captura o token do cookie
        if (!token) {
          throw new UnauthorizedException();
        }
        return token;
      },
      secretOrKey: 'secretKey', // Trocar para uma variável de ambiente em produção
    });
  }

  async validate(payload: any) {
    // Lógica de validação do payload do token JWT
    return { userId: payload.sub, username: payload.username };
  }
}
