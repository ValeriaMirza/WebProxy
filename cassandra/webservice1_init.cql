-- Webservice 1 Schema

CREATE KEYSPACE IF NOT EXISTS webservice1_keyspace 
WITH replication = {'class': 'SimpleStrategy', 'replication_factor' : 1};

USE webservice1_keyspace;

CREATE TABLE IF NOT EXISTS test_table (
    id UUID PRIMARY KEY,
    message TEXT
);
