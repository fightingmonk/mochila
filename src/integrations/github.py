#!/usr/bin/env python3
import argparse, requests, sys

from utils import env_or_required_arg, get_db_connection

COLLECTION_NAME = 'events_github'
TOKEN_ENV_NAME = 'GITHUB_TOKEN'

def headers(access_token):
    return {
        'Authorization' : f'Bearer {access_token}',
        'Content-Type': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }

def fetch_events(org, repo, access_token, page=1):
    endpoint = f'https://api.github.com/repos/{org}/{repo}/events?per_page=100&page={page}'
    resp = requests.get(endpoint, headers=headers(access_token))
    if (resp.status_code == 200):
        return resp.json()
    else:
        resp.raise_for_status()

def fetch_commits(org, repo, access_token, page=1):
    endpoint = f'https://api.github.com/repos/{org}/{repo}/commits?per_page=100&page={page}'
    resp = requests.get(endpoint, headers=headers(access_token))
    if (resp.status_code == 200):
        return resp.json()
    else:
        resp.raise_for_status()

def fetch_pulls(org, repo, access_token, page=1):
    endpoint = f'https://api.github.com/repos/{org}/{repo}/pulls?per_page=100&page={page}'
    resp = requests.get(endpoint, headers=headers(access_token))
    if (resp.status_code == 200):
        return resp.json()
    else:
        resp.raise_for_status()

def key_from_url(url):
    return url.split('/repos/')[1].replace('/', '_')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Import events from a GitHub repository')
    parser.add_argument('organization', type=str, nargs='?', help='the organization that owns the repository')
    parser.add_argument('repository', type=str, nargs='?', help='the repository to import events from')
    parser.add_argument('-t', '--token', dest='token', nargs='?', help=f'GitHub API token, or set {TOKEN_ENV_NAME} in env - get a token from https://github.com/settings/tokens', **env_or_required_arg(TOKEN_ENV_NAME))
    parser.add_argument('-q', '--quiet', dest='quiet', action='store_true', help='suppress console output')
    args = parser.parse_args()

    try:
        # TODO optionally read database credentials from argparse
        arango_db = get_db_connection(COLLECTION_NAME)
        collection = arango_db.collection(COLLECTION_NAME)

        page = 1
        import_count = 0
        update_count = 0
        ignore_count = 0
        errors = []
        refs = {}

        while page > 0:
            events = fetch_events(args.organization, args.repository, args.token, page=page)
            if len(events) > 0:
                # Create the arango key on each event
                for e in events:
                    e['_key'] = e['id']
                    try:
                        ref = e['payload']['ref']
                        if ref:
                            if ref in refs: refs[ref] += 1
                            else: refs[ref] = 1
                    except: pass

                res = collection.import_bulk(events, halt_on_error=False, details=True, on_duplicate='ignore')
                # res = {'error': False, 'created': 100, 'errors': 0, 'empty': 0, 'updated': 0, 'ignored': 0, 'details': []}
                import_count += res['created']
                update_count += res['updated']
                ignore_count += res['ignored']
                if res['errors'] > 0:
                    errors += res['details']

                page += 1
            else:
                page = 0

        page = 1
        while page > 0:
            events = fetch_commits(args.organization, args.repository, args.token, page=page)
            if len(events) > 0:
                # Create the arango key on each event
                for e in events:
                    e['_key'] = key_from_url(e['url'])
                    e['type'] = 'Commit'

                res = collection.import_bulk(events, halt_on_error=False, details=True, on_duplicate='ignore')
                # res = {'error': False, 'created': 100, 'errors': 0, 'empty': 0, 'updated': 0, 'ignored': 0, 'details': []}
                import_count += res['created']
                update_count += res['updated']
                ignore_count += res['ignored']
                if res['errors'] > 0:
                    errors += res['details']

                page += 1
            else:
                page = 0

        page = 1
        while page > 0:
            events = fetch_pulls(args.organization, args.repository, args.token, page=page)
            if len(events) > 0:
                # Create the arango key on each event
                for e in events:
                    e['_key'] = key_from_url(e['url'])
                    e['type'] = 'MergeRequest'

                res = collection.import_bulk(events, halt_on_error=False, details=True, on_duplicate='replace')
                # res = {'error': False, 'created': 100, 'errors': 0, 'empty': 0, 'updated': 0, 'ignored': 0, 'details': []}
                import_count += res['created']
                update_count += res['updated']
                ignore_count += res['ignored']
                if res['errors'] > 0:
                    errors += res['details']

                page += 1
            else:
                page = 0

        if (not args.quiet):
            print(f'Fetched and stored {import_count} new events, updated {update_count} events, and ignored {ignore_count} previously imported events from {args.organization}/{args.repository}')
            if len(errors) > 0:
                print('Error(s) occurred during import:')
                print(errors)

        print(refs)

    except Exception as ex:
        print(f'Processing GitHub events failed from {args.organization}/{args.repository}', file=sys.stderr)
        print(ex, file=sys.stderr)
        sys.exit(1)
