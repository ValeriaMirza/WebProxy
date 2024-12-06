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
    cassandra_host = os.getenv('CASSANDRA_HOST', 'cassandra2')
    cluster = Cluster([cassandra_host])
    session = cluster.connect()
    return session

def create_message_table(session):
    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS message_board_keyspace 
        WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
    """)
    session.set_keyspace('message_board_keyspace')
    session.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id UUID PRIMARY KEY,
            user_id UUID,
            message TEXT
        );
    """)

@app.route('/')
def index():
    return render_template('message_board.html')

@app.route('/messages', methods=['POST'])
def post_message():
    session = get_cassandra_session()
    create_message_table(session)


    user_id = request.form.get('user_id')
    message = request.form.get('message')

    if not user_id or not message:
        return jsonify({"error": "User ID and message are required"}), 400

   
    message_id = uuid.uuid4()
    session.execute("""
        INSERT INTO messages (id, user_id, message) VALUES (%s, %s, %s)
    """, (message_id, uuid.UUID(user_id), message))

   
    redis_client = get_redis_client()
    message_data = {"user_id": user_id, "message": message}
    redis_client.set(f"message:{message_id}", json.dumps(message_data))  # Serialize to JSON

    return jsonify({"message": "Message posted", "message_id": str(message_id)}), 201

@app.route('/messages', methods=['GET'])
def get_messages():
    session = get_cassandra_session()
    create_message_table(session)

   
    rows = session.execute("SELECT * FROM messages")
    messages = [{"id": str(row.id), "user_id": str(row.user_id), "message": row.message} for row in rows]
    return jsonify(messages)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
