rem docker-compose build
rem docker-compose up
docker stop md_one_server
docker rm md_one_server
docker build -t md_one .
docker run -d -p 5000:5000 --network app-network --restart always --name md_one_server -e DB_HOST=172.19.0.3 -e DB_PORT=3306 -e DB_DATABASE=db_multidomain -e DB_USERNAME=root -e DB_PASSWORD=R00tP@SSw0rD --link multi-mysql:db md_one 
