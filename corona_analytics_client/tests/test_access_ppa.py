import datetime
from unittest import mock

import pytest

from corona_analytics_client.access_ppa import (PPAContract, MPAN, CoronaPPAParamsMixin, AllPPAMPANs)
from lj_clients.clients import CoronaClient


class TestCoronaPPAParamsMixin:

    @pytest.fixture
    def corona_mixin(self):
        return CoronaPPAParamsMixin()

    test_params_de_morgans = {
        'mpan': '008450062012345678910',
        'contract_start_date_lte': datetime.date(2015, 1, 31),
        'contract_end_date_gte': datetime.date(2015, 1, 1),
    }

    test_params_start_only = {
        'mpan': '008450062012345678910',
        'contract_start_date_gte': datetime.date(2015, 1, 1),
    }

    test_params_end_only = {
        'mpan': '008450062012345678910',
        'contract_end_date_lte': datetime.date(2015, 1, 31),
    }

    test_params_mpan_only = {
        'mpan': '008450062012345678910',
    }

    test_params_mpan_contracted = {
        'mpan': '008450062012345678910',
        'contracted_ppa': 'true',
    }

    test_params_mpan_contracted_cancelled = {
        'mpan': '008450062012345678910',
        'contracted_ppa': 'true',
        'remove_cancelled_contracts': 'true',
    }

    @pytest.mark.fast_test
    @pytest.mark.parametrize("boolean, result_expected", [
        (True, 'true'),
        (False, 'false'),
        (None, 'false'),
    ])
    def test_boolean_handler(self, corona_mixin, boolean, result_expected):
        result = corona_mixin._boolean_handler(boolean)
        assert result == result_expected

    @pytest.mark.fast_test
    @pytest.mark.parametrize(
        "full_mpan, start_date, end_date, contracted_ppa, "
        "remove_cancelled_contracts, params_expected", [
            ('008450062012345678910',
             datetime.date(2015, 1, 1), datetime.date(2015, 1, 31), False,
             False, test_params_de_morgans,
             ),
            ('008450062012345678910',
             datetime.date(2015, 1, 1), None, False, False,
             test_params_start_only,
             ),
            ('008450062012345678910',
             None, datetime.date(2015, 1, 31), False, False,
             test_params_end_only,
             ),
            ('008450062012345678910',
             None, None, False, False,
             test_params_mpan_only,
             ),
            ('008450062012345678910',
             None, None, True, False,
             test_params_mpan_contracted,
             ),
            ('008450062012345678910',
             None, None, True, True,
             test_params_mpan_contracted_cancelled,
             ),
        ])
    def test_add_params(
            self, corona_mixin, full_mpan, start_date, end_date, contracted_ppa,
            remove_cancelled_contracts, params_expected):
        corona_mixin.params = {}
        corona_mixin.full_mpan = full_mpan
        corona_mixin.start_date = start_date
        corona_mixin.end_date = end_date
        corona_mixin.contracted_ppa = contracted_ppa
        corona_mixin.remove_cancelled_contracts = remove_cancelled_contracts
        corona_mixin._add_params()
        assert corona_mixin.params == params_expected


