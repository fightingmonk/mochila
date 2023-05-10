#!/usr/bin/env python3
import argparse, json, requests, sys
from utils import env_or_required_arg, get_db_connection

COLLECTION_NAME = 'events_vercel'
TOKEN_ENV_NAME = 'VERCEL_TOKEN'

def fetch_events(access_token, until=None):
    endpoint = f'https://api.vercel.com/v6/deployments?limit=100'
    if until:
        endpoint += f'&until={until}'
    headers = {'Authorization' : f'Bearer {access_token}'}
    resp = requests.get(endpoint, headers=headers)
    if (resp.status_code == 200):
        return resp.json()
    else:
        resp.raise_for_status()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Import deployment events from a Vercel account')
    parser.add_argument('-t', '--token', dest='token', nargs='?', help=f'Vercel API token, or set {TOKEN_ENV_NAME} in env - get a token from https://vercel.com/account/tokens', **env_or_required_arg(TOKEN_ENV_NAME))
    parser.add_argument('-q', '--quiet', dest='quiet', action='store_true', help='suppress console output')
    args = parser.parse_args()

    try:
        # TODO optionally read database credentials from argparse
        arango_db = get_db_connection(COLLECTION_NAME)
        collection = arango_db.collection(COLLECTION_NAME)

        nextPage = None
        import_count = 0
        ignore_count = 0
        errors = []
        while True:
            vercel_resp = fetch_events(args.token, until=nextPage)
            if vercel_resp and len(vercel_resp['deployments']) > 0:
                events = vercel_resp['deployments']
                # Create the arango key on each event
                for e in events:
                    e['_key'] = e['uid']
                
                res = collection.import_bulk(events, halt_on_error=False, details=True, on_duplicate='ignore')
                # res = {'error': False, 'created': 100, 'errors': 0, 'empty': 0, 'updated': 0, 'ignored': 0, 'details': []}
                import_count += res['created']
                ignore_count += res['ignored']
                if res['errors'] > 0:
                    errors += res['details']

                pagination = vercel_resp['pagination']
                if pagination and 'next' in pagination and pagination['next']:
                    nextPage = pagination['next']
                else:
                    break
            else:
                break

        if (not args.quiet):
            print(f'Fetched and stored {import_count} new events and ignored {ignore_count} previously imported events from Vercel')
            if len(errors) > 0:
                print('Error(s) occurred during import:')
                print(errors)
        
    except Exception as ex:
        print(f'Processing Vercel events failed', file=sys.stderr)
        print(ex, file=sys.stderr)
        sys.exit(1)
