web: gunicorn -w 4 -b 0.0.0.0:5000 webservice1.app:app
web2: gunicorn -w 4 -b 0.0.0.0:5001 webservice2.app:app
nginx: nginx -c /app/nginx/nginx.conf
cassandra1: cassandra -R
cassandra2: cassandra -R
redis: redis-server --bind 0.0.0.0
