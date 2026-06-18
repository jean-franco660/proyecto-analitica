# Lab 2 Source Database

This service runs the local MySQL `classicmodels` source database for lab 2.

It provides the operational source data used by the batch and streaming
pipelines.

## What This Contains

The dump file is:

```text
classicmodels_lab2.sql
```

It contains the `classicmodels` schema and seed data:

```text
classicmodels
```

The dump includes the standard Classic Models tables plus the lab 2 `ratings` table.

Expected tables:

```text
customers
employees
offices
orderdetails
orders
payments
productlines
products
ratings
```

## Start MySQL

From this folder:

```bash
docker-compose up -d --build
```

Or, with the newer Docker Compose plugin:

```bash
docker compose up -d --build
```

The container name is:

```text
classicmodels-lab2-mysql
```

The local host port is `3307` so it can run at the same time as lab 1, which uses `3306`.

Connection values:

```text
Host: 127.0.0.1
Port: 3307
Database: classicmodels
User: admin
Password: adminpwrd
```

## Connect

```bash
docker exec -it classicmodels-lab2-mysql mysql -uadmin -padminpwrd classicmodels
```

Or from your host machine:

```bash
mysql --host=127.0.0.1 --port=3307 --user=admin --password=adminpwrd classicmodels
```

Check the tables:

```sql
SHOW TABLES;
SELECT COUNT(*) FROM ratings;
SELECT * FROM ratings LIMIT 20;
```

## Reset and Reload

Docker only runs files in `/docker-entrypoint-initdb.d/` the first time the MySQL volume is created.

If you change `classicmodels_lab2.sql` and want to reload from scratch:

```bash
docker-compose down -v
docker-compose up -d --build
```

## Re-export From AWS RDS

If the AWS RDS database changes, regenerate the dump with a MySQL 8 Docker client.

Using Docker avoids version mismatch problems with newer local `mysqldump` clients.

```bash
docker run --rm \
  -v "$PWD:/dump" \
  mysql:8.4 \
  sh -c "MYSQL_PWD='<password>' mysqldump \
    --host=<rds-endpoint> \
    --user=<user> \
    --port=3306 \
    --single-transaction \
    --routines \
    --triggers \
    --events \
    --set-gtid-purged=OFF \
    --column-statistics=0 \
    --no-tablespaces \
    --databases classicmodels \
    > /dump/classicmodels_lab2.sql"
```

After regenerating the dump, reset the local Docker volume to reload it.
