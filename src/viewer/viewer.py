import solara, json
from utils import get_db_connection

arango_db = get_db_connection()

# Declare reactive variables at the top level. Components using these variables
# will be re-executed when their values change.
db_name = ''
collections = None


@solara.component
def Page():
    db_name = arango_db.db_name
    collections = json.dumps([col for col in arango_db.collections() if col['name'][0] != '_'], indent=2)

    solara.Text(db_name)
    solara.HTML('pre', collections)


# The following line is required only when running the code in a Jupyter notebook:
Page()
