from os import environ
from arango import ArangoClient

DATABASE_NAME = 'mochila'

def env_or_required_arg(key):
    val = environ.get(key)
    if val:
        return {'default': val}
    else:
        return {'required': True}

def get_db_connection(collection=None, host='127.0.0.1', port=8529, user='root', password=''):
    client = ArangoClient()
    # Ensure the mochila db exists (will fail if user doesn't have CREATE DB permissions)
    sys_db = client.db('_system', username=user, password=password)
    if not sys_db.has_database(DATABASE_NAME):
        sys_db.create_database(DATABASE_NAME)

    db = client.db(DATABASE_NAME, username=user, password=password)
    if collection and not db.has_collection(collection):
        db.create_collection(collection)

    return db
