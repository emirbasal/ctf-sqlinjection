sudo docker run -it --rm --name sql-injection -v "$PWD":/usr/src/sql-injection -w /usr/src/sql-injection -p 6667:6667 python:2 python server.py 
