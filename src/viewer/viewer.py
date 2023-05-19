import solara, json
from arango import ArangoClient

DATABASE_NAME = 'mochila'

def get_db_connection(host='127.0.0.1', port=8529, user='root', password=''):
    client = ArangoClient(hosts=[f"http://{host}:{port}"])

    # Ensure the mochila db exists (will fail if user doesn't have CREATE DB permissions)
    sys_db = client.db('_system', username=user, password=password)
    if not sys_db.has_database(DATABASE_NAME):
        sys_db.create_database(DATABASE_NAME)

    return client.db(DATABASE_NAME, username=user, password=password)

arango_db = get_db_connection()

# Declare reactive variables at the top level. Components using these variables
# will be re-executed when their values change.
db_name = ''
collections = None
sample_collection = solara.reactive('')
samples = None

def set_sample_collection(value):
    global sample_collection
    sample_collection.value = value

@solara.component
def Page():
    coll_names = [col['name'] for col in arango_db.collections() if col['name'][0] != '_']
    coll_info = [
            {'name': col, 'count': arango_db.collection(col).count()}
            for col
            in coll_names
        ]

    if sample_collection.value:
        data_samples = [e for e in arango_db.collection(sample_collection.value).all(limit=10).batch()]
    else:
        data_samples = []

    db_name = f"Using database: {arango_db.db_name}"
    collections = json.dumps(coll_info, indent=2)
    samples = json.dumps(data_samples, indent=2)


    solara.HTML('h1', db_name)
    solara.HTML('h2', "Event catalog")
    solara.HTML('pre', collections)
    solara.HTML('h2', "Data sample")
    solara.Select('Event source', coll_names, on_value=set_sample_collection)
    solara.HTML('pre', samples, style="border: solid 1px black; height: 400px; overflow: auto;")

Page()
