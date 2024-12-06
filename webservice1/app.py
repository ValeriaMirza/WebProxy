import redis
from flask import Flask, render_template, request, jsonify
from cassandra.cluster import Cluster
import uuid
import os
import json

app = Flask(__name__)


def get_redis_client():
    redis_host = os.getenv('REDIS_HOST', 'redis')
    client = redis.StrictRedis(host=redis_host, port=6379, db=0, decode_responses=True)
    return client


def get_cassandra_session():
    cassandra_host = os.getenv('CASSANDRA_HOST', 'cassandra1')
    cluster = Cluster([cassandra_host])
    session = cluster.connect()
    return session


def create_user_table(session):
    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS user_management_keyspace 
        WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
    """)
    session.set_keyspace('user_management_keyspace')
    session.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY,
            name TEXT,
            email TEXT
        );
    """)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/users', methods=['POST'])
def create_user():
    session = get_cassandra_session()
    create_user_table(session)

    name = request.form.get('name')
    email = request.form.get('email')

    if not name or not email:
        return jsonify({"error": "Name and email are required"}), 400

    user_id = uuid.uuid4()
    session.execute("""
        INSERT INTO users (id, name, email) VALUES (%s, %s, %s)
    """, (user_id, name, email))

    redis_client = get_redis_client()
    user_data = {"name": name, "email": email}
    redis_client.set(f"user:{user_id}", json.dumps(user_data))

    return jsonify({"message": "User created", "user_id": str(user_id)}), 201

@app.route('/users', methods=['GET'])
def get_users():
    session = get_cassandra_session()
    create_user_table(session)

    rows = session.execute("SELECT * FROM users")
    users = [{"id": str(row.id), "name": row.name, "email": row.email} for row in rows]
    return jsonify(users)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
