docker stop multi-mysql
docker rm multi-mysql
rem docker network create app-network
docker run --network app-network --network-alias mysql --name multi-mysql -v "./db/mysql":/var/lib/mysql -e MYSQL_ROOT_PASSWORD='R00tP@SSw0rD' -e MYSQL_DATABASE='db_multidomain' -p 3306:3306  -d mysql:5.7 