class TestAllPPAMPANs:

    test_resp = [
        {
            'mpan': '008450062012345678910',
            'contract_start_date_lte': datetime.date(2015, 1, 31),
            'contract_end_date_gte': datetime.date(2015, 1, 1)
        },
        {
            'mpan': '008450062012345678911',
            'contract_start_date_lte': datetime.date(2015, 1, 31),
            'contract_end_date_gte': datetime.date(2015, 1, 1)
        },
    ]

    test_resp_start_only = [
        {
            'mpan': '008450062012345678910',
            'contract_start_date_gte': datetime.date(2015, 1, 31),
        },
        {
            'mpan': '008450062012345678911',
            'contract_start_date_gte': datetime.date(2015, 1, 31),
        },
    ]

    test_resp_quote_id = [
        {
            'quote_id': 1001,
            'contract_start_date_lte': datetime.date(2015, 1, 31),
            'contract_end_date_gte': datetime.date(2015, 1, 1)
        },
        {
            'quote_id': 1009,
            'contract_start_date_lte': datetime.date(2015, 1, 31),
            'contract_end_date_gte': datetime.date(2015, 1, 1)
        },
    ]

    test_url_quotes = 'http://corona.limejump.dev:8202/api/ppa/quotes/'

    @pytest.fixture
    def all_mpans(self, start_date, end_date):
        corona_client = CoronaClient('dev')
        return AllPPAMPANs(corona_client, start_date, end_date)

    def create_response(self, data, status=200):
        resp = mock.Mock(status=status)
        resp.json.return_value = data
        return resp

    @pytest.mark.fast_test
    @pytest.mark.parametrize(
        "resp, url, corona_client, start_date, end_date, contracted_ppa, remove_cancelled", [
            (test_resp, test_url_quotes, CoronaClient('dev'), datetime.date(2015, 1, 1),
             datetime.date(2015, 1, 31), True, True),
        ])
    @mock.patch('corona_analytics_client.access_ppa.requests.get')
    def test_get_corona_response_both(
            self, mock_get, resp, url, corona_client, start_date, end_date, contracted_ppa,
            remove_cancelled):
        mock_get.return_value = self.create_response(resp)
        all_ppas = AllPPAMPANs(
            corona_client, start_date, end_date, contracted_ppa, remove_cancelled)
        all_ppas._add_params()
        all_ppas.get_corona_response()
        mock_get.assert_called_once_with(
            url, params={'contract_start_date_lte': end_date,
                         'contract_end_date_gte': start_date,
                         'contracted_ppa': 'true',
                         'remove_cancelled_contracts': 'true',
                         })

    @pytest.mark.fast_test
    @pytest.mark.parametrize(
        "resp, url, corona_client, start_date, end_date, contracted_ppa, remove_cancelled", [
            (test_resp_start_only, test_url_quotes, CoronaClient('dev'),
             datetime.date(2015, 1, 1), None, True, True),
        ])
    @mock.patch('corona_analytics_client.access_ppa.requests.get')
    def test_get_corona_response_one(
            self, mock_get, resp, url, corona_client, start_date, end_date, contracted_ppa,
            remove_cancelled):
        mock_get.return_value = self.create_response(resp)
        all_ppas = AllPPAMPANs(
            corona_client, start_date, end_date, contracted_ppa, remove_cancelled)
        all_ppas._add_params()
        all_ppas.get_corona_response()
        mock_get.assert_called_once_with(url, params={
            'contract_start_date_gte': start_date,
            'contracted_ppa': 'true',
            'remove_cancelled_contracts': 'true',
             })

    @pytest.mark.fast_test
    @pytest.mark.parametrize(
        "resp, url, corona_client, start_date, end_date, contracted_ppa, remove_cancelled,"
        " result_expected", [
            (test_resp, test_url_quotes, CoronaClient('dev'),
             datetime.date(2015, 1, 1), datetime.date(2015, 1, 31), True,
             False, {'008450062012345678910', '008450062012345678911'},),
        ])
    @mock.patch('corona_analytics_client.access_ppa.requests.get')
    def test_get_all_mpans(
            self, mock_get, resp, url, corona_client, start_date, end_date, contracted_ppa,
            remove_cancelled, result_expected):
        mock_get.return_value = self.create_response(resp)
        all_ppas = AllPPAMPANs(
            corona_client, start_date, end_date, contracted_ppa, remove_cancelled)
        result = all_ppas.get_all_ppa_mpans()
        mock_get.assert_called_once_with(url, params={
            'contract_start_date_lte': end_date,
            'contract_end_date_gte': start_date,
            'contracted_ppa': 'true',
            })
        assert result == result_expected

    @pytest.mark.fast_test
    @pytest.mark.parametrize(
        "resp, url, corona_client, start_date, end_date, contracted_ppa, remove_cancelled,"
        " result_expected", [
            (test_resp_quote_id, test_url_quotes, CoronaClient('dev'),
             datetime.date(2015, 1, 1), datetime.date(2015, 1, 31), True,
             False, {1001, 1009},),
        ])
    @mock.patch('corona_analytics_client.access_ppa.requests.get')
    def test_get_all_quotes(
            self, mock_get, resp, url, corona_client, start_date, end_date, contracted_ppa,
            remove_cancelled, result_expected):
        mock_get.return_value = self.create_response(resp)
        all_ppas = AllPPAMPANs(
            corona_client, start_date, end_date, contracted_ppa, remove_cancelled)
        result = all_ppas.get_all_ppa_quote_ids()
        mock_get.assert_called_once_with(url, params={
            'contract_start_date_lte': end_date,
            'contract_end_date_gte': start_date,
            'contracted_ppa': 'true',
            })
        assert result == result_expected


