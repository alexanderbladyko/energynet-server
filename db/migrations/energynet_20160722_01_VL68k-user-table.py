"""
user table
"""

from yoyo import step

__depends__ = {}

step("""
    CREATE SEQUENCE public.accounts_id_seq
        INCREMENT 1
        MINVALUE 1
        MAXVALUE 9223372036854775807
        START 1
        CACHE 1;
""", """
    DROP SEQUENCE public.accounts_id_seq;
""")

step("""
    CREATE TABLE public."accounts"
    (
        id integer NOT NULL DEFAULT nextval('accounts_id_seq'::regclass),
        name character varying(30) NOT NULL,
        password character varying(64) NOT NULL,
        salt character varying(16) NOT NULL,
        created time with time zone NOT NULL DEFAULT now(),
        updated time with time zone NOT NULL DEFAULT now(),
        CONSTRAINT accounts_pkey PRIMARY KEY (id),
        CONSTRAINT accounts_id_key UNIQUE (id)
    )
    WITH (
        OIDS=FALSE
    );
""", """
    DROP TABLE public."accounts";
""")

step("""
    CREATE INDEX accounts_id_idx
        ON public."accounts"
        USING btree
        (id);
""", """
    DROP INDEX public.accounts_id_idx;
""")


step("""
    CREATE UNIQUE INDEX accounts_name_idx
    ON public."accounts"
    USING btree
    (name COLLATE pg_catalog."default");
""", """
    DROP INDEX public.accounts_name_idx;
""")
