
CREATE TABLE public.roles (
	id serial4 NOT NULL,
	description varchar NOT NULL,
	active bool NOT NULL,
	created_at timestamp NOT NULL DEFAULT now(),
	CONSTRAINT roles_pkey PRIMARY KEY (id)
);

CREATE TABLE public.permissions (
	id serial4 NOT NULL,
	code varchar(100) NOT NULL,
	description varchar(255) NOT NULL,
	module varchar(100) NULL,
	active bool NOT NULL DEFAULT true,
	created_at timestamp NOT NULL DEFAULT now(),
	CONSTRAINT permissions_pkey PRIMARY KEY (id),
	CONSTRAINT permissions_code_key UNIQUE (code)
);

CREATE TABLE public.role_permissions (
	role_id int4 NOT NULL,
	permission_id int4 NOT NULL,
	CONSTRAINT role_permissions_pkey PRIMARY KEY (role_id, permission_id),
	CONSTRAINT role_permissions_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE CASCADE,
	CONSTRAINT role_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES public.permissions(id) ON DELETE CASCADE
);

CREATE TABLE public.users (
	id serial4 NOT NULL,
	password varchar(255) NOT NULL,
	name varchar(50) NOT NULL,
	email varchar(50) NOT NULL,
	phone varchar(12) NOT NULL,
	cpf varchar(12) NOT NULL,
	role_id int4 NULL,
	reset_password_token varchar(64) NULL,
	reset_password_expires timestamp NULL,
	active bool NOT NULL DEFAULT true,
	blocked bool NOT NULL DEFAULT false,
	failed_login_attempts int4 NOT NULL DEFAULT 0,
	password_reset_count int4 NOT NULL DEFAULT 0,
	password_reset_window_start timestamp NULL,
	created_at timestamp NOT NULL DEFAULT now(),
	CONSTRAINT users_cpf_key UNIQUE (cpf),
	CONSTRAINT users_pkey PRIMARY KEY (id)
);

INSERT INTO public.roles (id, description, active) VALUES
	(1, 'Usuario', true),
	(2, 'Operador', true),
	(3, 'Administrador', true),
	(4, 'Usuario_cliente', true);

SELECT setval(pg_get_serial_sequence('roles', 'id'), 4);

INSERT INTO public.permissions (code, description, module) VALUES
	('users:read', 'Listar e visualizar usuários', 'users'),
	('users:create', 'Cadastrar usuários', 'users'),
	('users:update', 'Atualizar usuários', 'users'),
	('users:delete', 'Desativar usuários', 'users'),
	('users:block', 'Bloquear usuários', 'users'),
	('users:unblock', 'Desbloquear usuários', 'users'),
	('roles:read', 'Listar e visualizar papéis', 'roles'),
	('roles:create', 'Cadastrar papéis', 'roles'),
	('roles:update', 'Atualizar papéis e permissões', 'roles'),
	('roles:delete', 'Desativar papéis', 'roles'),
	('permissions:read', 'Listar permissões do sistema', 'permissions'),
	('permissions:create', 'Cadastrar permissões (telas/funções)', 'permissions');

SELECT setval(pg_get_serial_sequence('permissions', 'id'), 12);

-- Operador: leitura de usuários
INSERT INTO public.role_permissions (role_id, permission_id)
SELECT 2, id FROM public.permissions WHERE code = 'users:read';

-- Administrador: todas as permissões
INSERT INTO public.role_permissions (role_id, permission_id)
SELECT 3, id FROM public.permissions;

-- Administrador inicial (CPF 00000000000 / senha Admin@123456 — altere em produção)
INSERT INTO public.users (password, name, email, phone, cpf, role_id, active) VALUES
	(
		'$2b$12$w9rvUrtds6hBy59RvjXAOOJBpqX4XY0ZHjd7R.isgOzN8bI6ADXlm',
		'Administrador',
		'admin@example.com',
		'0000000000',
		'00000000000',
		3,
		true
	);

ALTER TABLE public.users
	ADD CONSTRAINT users_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id);

CREATE TABLE public.audit_events (
	id bigserial NOT NULL,
	created_at timestamp NOT NULL DEFAULT now(),
	active bool NOT NULL DEFAULT true,
	request_id varchar(36) NULL,
	actor_user_id int4 NULL,
	action varchar(100) NOT NULL,
	resource_type varchar(50) NULL,
	resource_id varchar(100) NULL,
	outcome varchar(20) NOT NULL,
	ip_address varchar(45) NULL,
	event_metadata jsonb NULL,
	CONSTRAINT audit_events_pkey PRIMARY KEY (id),
	CONSTRAINT audit_events_actor_user_id_fkey FOREIGN KEY (actor_user_id) REFERENCES public.users(id)
);

CREATE INDEX audit_events_created_at_idx ON public.audit_events (created_at);
CREATE INDEX audit_events_action_idx ON public.audit_events (action);
CREATE INDEX audit_events_actor_user_id_idx ON public.audit_events (actor_user_id);
CREATE INDEX audit_events_request_id_idx ON public.audit_events (request_id);
CREATE INDEX permissions_module_idx ON public.permissions (module);
CREATE INDEX role_permissions_role_id_idx ON public.role_permissions (role_id);
