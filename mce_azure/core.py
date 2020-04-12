import logging
import time
from pprint import pprint
import os
import argparse
import json

import requests
from decouple import config
from dotenv import load_dotenv

from .utils import get_access_token, retry

logger = logging.getLogger(__name__)

load_dotenv(verbose=False)

DEFAULT_SUBSCRIPTION = config('MCE_AZURE_SUBSCRIPTION', default=None)
DEFAULT_TENANT = config('MCE_AZURE_TENANT', default=None)
DEFAULT_USER = config('MCE_AZURE_USER', default=None)
DEFAULT_PASSWORD = config('MCE_AZURE_PASSWORD', default=None)

CURRENT = os.path.abspath(os.path.dirname(__file__))
PROVIDERS_FILEPATH = config(
    'MCE_PROVIDERS_FILEPATH', default=os.path.join(CURRENT, 'azure-providers.json')
)

PROVIDERS = None


def get_ratelimit_header(headers):
    for k, v in headers.items():
        if k.startswith("x-ms-ratelimit-remaining"):
            return k, v

    return None, None


def load_providers(filepath=PROVIDERS_FILEPATH):
    global PROVIDERS

    if not os.path.exists(filepath):
        raise RuntimeError(f"{filepath} not found")

    with open(filepath) as fp:
        _providers = json.load(fp)
        PROVIDERS = {k.lower(): v for k, v in _providers.items()}
    if not PROVIDERS:
        raise Exception("PROVIDERS empty")

    logger.info(f"user provider filepath: {filepath}")

    return PROVIDERS


load_providers()


def get_azure_base_url(is_china=False):
    if is_china:
        return "https://management.chinacloudapi.cn"
    return "https://management.azure.com"


def get_api_version(resource_id):
    asset_split = resource_id.split('/')
    asset_type = f"{asset_split[6]}/{asset_split[7]}"
    api_version = PROVIDERS.get(asset_type.lower())

    if not api_version:
        raise Exception(f"api_version not found for type {asset_type}")

    return api_version


def get_session(token=None):
    session = requests.Session()
    session.headers['authorization'] = 'Bearer %s' % token
    return session


# TODO: retry paramètrable
# TODO: renvoyer le ratelimit
@retry(tries=3, sleep_time=2)
def get_resource_by_id(resource_id, session=None, token=None, is_china=False):
    """Get Resource by ID
    
    # TODO: doc args

    @see: https://docs.microsoft.com/en-us/rest/api/resources/resources/getbyid
    """

    # TODO: voir si valable partout: &$expand=resourceTypes/aliases

    base_url = get_azure_base_url(is_china=is_china)
    api_version = get_api_version(resource_id)
    resource_id = resource_id.lstrip('/')

    url = f"{base_url}/{resource_id}?api-version={api_version}"
    session = session or get_session(token=token)

    resp = session.get(url)

    rate_header, rate_value = get_ratelimit_header(resp.headers)
    msg = f"ratelimit : {rate_header}={rate_value} - {resource_id}"
    logger.info(msg)

    resp.raise_for_status()

    return resp.json()


"""
{
  "value": [
    {
      "id": "/tenants/a70a1586-9c4a-4373-b907-1d310660dbd1",
      "tenantId": "a70a1586-9c4a-4373-b907-1d310660dbd1",
      "countryCode": "US",
      "displayName": "Test_Test_aad50",
      "domains": [
        "aad50.ccsctp.net"
      ],
      "tenantCategory": "ManagedBy",
      "defaultDomain": "aad50.ccsctp.net",
      "tenantType": "AAD"
    },
"""


def get_tenant_list(session=None, token=None):
    """
    1 tenant pour plusieurs souscription
    """


"""
{
  "value": [
    {
      "id": "/subscriptions/291bba3f-e0a5-47bc-a099-3bdcb2a50a05",
      "subscriptionId": "291bba3f-e0a5-47bc-a099-3bdcb2a50a05",
      "tenantId": "31c75423-32d6-4322-88b7-c478bdde4858",
      "displayName": "Example Subscription",
      "state": "Enabled",
      "subscriptionPolicies": {
        "locationPlacementId": "Internal_2014-09-01",
        "quotaId": "Internal_2014-09-01",
        "spendingLimit": "Off"
      },
      "authorizationSource": "RoleBased",
      "managedByTenants": [
        {
          "tenantId": "8f70baf1-1f6e-46a2-a1ff-238dac1ebfb7"
        }
      ],
      "tags": {
        "tagKey1": "tagValue1",
        "tagKey2": "tagValue2"
      }
    },
"""


