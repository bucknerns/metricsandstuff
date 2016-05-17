===============
metricsandstuff
===============

Setting up a Dev Environment
============================

This is assuming that you are creating a general1-8 server on RAX Public Cloud
running Ubuntu 14.04 (Trusty Tahr).

MySQL
-----

1. Update the package list:
::
    > apt-get update

2. Install the following packages:
::
    > apt-get install mysql-server libmysqlclient-dev python-dev python-pip git

3. During the mysql-server install it will ask you to enter a password for the
root user, for this example we'll use ``abc123``

4. Log in to mysql and create a database named ``subunit``
::
    > mysql -u root -p
    Enter password:
    mysql> create database subunit;
    Query OK, 1 row affected (0.00 sec)

5. Git clone subunit2sql
::
    > git clone https://github.com/openstack-infra/subunit2sql

6. Git clone metricsandstuff
::
    > git clone https://github.com/bucknerns/metricsandstuff

7. Install mysql-python
::
    > pip install mysql-python

8. Install subunit2sql
::
    > pip install subunit2sql/

9. Install metricsandstuff
::
    > pip install metricsandstuff/

10. Update the database schema via subunit2sql-db-manage
::
    > subunit2sql-db-manage --database-connection mysql://root:abc123@127.0.0.1/subunit upgrade head

11. Insert subunit data into the database (in this example we're using a
subunit output of tempest)
::
    > subunit-1to2 tempest.subunit | subunit2sql --database-connection mysql://root:abc123@127.0.0.1/subunit

12. Install gunicorn
::
    > pip install gunicorn

13. Run metricsandstuff
::
    > gunicorn -b 0.0.0.0:80 myapp.run:app

PostgreSQL
----------

1. Update the package list:
::
    > apt-get update

2. Install the following packages:
::
    > apt-get install postgresql postgresql-contrib libpq-dev python-dev python-pip git

3. Switch to the postgres user, connect to PostgreSQL, create a ``root`` user
with password ``abc123``, create a ``subunit`` database, and grant the user all
privileges on the database
::
    > sudo su - postgres
    > psql
    postgres=# create user root password 'abc123';
    CREATE ROLE
    postgres=# create database subunit;
    CREATE DATABASE
    postgres=# grant all privileges on database subunit to root;
    GRANT
    postgres=# \q
    > logout

4. Git clone subunit2sql
::
    > git clone https://github.com/openstack-infra/subunit2sql

5. Git clone metricsandstuff
::
    > git clone https://github.com/bucknerns/metricsandstuff

6. Install psycopg2
::
    > pip install psycopg2

7. Change the connection string in metricsandstuff
::
    > vim metricsandstuff
    :%s/mysql/postgresql+psycopg2/g
    :wq

8. Install subunit2sql
::
    > pip install subunit2sql/

9. Install metricsandstuff
::
    > pip install metricsandstuff/

10. Update the database schema via subunit2sql-db-manage
::
    > subunit2sql-db-manage --database-connection postgresql+psycopg2://root:abc123@127.0.0.1/subunit upgrade head

11. Insert subunit data into the database (in this example we're using a
subunit output of tempest)
::
    > subunit-1to2 tempest.subunit | subunit2sql --database-connection postgresql+psycopg2://root:abc123@127.0.0.1/subunit

12. Install gunicorn
::
    > pip install gunicorn

13. Run metricsandstuff
::
    > gunicorn -b 0.0.0.0:80 myapp.run:app
