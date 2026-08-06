-- Schema version: 1.4.0
-- Novidades: UNIQUE em users.email

CREATE TABLE public.roles (
    id          SERIAL PRIMARY KEY,
    description VARCHAR NOT NULL,
    active      BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC')
);

CREATE TABLE public.users (
    id                     SERIAL PRIMARY KEY,
    password               VARCHAR(255),
    name                   VARCHAR(50) NOT NULL,
    email                  VARCHAR(50) NOT NULL,
    phone                  VARCHAR(12) NOT NULL,
    cpf                    VARCHAR(12),
    role_id                INTEGER DEFAULT 1,
    auth_provider          VARCHAR(20) NOT NULL DEFAULT 'local',
    google_id              VARCHAR(255),
    failed_login_attempts  INTEGER NOT NULL DEFAULT 0,
    reset_password_token   VARCHAR(255),
    reset_password_expires TIMESTAMP,
    active                 BOOLEAN NOT NULL DEFAULT TRUE,
    created_at             TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
    CONSTRAINT users_email_key UNIQUE (email),
    CONSTRAINT users_cpf_key UNIQUE (cpf),
    CONSTRAINT users_google_id_key UNIQUE (google_id),
    CONSTRAINT users_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles (id)
);

CREATE TABLE public.sessions (
    id           SERIAL PRIMARY KEY,
    token_hash   VARCHAR(255) NOT NULL UNIQUE,
    user_id      INTEGER NOT NULL,
    expires_at   TIMESTAMP NOT NULL,
    ip_address   VARCHAR(45),
    user_agent   VARCHAR(255),
    active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at   TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
    CONSTRAINT sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users (id)
);

CREATE TABLE public.api_keys (
    id          SERIAL PRIMARY KEY,
    key_prefix  VARCHAR(12) NOT NULL,
    key_hash    VARCHAR(255) NOT NULL UNIQUE,
    name        VARCHAR(100) NOT NULL,
    user_id     INTEGER NOT NULL,
    scopes      VARCHAR(255) NOT NULL DEFAULT 'read',
    expires_at  TIMESTAMP,
    active      BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
    CONSTRAINT api_keys_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users (id)
);

CREATE TABLE public.revoked_tokens (
    id          SERIAL PRIMARY KEY,
    jti         VARCHAR(36) NOT NULL UNIQUE,
    token_type  VARCHAR(20) NOT NULL,
    user_id     INTEGER,
    expires_at  TIMESTAMP NOT NULL,
    active      BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC')
);

INSERT INTO public.roles (id, description, active) VALUES
    (1, 'Operador',      TRUE),
    (2, 'Administrador', TRUE);

SELECT setval(pg_get_serial_sequence('public.roles', 'id'), (SELECT MAX(id) FROM public.roles));

CREATE INDEX idx_users_email ON public.users (email);
CREATE INDEX idx_users_role_id ON public.users (role_id);
CREATE INDEX idx_users_google_id ON public.users (google_id) WHERE google_id IS NOT NULL;
CREATE INDEX idx_users_reset_password_token ON public.users (reset_password_token)
    WHERE reset_password_token IS NOT NULL;
CREATE INDEX idx_roles_active ON public.roles (active);
CREATE INDEX idx_sessions_user_id ON public.sessions (user_id);
CREATE INDEX idx_sessions_token_hash ON public.sessions (token_hash);
CREATE INDEX idx_api_keys_prefix ON public.api_keys (key_prefix);
CREATE INDEX idx_api_keys_user_id ON public.api_keys (user_id);
CREATE INDEX idx_revoked_tokens_jti ON public.revoked_tokens (jti);
CREATE INDEX idx_revoked_tokens_expires_at ON public.revoked_tokens (expires_at);