class TestPPAContract:

    @pytest.fixture
    def ppa_contract(self, **kwargs):
        corona_client = CoronaClient('dev')
        return PPAContract(corona_client, **kwargs)

    test_resp = [
        {
            'value': 50.0, 'price_type': 'power',
            'pass_through_percent': 95.5, 'product_quote_type': 'Flexible'
        },
    ]

    test_values = {
        'values': {
            'power': 50.0,
        },
        'pass_throughs': {
            'power': 0.955,
        },
        'contract_types': {
            'power': 'Flexible',
        },
    }

    test_resp_2 = [
        {
            'value': 50.0, 'price_type': 'power',
            'pass_through_percent': 95.5, 'product_quote_type': 'Flexible'
        },
        {
            'value': 0.22, 'price_type': 'aahedc',
            'pass_through_percent': 96, 'product_quote_type': 'Flexible'
        },
    ]

    test_values_2 = {
        'values': {
            'power': 50.0, 'aahedc': 0.22,
        },
        'pass_throughs': {
            'power': 0.955, 'aahedc': 0.96,
        },
        'contract_types': {
            'power': 'Flexible', 'aahedc': 'Flexible',
        },
    }

    test_url_products = 'http://corona.limejump.dev:8202/api/ppa/product-quotes/'

    def create_response(self, data, status=200):
        resp = mock.Mock(status=status)
        resp.json.return_value = data
        return resp

    @pytest.mark.fast_test
    @pytest.mark.parametrize("resp, url, corona_client, quote_id, values_expected", [
        (test_resp, test_url_products, CoronaClient('dev'), 1, test_values),
        (test_resp_2, test_url_products, CoronaClient('dev'), 1000, test_values_2),
    ])
    @mock.patch('corona_analytics_client.access_ppa.requests.get')
    def test_set_quote_info(
            self, mock_get, resp, url, corona_client, quote_id, values_expected):
        mock_get.return_value = self.create_response(resp)
        contract = PPAContract(corona_client, quote_id=quote_id)
        mock_get.assert_called_once_with(
            url, params={
                'quote_id': quote_id,
            })
        for price in values_expected['values']:
            assert contract.values[price] == values_expected['values'][price]
            assert contract.pass_throughs[price] == values_expected[
                'pass_throughs'][price]
            assert contract.contract_types[price] == values_expected[
                'contract_types'][price]

    @pytest.mark.fast_test
    @pytest.mark.parametrize("resp, url, corona_client, quote_id", [
        (None, test_url_products, CoronaClient('dev'), 1),
    ])
    @mock.patch('corona_analytics_client.access_ppa.requests.get')
    def test_set_quote_info_none(self, mock_get, resp, url, corona_client, quote_id):
        mock_get.return_value = self.create_response(resp)
        contract = PPAContract(corona_client, quote_id=quote_id)
        mock_get.assert_called_once_with(
            url, params={
                'quote_id': quote_id,
            })
        assert not contract.values
        assert not contract.pass_throughs
        assert not contract.contract_types

    @pytest.mark.fast_test
    @pytest.mark.parametrize("str_dates, result_expected", [
        (('2016-01-01', '2016-10-31'),
         (datetime.date(2016, 1, 1), datetime.date(2016, 10, 31)),),
        ((None, None), (None, None),),
        (('2016-1-1', '2016-10-31'),
         (datetime.date(2016, 1, 1), datetime.date(2016, 10, 31)),),
    ])
    @mock.patch('corona_analytics_client.access_ppa.PPAContract.get_quote_info')
    def test_set_dates(
            self, access_get, ppa_contract, str_dates, result_expected):
        access_get.return_value = self.create_response(None)
        ppa_contract.details['contract_start_date'] = str_dates[0]
        ppa_contract.details['contract_end_date'] = str_dates[1]
        ppa_contract.set_dates()
        assert ppa_contract.details['contract_start_date'] == result_expected[0]
        assert ppa_contract.details['contract_end_date'] == result_expected[1]

    @pytest.mark.fast_test
    @pytest.mark.parametrize(
        "details, spill_start_expected, spill_end_expected", [
            ({}, None, None),
            ({'spill_period': 0}, None, None),
            ({'spill_period': 5,
              'contract_start_date': datetime.date(2016, 1, 1)},
             datetime.date(2016, 1, 1), datetime.date(2016, 1, 5)),
            ({'spill_period': 365,
              'contract_start_date': datetime.date(2015, 1, 1)},
             datetime.date(2015, 1, 1), datetime.date(2015, 12, 31)),
        ])
    def test_set_spill_dates(
            self, ppa_contract, details, spill_start_expected,
            spill_end_expected):
        ppa_contract.details = details
        ppa_contract.set_spill_dates()
        assert ppa_contract.details['spill_start'] == spill_start_expected
        assert ppa_contract.details['spill_end'] == spill_end_expected


