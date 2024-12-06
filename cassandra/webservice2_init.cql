-- Webservice 2 Schema

CREATE KEYSPACE IF NOT EXISTS webservice2_keyspace 
WITH replication = {'class': 'SimpleStrategy', 'replication_factor' : 1};

USE webservice2_keyspace;

CREATE TABLE IF NOT EXISTS test_table (
    id UUID PRIMARY KEY,
    message TEXT
);