def get_subscriptions_list(session=None, token=None):
    """Get Subscriptions List

    @see: https://docs.microsoft.com/en-us/rest/api/resources/subscriptions/list

    """
    # https://docs.microsoft.com/en-us/rest/api/resources/subscriptions/listlocations
    # api_version = PROVIDERS.get("Microsoft.Resources/resources".lower())

    raise NotImplementedError()


# TODO: filter type
def get_resources_list(
    subscription_id, session=None, token=None, is_china=False, includes=PROVIDERS
):
    """Get Resources List

    @see: https://docs.microsoft.com/en-us/rest/api/resources/resources/list
    """

    base_url = get_azure_base_url(is_china=is_china)

    api_version = PROVIDERS.get("Microsoft.Resources/resources".lower())

    url = f"{base_url}/subscriptions/{subscription_id}/resources?api-version={api_version}"
    session = session or get_session(token=token)

    resp = session.get(url)

    rate_header, rate_value = get_ratelimit_header(resp.headers)
    msg = f"ratelimit : {rate_header}={rate_value} - {subscription_id}"
    logger.info(msg)

    resp.raise_for_status()

    for item in resp.json()['value']:
        if item['type'].lower() in includes:
            yield item
        else:
            logger.info("exclude type : %s" % item['type'].lower())


"""
https://docs.microsoft.com/fr-fr/azure/azure-resource-manager/management/request-limits-and-throttling
    HTTP status code 429 Too many requests
    The response includes a Retry-After value

x-ms-ratelimit-remaining-subscription-reads	Requêtes de lecture restantes étendues à l’abonnement. Cette valeur est renvoyée pour les opérations de lecture.
    az group list --verbose --debug
x-ms-ratelimit-remaining-subscription-writes

x-ms-ratelimit-remaining-tenant-reads
x-ms-ratelimit-remaining-tenant-writes

x-ms-ratelimit-remaining-subscription-resource-requests
x-ms-ratelimit-remaining-subscription-resource-entities-read

x-ms-ratelimit-remaining-tenant-resource-requests
x-ms-ratelimit-remaining-tenant-resource-entities-read

https://docs.microsoft.com/en-us/azure/azure-resource-manager/management/request-limits-and-throttling
Subscription	reads	12000
Subscription	deletes	15000
Subscription	writes	1200
Tenant	reads	12000
Tenant	writes	1200
"""


def get_resourcegroups_list(subscription_id, session=None, token=None, is_china=False):
    """Get ResourceGroup List
    
    https://docs.microsoft.com/en-us/rest/api/resources/resourcegroups/list
    """

    base_url = get_azure_base_url(is_china=is_china)

    api_version = PROVIDERS.get(
        "Microsoft.Resources/subscriptions/resourceGroups".lower()
    )

    url = f"{base_url}/subscriptions/{subscription_id}/resourcegroups?api-version={api_version}"
    session = session or get_session(token=token)

    resp = session.get(url)

    rate_header, rate_value = get_ratelimit_header(resp.headers)
    msg = f"ratelimit : {rate_header}={rate_value} - {subscription_id}"
    logger.info(msg)

    resp.raise_for_status()

    return resp.json()['value']


def get_resourcegroup_by_name(
    subscription_id, resource_group_name, session=None, token=None, is_china=False
):
    """Get ResourceGroup List
    
    GET https://management.azure.com/subscriptions/{subscriptionId}/resourcegroups/{resourceGroupName}?api-version=2019-10-01
    """
    raise NotImplementedError()


def async_get_resources(subscription_id, session, pool_size=20):

    from gevent.pool import Pool

    pool = Pool(pool_size)

    resources = []
    errors = []
    greenlets = []

    for item in get_resources_list(
        subscription_id, session=session, includes=PROVIDERS
    ):
        resource_id = item['id']
        try:
            greenlets.append(
                pool.spawn(get_resource_by_id, resource_id, session=session)
            )
        except Exception as err:
            msg = "fetch resource [%s] error : %s" % (resource_id, err)
            logger.error(msg)

    pool.join()

    for g in greenlets:
        if g.successful():
            resources.append(g.value)
        else:
            errors.append(g.exception)

    return resources, errors


