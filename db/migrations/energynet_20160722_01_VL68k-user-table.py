"""
user table
"""

from yoyo import step

__depends__ = {}

step("""
    CREATE SEQUENCE public.user_id_seq
        INCREMENT 1
        MINVALUE 1
        MAXVALUE 9223372036854775807
        START 1
        CACHE 1;
""", """
    DROP SEQUENCE public.user_id_seq;
""")

step("""
    CREATE TABLE public."user"
    (
        id integer NOT NULL DEFAULT nextval('user_id_seq'::regclass),
        name character varying(30) NOT NULL,
        password character varying(64) NOT NULL,
        salt character varying(16) NOT NULL,
        created time with time zone NOT NULL DEFAULT now(),
        updated time with time zone NOT NULL DEFAULT now(),
        CONSTRAINT user_pkey PRIMARY KEY (id),
        CONSTRAINT user_id_key UNIQUE (id)
    )
    WITH (
        OIDS=FALSE
    );
""", """
    DROP TABLE public."user";
""")

step("""
    CREATE INDEX user_id_idx
        ON public."user"
        USING btree
        (id);
""", """
    DROP INDEX public.user_id_idx;
""")


step("""
    CREATE UNIQUE INDEX user_name_idx
    ON public."user"
    USING btree
    (name COLLATE pg_catalog."default");
""", """
    DROP INDEX public.user_name_idx;
""")
