import { Injectable } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';

@Injectable()
export class AuthService {
  constructor(private readonly jwtService: JwtService) {}

  async login(loginData: any): Promise<string> {
    // Valide o loginData (usuário e senha)
    const payload = { username: loginData.username, sub: loginData.userId };
    
    // Gera o JWT
    return this.jwtService.sign(payload);
  }
}
