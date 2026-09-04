#!/bin/bash
# DB_HOST=$(dotenv get DB_HOST)
# DB_PORT=$(dotenv get DB_PORT)
# DB_DATABASE=$(dotenv get DB_DATABASE)
# DB_USERNAME=$(dotenv get DB_USERNAME)
# DB_PASSWORD=$(dotenv get DB_PASSWORD)
SCRIPT_PATH=$1
FILE=${SCRIPT_PATH}"/migration.txt"
pwd
echo 'READ FILE : '${FILE}
while  IFS= read -r line; do
SCRIPT=${SCRIPT_PATH}/${line}
echo 'SCRIPT : ' ${SCRIPT}
# mysql -h ${DB_HOST} --protocol=TCP -P ${DB_PORT} -u ${DB_USERNAME} -p${DB_PASSWORD} ${DB_DATABASE}  < ${SCRIPT}
mysql -h ${DB_HOST} -P ${DB_PORT} -u ${DB_USERNAME} -p${DB_PASSWORD} ${DB_DATABASE}  < ${SCRIPT}
done < ${FILE}
