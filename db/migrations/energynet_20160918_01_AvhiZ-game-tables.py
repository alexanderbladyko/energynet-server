"""
game tables
"""

from yoyo import step

__depends__ = {'energynet_20160722_01_VL68k-user-table'}


step("""
    CREATE TABLE public.fields
    (
        name text NOT NULL,
        data jsonb,
        geometry polygon,
        CONSTRAINT fields_pkey PRIMARY KEY (name)
    );
""", """
    DROP TABLE public.fields
""")


step("""
    CREATE TABLE public.areas
    (
        name text NOT NULL,
        color character(7),
        geometry polygon,
        field_name text,
        CONSTRAINT areas_name_pkey PRIMARY KEY (name),
        CONSTRAINT areas_field_name FOREIGN KEY (field_name)
            REFERENCES public.fields (name) MATCH SIMPLE
            ON UPDATE NO ACTION ON DELETE NO ACTION
    );
""", """
    DROP TABLE public.areas;
""")


step("""
    CREATE INDEX fki_areas_field_name
        ON public.areas
        USING btree
        (field_name COLLATE pg_catalog."default");
""", """
    DROP INDEX public.fki_areas_field_name;
""")


step("""
    CREATE TABLE public.cities
    (
        name text NOT NULL,
        area_name text,
        center point,
        slots integer[],
        CONSTRAINT cities_name_pkey PRIMARY KEY (name),
        CONSTRAINT cities_area_name FOREIGN KEY (area_name)
            REFERENCES public.areas (name) MATCH SIMPLE
            ON UPDATE NO ACTION ON DELETE NO ACTION
    )
""", """
    DROP TABLE public.cities;
""")


step("""
    CREATE INDEX fki_cities_area_name
        ON public.cities
        USING btree
        (area_name COLLATE pg_catalog."default");
""", """
    DROP INDEX public.fki_cities_area_name;
""")


step("""
    CREATE TABLE public."junсtions"
    (
        city_1 text NOT NULL,
        city_2 text NOT NULL,
        cost integer,
        center point,
        geometry line,
        CONSTRAINT cities_names_pkey PRIMARY KEY (city_1, city_2)
    )
""", """
    DROP TABLE public."junсtions";
""")


step("""
    CREATE SEQUENCE public.stations_id_seq
        INCREMENT 1
        MINVALUE 1
        MAXVALUE 9223372036854775807
        START 1
        CACHE 1;
""", """
    DROP SEQUENCE public.stations_id_seq;
""")


step("""
    CREATE TABLE public.stations
    (
        id integer NOT NULL DEFAULT nextval('stations_id_seq'::regclass),
        cost integer,
        capacity integer,
        resources text[]
    )
""", """
    DROP TABLE public.stations;
""")