class TestMPAN:

    @pytest.fixture
    def ppa_contract(self, **kwargs):
        corona_client = CoronaClient('dev')
        return PPAContract(corona_client, **kwargs)

    @pytest.fixture
    def mpan(self):
        full_mpan = ""
        start_date = None
        end_date = None
        corona_client = CoronaClient('dev')
        return MPAN(corona_client, full_mpan, start_date, end_date)

    test_contract_details = [
        {'quote_id': 100, 'spill_start': None, 'spill_end': None},
        {'quote_id': 101, 'spill_start': None, 'spill_end': None},
    ]

    test_contract_details2 = [
        {'quote_id': 100, 'spill_start': None, 'spill_end': None},
        {'quote_id': 1001, 'spill_start': None, 'spill_end': None},
        {'quote_id': 101, 'spill_start': None, 'spill_end': None},
    ]

    test_contract_details3 = [
        {'quote_id': 100, 'spill_period': 0, 'spill_start': None, 'spill_end': None},
        {'quote_id': 101, 'spill_period': 0, 'spill_start': None, 'spill_end': None},
    ]

    test_url_quotes = 'http://corona.limejump.dev:8202/api/ppa/quotes/'

    test_url_billing = 'http://corona.limejump.dev:8202/api/ppa/billing-info/'

    test_billing_details = [{
        'billing_name': 'test', 'address_line_1': 'street',
        'address_line_2': 'city', 'address_line_3': 'county',
        'vat_number': '123'
    }]

    test_url_sites = 'http://corona.limejump.dev:8202/api/sites/'

    test_sites = {
        'company': 12, 'site': 1, 'name': 'test_name'
    }

    def create_response(self, data, status=200):
        resp = mock.Mock(status=status)
        resp.json.return_value = data
        return resp

    @pytest.mark.fast_test
    @pytest.mark.parametrize("test_contracts, contract_expected", [
        (test_contract_details,
         {'quote_id': 101, 'spill_start': None, 'spill_end': None}),
        (test_contract_details2,
         {'quote_id': 1001, 'spill_start': None, 'spill_end': None}),
        (test_contract_details3,
         {'quote_id': 101, 'spill_period': 0, 'spill_start': None,
          'spill_end': None}),
    ])
    @mock.patch('corona_analytics_client.access_ppa.requests.get')
    def test_set_ppa_contracts(
            self, mock_get, mpan, test_contracts, contract_expected):
        mpan.ppa_contracts = []
        for contract_details in test_contracts:
            mock_get.json.return_value = contract_details
            mpan.ppa_contracts.append(self.ppa_contract(**contract_details))
        mpan.set_live_ppa_contract()
        assert mpan.live_ppa_contract.details == contract_expected

    @pytest.mark.fast_test
    def test_set_ppa_contracts_none(self, mpan):
        mpan.ppa_contracts = []
        mpan.set_live_ppa_contract()
        assert not mpan.live_ppa_contract

    @pytest.mark.fast_test
    @pytest.mark.parametrize("resp, url, corona_client, site_id", [
        (test_sites, test_url_sites, CoronaClient('dev'), 12),
    ])
    @mock.patch('corona_analytics_client.access_ppa.requests.get')
    def test_get_site_info(
            self, mock_get, mpan, resp, url, corona_client, site_id):
        mpan.live_ppa_contract = PPAContract(corona_client)
        mpan.live_ppa_contract.details['site'] = site_id
        mock_get.return_value = self.create_response(resp)
        mpan.get_site_info()
        mock_get.assert_called_once_with(url + str(site_id))

    @pytest.mark.fast_test
    @pytest.mark.parametrize("resp, site_resp, corona_client, site_id", [
        (test_billing_details, test_sites, CoronaClient('dev'), 12),
    ])
    @mock.patch('corona_analytics_client.access_ppa.requests.get')
    def test_set_billing_details(
            self, mock_get, mpan, resp, site_resp, corona_client, site_id):
        mpan.live_ppa_contract = PPAContract(corona_client)
        mpan.live_ppa_contract.details['site'] = site_id
        mock_get.return_value = self.create_response(resp)
        mpan.set_billing_details(site_resp)
        mock_get.assert_called_once_with(
            'http://corona.limejump.dev:8202/api/billing-info/?company=' +
            str(site_id))

    @pytest.mark.fast_test
    @pytest.mark.parametrize("resp, site_resp", [
        (None, None,),
    ])
    @mock.patch('corona_analytics_client.access_ppa.requests.get')
    def test_set_billing_details_none(self, mock_get, mpan, resp, site_resp):
        mpan.live_ppa_contract = None
        mock_get.return_value = self.create_response(resp)
        mpan.set_billing_details(site_resp)
        assert not mpan.billing_details

    @pytest.mark.fast_test
    @pytest.mark.parametrize("site_resp, result_expected", [
        (test_sites, 'test_name'),
        ({}, None),
    ])
    def test_set_site_name(self, mpan, site_resp, result_expected):
        mpan.set_site_name(site_resp)
        assert mpan.site_name == result_expected

    @pytest.mark.fast_test
    @pytest.mark.parametrize("site_resp, result_expected", [
        (test_sites, 12),
        ({}, None),
    ])
    def test_set_company_id(self, mpan, site_resp, result_expected):
        mpan.set_company_id(site_resp)
        assert mpan.company_id == result_expected

    @pytest.mark.fast_test
    @pytest.mark.parametrize("details, result_expected", [
        ({'technology': 'AD'}, 'export'),
        ({'technology': 'Import'}, 'import'),
        ({}, None),
    ])
    def test_set_meter_type(self, mpan, details, result_expected):
        mpan.live_ppa_contract = self.ppa_contract()
        mpan.live_ppa_contract.details = details
        mpan.set_meter_type()
        assert mpan.meter_type == result_expected

    def test_get_start_live_end_live(self):
        mpan = '008456982100041340401'
        corona_client = CoronaClient('prod')
        my_mpan = MPAN(corona_client, mpan)
        my_mpan.set_all_info()
        print("")


if __name__ == "__main__":
    pytest.main(__file__)
