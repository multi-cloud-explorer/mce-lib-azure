import logging
import time

from azure.mgmt.resource.resources import ResourceManagementClient
from azure.common.credentials import UserPassCredentials, ServicePrincipalCredentials

logger = logging.getLogger(__name__)

__all__ = ['get_access_token', 'retry']


class AuthenticationError(Exception):
    pass


def get_access_token(
    subscription_id=None, user=None, password=None, tenant=None, is_china=False
):
    """
    Open Azure API session using AzureSDK and return Token

    :param subscription_id: Azure Subscription ID
    :type subscription_id: str
    :param user: UserName or Client ID
    :type user: str
    :param password: Password or Secret ID
    :type password: str
    :param tenant: Tenant ID
    :type tenant: str
    :param is_china: China Option
    :type is_china: bool

    :return: Token
    :rtype: dict

    """

    for field_name in ['subscription_id', 'user', 'password']:
        if locals().get(field_name, None) is None:
            raise AttributeError("field [%s] is required" % field_name)

    try:
        if not tenant:
            credentials = UserPassCredentials(user, password, china=is_china)
        else:
            credentials = ServicePrincipalCredentials(
                client_id=user, secret=password, tenant=tenant, china=is_china
            )
    except Exception as e:
        msg = 'Login Azure FAILED with message : %s' % str(e)
        logger.error(msg)
        raise AuthenticationError(msg)

    rm = ResourceManagementClient(credentials, subscription_id)
    if rm.config.generate_client_request_id:
        return credentials.token
    else:
        msg = 'login azure failed'
        logger.error(msg)
        raise AuthenticationError(msg)


def retry(tries=3, sleep_time=2):
    """Retry calling the decorated function

    :param tries: number of times to try
    :type tries: int

    >>> @retry(tries=3, sleep_time=2)
    >>> def download_page(url):
    >>> ...return requests.get(url)

    """

    def try_it(func):
        def f(*args, **kwargs):
            attempts = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    logger.error(
                        "retry %s - error[%s] - attempts[%s/%s]"
                        % (func, str(e), attempts, tries)
                    )
                    if attempts >= tries:
                        raise e
                    time.sleep(sleep_time)

        return f

    return try_it
