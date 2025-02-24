#!/bin/bash

if [ -z "$(ls -A /var/lib/postgresql/data)" ]; then
	
	initdb --pwfile=/run/secrets/db_adm_psw -A md5 /var/lib/postgresql/data
   
	pg_ctl -D /var/lib/postgresql/data start

    PGPASSWORD="$(cat /run/secrets/db_adm_psw)" psql -c "CREATE USER $(cat /run/secrets/db_user) WITH PASSWORD '$(cat /run/secrets/db_user_psw)' CREATEDB;"
    PGPASSWORD="$(cat /run/secrets/db_user_psw)" psql -U "$(cat /run/secrets/db_user)" -d postgres -c "CREATE DATABASE $(cat /run/secrets/db_name);"

	pg_ctl -D /var/lib/postgresql/data stop

	echo "host all all all md5" >> /var/lib/postgresql/data/pg_hba.conf
fi

postgres -D /var/lib/postgresql/data


# sql command crimes :()
# PGPASSWORD="$(cat /run/secrets/db_adm_psw)" psql -c "CREATE USER $(cat /run/secrets/db_user) WITH PASSWORD '$(cat /run/secrets/db_user_psw)';" 
# PGPASSWORD="$(cat /run/secrets/db_adm_psw)" psql -c "GRANT ALL PRIVILEGES ON DATABASE $(cat /run/secrets/db_name) TO $(cat /run/secrets/db_user);"
# PGPASSWORD="$(cat /run/secrets/db_adm_psw)" psql -c "CREATE DATABASE $(cat /run/secrets/db_name);" 
# PGPASSWORD="$(cat /run/secrets/db_adm_psw)" psql -d "$(cat /run/secrets/db_name)" -c "ALTER USER $(cat /run/secrets/db_user) CREATEDB;" 
# PGPASSWORD="$(cat /run/secrets/db_adm_psw)" psql -d "$(cat /run/secrets/db_name)" -c "GRANT ALL ON SCHEMA public TO $(cat /run/secrets/db_user);"
# PGPASSWORD="$(cat /run/secrets/db_adm_psw)" psql -c "ALTER USER postgres WITH PASSWORD '$(cat /run/secrets/db_adm_psw)';"