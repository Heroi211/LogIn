
CREATE TABLE public.roles (
	id serial4 NOT NULL,
	description varchar NOT NULL,
	active bool NOT NULL,
	created_at timestamp NOT NULL DEFAULT now(),
	CONSTRAINT roles_pkey PRIMARY KEY (id)
);

CREATE TABLE public.users (
	id serial4 NOT NULL,
	password varchar(255) NOT NULL,
	name varchar(50) NOT NULL,
	email varchar(50) NOT NULL,
	phone varchar(12) NOT NULL,
	cpf varchar(12) NOT NULL,
	role_id int4 NULL,
	reset_password_token varchar(255) NULL,
	reset_password_expires timestamp NULL,
	active bool NOT NULL DEFAULT true,
	created_at timestamp NOT NULL DEFAULT now(),
	CONSTRAINT users_cpf_key UNIQUE (cpf),
	CONSTRAINT users_pkey PRIMARY KEY (id)
);

INSERT INTO public.roles (description, active) VALUES
	('User', true),
	('Operator', true),
	('Administrator', true);

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