def options():

    parser = argparse.ArgumentParser(
        description='Azure Exlorer',
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=True,
    )

    parser.add_argument(
        '--subscription',
        '-b',
        dest='subscription_id',
        help='Subscription_id ID (provider format). Default: %(default)s',
        default=DEFAULT_SUBSCRIPTION,
    )  # required=True)

    parser.add_argument(
        '--tenant',
        '-t',
        dest='tenant',
        help='Tenant ID. Default: %(default)s',
        default=DEFAULT_TENANT,
    )  # required=True)

    parser.add_argument(
        '--user',
        '-u',
        dest='user',
        help='Client ID or Username. Default: %(default)s',
        default=DEFAULT_USER,
    )  # required=True)

    parser.add_argument(
        '--password',
        '-p',
        dest='password',
        help='Secret ID or Password.',
        default=DEFAULT_PASSWORD,
    )  # required=True)

    parser.add_argument(
        '--resource-id',
        '-r',
        dest='resource_id',
        help='Get resource ID',
        required=False,
    )

    parser.add_argument(
        '--china',
        dest='is_china',
        help='China Subscription ?. Default: %(default)s',
        action='store_true',
        default=False,
        required=False,
    )

    parser.add_argument('--json', action="store_true")

    parser.add_argument('--debug', action="store_true")

    parser.add_argument(
        '--command',
        '-C',
        choices=['get', 'list', 'group'],
        dest='command',
        help='Command',
        required=True,
    )

    parser.add_argument(
        '--export', dest='export_json_file', help='Export File', required=False
    )

    parser.add_argument(
        '--expand',
        action="store_true",
        help='fetch all informations for each Resource. (for list command only)',
    )

    return parser.parse_args()


def main():
    args = options()

    logging_level = logging.INFO

    if args.debug:
        logging_level = logging.DEBUG

    logging.basicConfig(level=logging_level)

    subscription_id = args.subscription_id
    user = args.user
    password = args.password
    tenant = args.tenant
    resource_id = args.resource_id

    token = get_access_token(
        subscription_id=subscription_id,
        user=user,
        password=password,
        tenant=tenant,
        is_china=False,
    )

    session = get_session(token=token['access_token'])

    start = time.time()

    if args.command == "get" and resource_id:
        data = get_resource_by_id(resource_id, session=session)
        if args.json:
            print(
                json.dumps(
                    data, indent=4, escape_forward_slashes=False, ensure_ascii=False
                )
            )
        else:
            pprint(data)

    elif args.command == "list":

        if args.export_json_file:
            with open(args.export_json_file, 'w') as fp:

                if args.expand:
                    datas = []

                    for item in get_resources_list(
                        subscription_id, session=session, includes=PROVIDERS
                    ):
                        try:
                            datas.append(
                                get_resource_by_id(item['id'], session=session)
                            )
                        except Exception as err:
                            msg = "fetch resource [%s] error : %s" % (item['id'], err)
                            logger.error(msg)

                    json.dump(
                        datas,
                        fp,
                        indent=4,
                        escape_forward_slashes=False,
                        ensure_ascii=False,
                    )
                else:

                    resource_list = list(
                        get_resources_list(
                            subscription_id, session=session, includes=PROVIDERS
                        )
                    )
                    json.dump(
                        resource_list,
                        fp,
                        indent=4,
                        escape_forward_slashes=False,
                        ensure_ascii=False,
                    )
        else:
            for item in get_resources_list(
                subscription_id, session=session, includes=PROVIDERS
            ):
                if args.expand:
                    item = get_resource_by_id(item['id'], session=session)
                print('--------------------------------------------------------')
                pprint(item)
                print('--------------------------------------------------------')

    elif args.command == "group":
        data = get_resourcegroups_list(subscription_id, session=session)
        if args.json:
            print(
                json.dumps(
                    data, indent=4, escape_forward_slashes=False, ensure_ascii=False
                )
            )
        else:
            pprint(data)

    duration = time.time() - start
    logger.info("DURATION: %d" % duration)


if __name__ == "__main__":
    main()
