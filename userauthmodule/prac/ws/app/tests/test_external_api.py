from unittest.mock import patch,Mock
import pytest

@patch('api.services.requests.get')
def test_external_api_integration(mock_get):
    mock_respone = Mock()
    mock_response.json.return_value = {'data': 'test'}
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    service = ExternalAPIService()
    result = service.get_data('endpoint')

    assert result == {'data' : 'test'}
    mock_get.assert_called_once()

    
