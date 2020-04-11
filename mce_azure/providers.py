import logging
import json
import argparse

import requests
from decouple import config

from .utils import get_access_token

logger = logging.getLogger(__name__)

DEFAULT_SUBSCRIPTION = config('MCE_AZURE_SUBSCRIPTION', default=None)
DEFAULT_TENANT = config('MCE_AZURE_TENANT', default=None)
DEFAULT_USER = config('MCE_AZURE_USER', default=None)
DEFAULT_PASSWORD = config('MCE_AZURE_PASSWORD', default=None)

def download_providers(access_token, subscription_id=None, is_china=False, api_version="2019-10-01"):
    """Get list of services providers

    @see: https://docs.microsoft.com/en-us/rest/api/resources/providers/list
    """

    base_url = "https://management.azure.com"
    if is_china:
        base_url = "https://management.chinacloudapi.cn/"

    providers_url = f"{base_url}/subscriptions/{subscription_id}/providers?api-version={api_version}"

    session = requests.Session()
    session.headers['authorization'] = 'Bearer %s' % access_token

    resp = session.get(providers_url)
    resp.raise_for_status()

    return resp.json()

def transform_providers(providers):

    result = {}
    for provider in providers['value']:
        namespace = provider['namespace']
        resourceTypes = provider.get('resourceTypes')
        if resourceTypes:
            for r in resourceTypes:
                if r.get('apiVersions'):
                    r_type = "%s/%s" % (namespace, r['resourceType'])
                    result[r_type] = r['apiVersions'][0]

    return result

def options():

    parser = argparse.ArgumentParser()

    parser.add_argument('--subscription', '-b', 
                    dest='subscription_id',
                    help='Subscription_id ID. Default: %(default)s',
                    default=DEFAULT_SUBSCRIPTION,
                    required=True)

    parser.add_argument('--tenant', '-t', 
                    dest='tenant',
                    help='Tenant ID. Default: %(default)s',
                    default=DEFAULT_TENANT,
                    required=True)

    parser.add_argument('--user', '-u', 
                    dest='user',
                    help='Client ID or Username.',
                    default=DEFAULT_USER,
                    required=True)

    parser.add_argument('--password', '-p', 
                    dest='password',
                    help='Secret ID or Password.',
                    required=True)

    parser.add_argument('--china', 
                    dest='is_china',
                    help='IS China ?. Default: %(default)s',
                    action='store_true',
                    default=False,
                    required=False)

    parser.add_argument('--output', '-o',
                    dest='output',
                    help='Output filepath. Default: %(default)s',
                    default="azure-providers.json",
                    required=False)

    return parser.parse_args()

def main():

    args = options()

    logging.basicConfig(level=logging.INFO)

    token = get_access_token(subscription_id=args.subscription_id, 
                             user=args.user, 
                             password=args.password, 
                             tenant=args.tenant, 
                             is_china=args.is_china)

    providers = download_providers(token['access_token'], 
                             subscription_id=args.subscription_id, 
                             is_china=args.is_china)

    result = transform_providers(providers)

    with open(args.output, 'w') as fp:
        json.dump(result, fp, indent=4)

if __name__ == '__main__':
    main()
