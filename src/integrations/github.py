#!/usr/bin/env python3
import argparse, requests, sys

from utils import env_or_required_arg, get_db_connection

COLLECTION_NAME = 'events_github'
TOKEN_ENV_NAME = 'GITHUB_TOKEN'

def fetch_events(org, repo, access_token, page=1):
    endpoint = f'https://api.github.com/repos/{org}/{repo}/events?per_page=100&page={page}'
    headers = {'Authorization' : f'Bearer {access_token}'}
    resp = requests.get(endpoint, headers=headers)
    if (resp.status_code == 200):
        return resp.json()
    else:
        resp.raise_for_status()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Import events from a GitHub repository')
    parser.add_argument('organization', type=str, nargs='?', help='the organization that owns the repository')
    parser.add_argument('repository', type=str, nargs='?', help='the repository to import events from')
    parser.add_argument('-t', '--token', dest='token', nargs='?', help='GitHub API token', **env_or_required_arg(TOKEN_ENV_NAME))
    parser.add_argument('-q', '--quiet', dest='quiet', action='store_true', help='suppress console output')
    args = parser.parse_args()

    try:
        # TODO optionally read database credentials from argparse
        arango_db = get_db_connection(COLLECTION_NAME)
        collection = arango_db.collection(COLLECTION_NAME)

        page = 1
        import_count = 0
        ignore_count = 0
        errors = []
        while page > 0:
            events = fetch_events(args.organization, args.repository, args.token, page=page)
            if len(events) > 0:
                # Create the arango key on each event
                for e in events:
                    e['_key'] = e['id']
                
                res = collection.import_bulk(events, halt_on_error=False, details=True, on_duplicate='ignore')
                # res = {'error': False, 'created': 100, 'errors': 0, 'empty': 0, 'updated': 0, 'ignored': 0, 'details': []}
                import_count += res['created']
                ignore_count += res['ignored']
                if res['errors'] > 0:
                    errors += res['details']

                page += 1
            else:
                page = 0
        if (not args.quiet):
            print(f'Fetched and stored {import_count} new events and ignored {ignore_count} previously imported events from {args.organization}/{args.repository}')
            if len(errors) > 0:
                print('Error(s) occurred during import:')
                print(errors)
        
    except Exception as ex:
        print(f'Processing GitHub events failed from {args.organization}/{args.repository}', file=sys.stderr)
        print(ex, file=sys.stderr)
        sys.exit(1)
