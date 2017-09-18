IF NOT EXISTS (
    SELECT
    FROM   pg_catalog.pg_user
    WHERE  pg_catalog.usename = 'postgres') THEN

        CREATE ROLE 'postgres' LOGIN PASSWORD 'postgres';
    END IF;
END;

IF NOT EXISTS (SELECT 1 FROM pg_database WHERE pg_database.datname = 'energynet_dev') THEN
    CREATE DATABASE energynet_dev;
END;
IF NOT EXISTS (
    SELECT
    FROM   pg_catalog.pg_user
    WHERE  pg_catalog.usename = 'postgres') THEN

        CREATE ROLE 'postgres' LOGIN PASSWORD 'postgres';
    END IF;
END;

IF NOT EXISTS (SELECT 1 FROM pg_database WHERE pg_database.datname = 'energynet_tests') THEN
    CREATE DATABASE energynet_tests;
END;
