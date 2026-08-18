# Checklist de segurança (Fase B)

## Autenticação e bloqueio

- [x] **3 tentativas de login falhas** → usuário bloqueado automaticamente (`LOGIN_MAX_FAILED_ATTEMPTS`)
- [x] Usuário **inativo** ou **bloqueado** não autentica
- [x] JWT revalidado: usuário bloqueado/inativo perde acesso imediato (`GET /v1/users/logged` e rotas protegidas)
- [x] **Admin bloqueia/desbloqueia** via `POST /v1/users/{id}/block` e `/unblock` (permissões `users:block`, `users:unblock`)

## Recuperação de senha

- [x] Token enviado por e-mail em **texto plano** (uso único, curta validade)
- [x] Token persistido como **SHA-256** no banco (`reset_password_token`)
- [x] Limite de **3 solicitações em 30 dias** por usuário (`PASSWORD_RESET_MAX_REQUESTS`, `PASSWORD_RESET_WINDOW_DAYS`)

## Política de senha

- [x] Comprimento mínimo configurável (`PASSWORD_MIN_LENGTH`) em cadastro e reset

## Rate limiting (por IP)

- [x] Login (`RATE_LIMIT_LOGIN_PER_MINUTE`)
- [x] Signup (`RATE_LIMIT_SIGNUP_PER_MINUTE`)
- [x] Forgot password (`RATE_LIMIT_FORGOT_PASSWORD_PER_MINUTE`)

> Implementação em memória (adequada para instância única). Em cluster, usar Redis ou similar.

## CORS

- [x] Origens configuráveis via `CORS_ORIGINS` (lista separada por vírgula ou `*`)
- [x] `allow_credentials=False` quando `CORS_ORIGINS=*`

## Auditoria

Eventos registrados: `auth.login.*`, `auth.password.reset.*`, `user.blocked`, `user.unblocked`, `user.auto_blocked`.

## Produção — revisar antes do deploy

- [ ] `SECRET` forte e único
- [ ] `CORS_ORIGINS` restrito ao domínio do frontend
- [ ] SMTP configurado para reset de senha
- [ ] Alterar credenciais do admin inicial (`init_db/database.sql`)
- [ ] HTTPS terminado no reverse proxy
- [ ] Considerar rate limit distribuído (Redis) se houver múltiplas réplicas
