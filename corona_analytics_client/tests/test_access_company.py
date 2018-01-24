from unittest import mock

import pytest

from corona_analytics_client.access_company import (CompanyParamsMixin, Company)
from lj_clients.clients import CoronaClient


class TestCompanyParamsMixin:

    @pytest.fixture
    def company_params(self):
        return CompanyParamsMixin()

    @pytest.mark.parametrize("name, company_id, result_expected", [
        (None, 10, {}),
        ('Awesome Company Limited', None, {'name': 'Awesome Company Limited'}),
        (None, None, {}),
    ])
    def test_add_params(
            self, company_params, name, company_id, result_expected):
        company_params.params = {}
        company_params.name = name
        company_params.company_id = company_id
        company_params._add_params()
        assert company_params.params == result_expected


class TestCompany:

    @pytest.fixture
    def company(self):
        corona_client = CoronaClient('dev')
        return Company(corona_client)

    @staticmethod
    def create_reponse(data, status=200):
        resp = mock.Mock(status=status)
        resp.json.return_value = data
        return resp

    test_companies_url = 'http://corona.limejump.dev:8202/api/companies/'

    test_billing_url = 'http://corona.limejump.dev:8202/api/billing-info/?company='

    test_site_url = 'http://corona.limejump.dev:8202/api/sites/'

    @pytest.mark.parametrize("company_id, name, resp", [
        (10, None, test_companies_url,),
    ])
    @mock.patch('corona_analytics_client.access_company.requests.get')
    def test_get_companies_response_company_id(
            self, mock_get, company, company_id, name, resp):
        mock_get.return_value = self.create_reponse(resp+str(company_id))
        company.company_id = company_id
        company.name = name
        company._add_params()
        company.get_companies_response()
        mock_get.assert_called_once_with(resp+str(company_id))

    @pytest.mark.parametrize("company_id, name, resp", [
        (None, 'Awesome AD Limited', test_companies_url,),
    ])
    @mock.patch('corona_analytics_client.access_company.requests.get')
    def test_get_companies_response_company_name(
            self, mock_get, company, company_id, name, resp):
        mock_get.return_value = self.create_reponse(resp)
        company.company_id = company_id
        company.name = name
        company._add_params()
        company.get_companies_response()
        mock_get.assert_called_once_with(
            resp, params={'name': 'Awesome AD Limited'})

    @pytest.mark.parametrize("company_id, name, resp", [
        (None, None, None,),
    ])
    @mock.patch('corona_analytics_client.access_company.requests.get')
    def test_get_companies_response_none(
            self, mock_get, company, company_id, name, resp):
        mock_get.return_value = self.create_reponse(resp)
        company.company_id = company_id
        company.name = name
        company._add_params()
        result = company.get_companies_response()
        assert not result

    @pytest.mark.parametrize("company_id, resp", [
        (10, test_billing_url,),
    ])
    @mock.patch('corona_analytics_client.access_company.requests.get')
    def test_get_billing_response(self, mock_get, company, company_id, resp):
        mock_get.return_value = self.create_reponse(resp+str(company_id))
        company.company_id = company_id
        company._add_params()
        company.get_billing_response()
        mock_get.assert_called_once_with(resp+str(company_id))

    @pytest.mark.parametrize("company_id, resp", [
        (None, None,),
    ])
    @mock.patch('corona_analytics_client.access_company.requests.get')
    def test_get_billing_response_none(
            self, mock_get, company, company_id, resp):
        mock_get.return_value = self.create_reponse(resp)
        company.company_id = company_id
        company._add_params()
        result = company.get_billing_response()
        assert not result

    @pytest.mark.parametrize("company_id, resp", [
        (10, test_site_url,),
    ])
    @mock.patch('corona_analytics_client.access_company.requests.get')
    def test_get_site_response(self, mock_get, company, company_id, resp):
        mock_get.return_value = self.create_reponse(resp+str(company_id))
        company.company_id = company_id
        company._add_params()
        company.get_site_response()
        mock_get.assert_called_once_with(resp+str(company_id))

    @pytest.mark.parametrize("company_id, resp", [
        (None, None,),
    ])
    @mock.patch('corona_analytics_client.access_company.requests.get')
    def test_get_site_response_none(self, mock_get, company, company_id, resp):
        mock_get.return_value = self.create_reponse(resp)
        company.company_id = company_id
        company._add_params()
        result = company.get_site_response()
        assert not result

    @pytest.mark.parametrize("resp, billing_details_expected", [
        ([{'billing_name': 'Horrible Hydro PLC'}],
         {'billing_name': 'Horrible Hydro PLC'},),
        (None, None,),
    ])
    @mock.patch('corona_analytics_client.access_company.Company.get_billing_response')
    def test_set_billing_details(
            self, mock_get, company, resp, billing_details_expected):
        mock_get.return_value = resp
        company.set_billing_details()
        assert company.billing_details == billing_details_expected

    @pytest.mark.parametrize(
        "company_resp, company_id, name, company_id_expected, name_expected", [
            ([], None, None, None, None),
            ({'name': 'Dodgey Diesel Corp', 'id': 10},
             10, None, 10, 'Dodgey Diesel Corp'),
            ({'name': 'Super Solar Ltd', 'id': 10},
             None, 'Super Solar Ltd', 10, 'Super Solar Ltd'),
            ({'name': 'Super Solar Ltd', 'id': 10},
             10, 'Super Solar Ltd', 10, 'Super Solar Ltd'),
        ])
    @mock.patch('corona_analytics_client.access_company.Company.get_companies_response')
    @mock.patch('corona_analytics_client.access_company.Company.get_billing_response')
    def test_set_billing_details(
            self, mock_billing, mock_company, company, company_resp, company_id,
            name, company_id_expected, name_expected):
        mock_billing.return_value = None
        mock_company.return_value = company_resp
        company.company_id = company_id
        company.name = name
        company.set_company_info()
        assert company.company_id == company_id_expected
        assert company.name == name_expected


if __name__ == "__main__":
    pytest.main(__file__)
