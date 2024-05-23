
CREATE TABLE public.roles (
	id serial4 NOT NULL,
	description varchar NOT NULL,
	active bool NOT NULL,
	CONSTRAINT roles_pkey PRIMARY KEY (id)
);

CREATE TABLE public.users (
	id serial4 NOT NULL,
	"password" varchar(255) NOT NULL,
	"name" varchar(50) NOT NULL,
	email varchar(50) NOT NULL,
	"CPF" varchar(12) NOT NULL,
	created_at timestamp NULL,
	role_id int4 NULL,
	active bool NULL,
	CONSTRAINT "users_CPF_key" UNIQUE ("CPF"),
	CONSTRAINT users_pkey PRIMARY KEY (id)
);

CREATE TABLE public.users_update (
	id serial4 NOT NULL,
	updated_at timestamp NOT NULL,
	user_id int4 NULL,
	user_password varchar NULL,
	user_name varchar NULL,
	user_email varchar NULL,
	"user_CPF" varchar NOT NULL,
	role_changed int4 NULL,
	active_changed bool NULL,
	user_changer int4 NULL,
	CONSTRAINT users_update_pkey PRIMARY KEY (id),
	CONSTRAINT "users_update_user_CPF_key" UNIQUE ("user_CPF")
);

INSERT INTO public.roles (description,active) VALUES
	 ('User',true),
	 ('Operator',true),
	 ('Administrator',true);

ALTER TABLE public.users ADD CONSTRAINT users_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id);
ALTER TABLE public.users_update ADD CONSTRAINT users_update_role_changed_fkey FOREIGN KEY (role_changed) REFERENCES public.roles(id);
ALTER TABLE public.users_update ADD CONSTRAINT users_update_user_changer_fkey FOREIGN KEY (user_changer) REFERENCES public.users(id);
ALTER TABLE public.users_update ADD CONSTRAINT users_update_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);