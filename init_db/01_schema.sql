-- Schema alinhado aos models ORM (Users, Roles + modelsGeneric)

CREATE TABLE public.roles (
    id          SERIAL PRIMARY KEY,
    description VARCHAR NOT NULL,
    active      BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC')
);

CREATE TABLE public.users (
    id                     SERIAL PRIMARY KEY,
    password               VARCHAR(255) NOT NULL,
    name                   VARCHAR(50) NOT NULL,
    email                  VARCHAR(50) NOT NULL,
    phone                  VARCHAR(12) NOT NULL,
    cpf                    VARCHAR(12) NOT NULL,
    role_id                INTEGER REFERENCES public.roles(id),
    reset_password_token   VARCHAR(255),
    reset_password_expires TIMESTAMP,
    active                 BOOLEAN NOT NULL DEFAULT TRUE,
    created_at             TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
    CONSTRAINT users_cpf_key UNIQUE (cpf)
);

CREATE INDEX idx_users_email ON public.users (email);
CREATE INDEX idx_users_role_id ON public.users (role_id);
CREATE INDEX idx_users_reset_password_token ON public.users (reset_password_token)
    WHERE reset_password_token IS NOT NULL;
CREATE INDEX idx_roles_active ON public.roles (active);
