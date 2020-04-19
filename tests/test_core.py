import pytest
from unittest.mock import patch

from mce_azure import core

def test_get_resourcegroups_list(mock_response_class, json_file):

    data = json_file("resource_group_list.json")

    with patch("requests.Session.get") as func:
        func.return_value = mock_response_class(200, data)
        session = core.get_session("test")
        response = core.get_resourcegroups_list("00000000-0000-0000-0000-000000000000", session=session)
        assert response == data["value"]

def test_get_resources_list(mock_response_class, json_file):

    data = json_file("resource_list.json")

    with patch("requests.Session.get") as func:
        func.return_value = mock_response_class(200, data)
        session = core.get_session("test")
        response = list(core.get_resources_list("00000000-0000-0000-0000-000000000000", session=session))
        assert response == data["value"]

def test_get_resource_by_id(mock_response_class, json_file):

    data = json_file("resource-vm.json")
    resource_id = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/MY_RG_GROUP/providers/Microsoft.Compute/virtualMachines/MY_VM"

    with patch("requests.Session.get") as func:
        func.return_value = mock_response_class(200, data)
        session = core.get_session("test")
        response = core.get_resource_by_id(resource_id, session=session)
        assert response == data

@pytest.mark.skipif(core.GEVENT is False, reason="Gevent not available")
def test_async_get_resources(mock_response_class, json_file):
    raise NotImplementedError()
