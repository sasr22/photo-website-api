import os
import psycopg

def init_db():
    db = psycopg.connect(os.environ["DB_URI"])

    db.cursor().execute("""
    CREATE TABLE IF NOT EXISTS register_tokens(
        uuid CHAR(36) UNIQUE,
        email CHAR(512) UNIQUE,
        ip CHAR(15) UNIQUE,
        created_at NUMERIC DEFAULT EXTRACT(EPOCH FROM NOW()),
        PRIMARY KEY(uuid, email, ip)
    );
    """)
    db.cursor().execute("""
    CREATE TABLE IF NOT EXISTS api_tokens(
        uuid CHAR(36) UNIQUE,
        email CHAR(512) UNIQUE,
        ip CHAR(15) UNIQUE,
        created_at NUMERIC DEFAULT EXTRACT(EPOCH FROM NOW()),
        PRIMARY KEY(uuid, email, ip)
    );
    """)
    db.cursor().execute("""
    CREATE TABLE IF NOT EXISTS view_tokens(
        uuid CHAR(36) UNIQUE,
        api_uuid CHAR(36) UNIQUE,
        created_at NUMERIC DEFAULT EXTRACT(EPOCH FROM NOW()),
        FOREIGN KEY(api_uuid) REFERENCES api_tokens(uuid),
        PRIMARY KEY (uuid)
    );
    """)
    db.cursor().execute("""
    CREATE TABLE IF NOT EXISTS delete_tokens(
        uuid CHAR(36) UNIQUE,
        api_uuid CHAR(36) UNIQUE,
        created_at NUMERIC DEFAULT EXTRACT(EPOCH FROM NOW()),
        FOREIGN KEY(api_uuid) REFERENCES api_tokens(uuid),
        PRIMARY KEY (uuid)
    );
    """)
    db.cursor().execute("""
    CREATE TABLE IF NOT EXISTS images(
        uuid CHAR(36) UNIQUE,
        api_uuid CHAR(36) UNIQUE,
        full_path CHAR(256) UNIQUE,
        mimetype CHAR(256),
        created_at NUMERIC DEFAULT EXTRACT(EPOCH FROM NOW()),
        FOREIGN KEY(api_uuid) REFERENCES api_tokens(uuid),
        PRIMARY KEY (uuid, mimetype)
    );
    """)
    db.commit()

    db.close()