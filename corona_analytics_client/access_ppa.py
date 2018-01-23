import requests
import datetime
import os
from dateutil.relativedelta import relativedelta
from geopy.geocoders import Nominatim

# from access.access_quotation import AccessQuotation, QuoteDetail
# from access.access_trade_capture import AccessMonthlyScalars


class CoronaPPAParamsMixin(object):
    full_mpan = None
    start_date = None
    end_date = None
    contracted_ppa = None
    remove_cancelled_contracts = None
    params = {}

    @staticmethod
    def _boolean_handler(boolean):
        """
        Django syntax requires booleans as lower case strings.
        :param boolean:
        :return: boolean string equivalent.
        """
        if boolean:
            return 'true'
        return 'false'

    def _add_params(self):
        """
        Add kwargs to _params for query filtering.
        MPAN is always added, and contract start and end date are added
        depending.

        contracted_ppa filter in Django is only used if True, where is filters
        quotes which have a contract (signed).

        remove_cancelled_contracts again is only used if False, where filter
        removes contracts which are cancelled.

        If both attributes are given, then contracts are found via
        De Morgan's Law.

        Else they are treated as individual entities and a simple boundary
        condition is used.
        """
        if self.full_mpan:
            self.params['mpan'] = self.full_mpan
        if self.contracted_ppa:
            self.params['contracted_ppa'] = self._boolean_handler(
                self.contracted_ppa)
        if self.remove_cancelled_contracts:
            self.params[
                'remove_cancelled_contracts'] = self._boolean_handler(
                self.remove_cancelled_contracts)
        if self.start_date and self.end_date:
            # De Morgan's Law
            self.params['contract_start_date_lte'] = self.end_date
            self.params['contract_end_date_gte'] = self.start_date
        else:
            if self.start_date:
                self.params['contract_start_date_gte'] = self.start_date
            if self.end_date:
                self.params['contract_end_date_lte'] = self.end_date


class AllPPAMPANs(CoronaPPAParamsMixin):
    """
    Class to return all live MPANs for PPA.

    You can add other params before calling the get methods:

    self.params['roc_factor_gt'] = 0.1
    self.params['meter_type'] = 'export'

    :param start_date: start date of query period, datetime.date()
    :param end_date: end date of query period, datetime.date()
    :param contracted_ppa: whether quote/ contract is signed, boolean
    :param remove_cancelled_contracts: if you want to remove cancelled
    contracts from results, boolean. If False then cancelled contracts are
    returned.
    """
    def __init__(self, corona_client, start_date, end_date, contracted_ppa=True,
                 remove_cancelled_contracts=True):
        self.corona_client = corona_client
        self.start_date = start_date
        self.end_date = end_date
        self.contracted_ppa = contracted_ppa
        self.remove_cancelled_contracts = remove_cancelled_contracts
        self.params = {}

    def get_corona_response(self):
        url = self.corona_client.get_url('ppa-quotes')
        url = url.format('')
        return requests.get(url, params=self.params).json()

    def get_all_ppa_mpans(self, quote_type=None):
        self._add_params()
        resp = self.get_corona_response()
        if quote_type:
            return {quote['mpan'] for quote in resp if quote['quote_type'] == quote_type}
        else:
            return {quote['mpan'] for quote in resp}

    def get_all_ppa_mpans_with_no_params(self):
        resp = self.get_corona_response()
        return {quote['mpan'] for quote in resp}

    def get_all_ppa_quote_ids(self):
        self._add_params()
        resp = self.get_corona_response()
        return {quote['quote_id'] for quote in resp}

    # def get_all_mpans_by_meter_type(self, meter_type=None, get_quote_ids=False, get_live_dates=False):
    #     """
    #     Get a dict of mpans with a dict of their details, so it's
    #     {mpan 1: {full_mpan: full_mpan, 'technology': tech, 'site_name': site_name,
    #                 'meter_type': meter_type, 'kW': 'capacity_kw', 'contracts': contracts object
    #     :param meter_type:
    #     :param get_quote_ids: if True, add 'quote_ids': quote ids to dict
    #     :param get_live_dates: if True, add start_live_date: start_live_date, end_live_date: end_live_date to dict
    #     :return:
    #     """
    #
    #     mpan_list_long = self.get_all_ppa_mpans()
    #     dict_out = {}
    #     for mpan_long in mpan_list_long:
    #         if mpan_long != '':
    #             m = MPAN(self.corona_client, mpan_long, start_date=self.start_date, end_date=self.end_date)
    #             m.set_all_info()
    #             if m.ppa_contracts[0].details['load_profile'].lower() == "super peak":
    #                 tech = "Peak"
    #             else:
    #                 tech = m.ppa_contracts[0].details['technology']
    #
    #             info = {'full_mpan': m.full_mpan,
    #                     'technology': tech,
    #                     'site_name': m.site_name,
    #                     'meter_type': m.meter_type,
    #                     'kW': m.ppa_contracts[0].details['capacity_kw'],
    #                     'contracts': m.ppa_contracts}
    #
    #             if get_quote_ids:
    #                 quote_ids = []
    #                 for ppa_contract in m.ppa_contracts:
    #                     quote_ids.append(ppa_contract.details['quote_id'])
    #                 info['quote_ids'] = quote_ids
    #             if get_live_dates:
    #                 m.get_start_live_end_live(m.ppa_contracts)
    #                 info['start_live_date'] = m.start_live_date
    #                 info['end_live_date'] = m.end_live_date
    #
    #             if meter_type is None:
    #                 dict_out[m.mpan] = info
    #             else:
    #                 if m.meter_type.lower() == meter_type.lower():
    #                     dict_out[m.mpan] = info
    #     return dict_out

    def get_all_full_mpans_by_meter_type(self, meter_type=None):
        """
        Get all mpans in a dict with the full mpan the key and the value a dict of
        technology, site name, meter type and kw
        :param meter_type:
        :return:
        """

        mpan_list_long = self.get_all_ppa_mpans()
        dict_out = {}
        for mpan_long in mpan_list_long:
            m = MPAN(self.corona_client, mpan_long, self.start_date, self.end_date)
            m.set_all_info()
            info = {'technology': m.ppa_contracts[0].details['technology'],
                    'site_name': m.site_name,
                    'meter_type': m.meter_type,
                    'kW': m.ppa_contracts[0].details['capacity_kw']}
            if meter_type is None:
                dict_out[m.full_mpan] = info
            else:
                if m.meter_type.lower() == meter_type.lower():
                    dict_out[m.full_mpan] = info

        return dict_out


class PPAContract(object):
    def __init__(self, corona_client, **kwargs):

        self.corona_client = corona_client
        self.details = kwargs
        self.values = {}
        self.pass_throughs = {}
        self.contract_types = {}

        # Reformat quote info
        self.set_quote_info()
        self.set_dates()
        self.set_spill_dates()

    def set_dates(self):
        if 'contract_start_date' in self.details:
            if isinstance(self.details['contract_start_date'], str):
                start_date = datetime.datetime.strptime(
                    self.details['contract_start_date'], '%Y-%m-%d')
                self.details['contract_start_date'] = start_date.date()
        if 'contract_end_date' in self.details:
            if isinstance(self.details['contract_end_date'], str):
                end_date = datetime.datetime.strptime(
                    self.details['contract_end_date'], '%Y-%m-%d')
                self.details['contract_end_date'] = end_date.date()

    def get_quote_info(self):
        if 'quote_id' in self.details:
            params = {
                'quote_id': self.details['quote_id'],
            }
            url = self.corona_client.get_url('ppa-product-quote')
            return requests.get(url, params=params).json()

    def set_quote_info(self):
        quote = self.get_quote_info()
        if quote:
            for item in quote:
                self.values[item['price_type']] = item['value']
                self.pass_throughs[item['price_type']] = item[
                    'pass_through_percent'] / 100.0
                self.contract_types[item['price_type']] = item[
                    'product_quote_type']

    def set_spill_dates(self):
        """
        Adds spill_start and spill_end keys to details. If there is no spill
        period then these fields are set to None. Else they are set to the
        relevant datetime.date() object.
        """
        self.details['spill_start'] = None
        self.details['spill_end'] = None
        if 'spill_period' in self.details:
            if self.details['spill_period']:
                self.details['spill_start'] = self.details[
                    'contract_start_date']
                self.details['spill_end'] = (
                    self.details['contract_start_date'] +
                    relativedelta(days=self.details['spill_period']-1))


class MPAN(CoronaPPAParamsMixin):
    def __init__(self, corona_client, full_mpan, start_date=None, end_date=None,
                 contracted_ppa=True, remove_cancelled_contracts=True):
        """
        :param full_mpan: 21 digit MPAN, str
        :param start_date: start date of query period, datetime.date()
        :param end_date: end date of query period, datetime.date()
        :param contracted_ppa: whether quote/ contract is signed, boolean
        :param remove_cancelled_contracts: if you want to remove cancelled
        contracts, boolean. If False then cancelled contracts are returned.
        """

        self.corona_client = corona_client
        self.full_mpan = full_mpan
        self.mpan = full_mpan[-13:]
        self.start_date = start_date
        self.end_date = end_date
        self.contracted_ppa = contracted_ppa
        self.remove_cancelled_contracts = remove_cancelled_contracts
        self.site_name = None
        self.company_id = None
        self.meter_type = None
        self.ppa_contracts = None
        self.live_ppa_contract = None
        self.billing_details = None
        self.monthly_scalars = None
        self.start_live_date = None  # The minimum start date of all consecutive live contracts
        self.end_live_date = None  # The maximum end_date of all consecutive live contracts
        self.registration_details = None
        self.site_postcode = None
        self.site_latitude = None
        self.site_longitude = None
        self.site_info = None

        # For Corona querying
        self.params = {}

    def get_site_info(self):
        """
        Corona is set up that each Company can have many sites, which
        (I believe) are related or indeed MPANs which is what this class is.

        Therefore on the live_ppa_contract details the site field is an id
        which is linked to the company which in turn is linked to billing
        details, which this function is initially primarily used for.

        :return: site_resp
        """
        if self.live_ppa_contract:
            site_id = self.live_ppa_contract.details['site']
            site_url = self.corona_client.get_url('sites')
            site_url = os.path.join(site_url, str(site_id))
            self.site_info = requests.get(site_url).json()
            return self.site_info

    def set_billing_details(self, site_resp):
        """
        Set the billing details.
        :param site_resp: return value of _get_site_info()

        Response gives a list of dictionaries, but only one billing information
        should exist, so set the first in list as billing_details.
        """
        if site_resp and 'company' in site_resp:
            company_id = site_resp['company']
            billing_url = self.corona_client.get_url('billing-info')
            query_string = "?company={}".format(str(company_id))
            billing_url = os.path.join(billing_url, query_string)
            resp = requests.get(billing_url).json()
            if resp:
                self.billing_details = resp[0]

    def set_registration_details(self):
        """
        Get registration information such as new install flag, go live date
        DC/DA
        :return:
        """
        registration_url = self.corona_client.get_url('registrations')
        query_string = "?mpan={}".format(self.full_mpan)
        registration_url = os.path.join(registration_url, query_string)
        resp = requests.get(registration_url).json()
        if resp:
            self.registration_details = resp[0]

    def set_site_name(self, site_resp):
        if site_resp and 'name' in site_resp:
            self.site_name = site_resp['name']

    def set_company_id(self, site_resp):
        if site_resp and 'company' in site_resp:
            self.company_id = site_resp['company']

    def set_site_postcode(self, site_resp):
        if site_resp and 'addresses' in site_resp:
            if len(site_resp['addresses']) and 'postcode' in site_resp['addresses'][0]:
                self.site_postcode = site_resp['addresses'][0]['postcode']

    def set_lat_lon(self):
        if self.site_postcode is not None:
            location = Nominatim().geocode(self.site_postcode)
            self.site_latitude = location.latitude
            self.site_longitude = location.longitude

    def set_meter_type(self):
        if (self.live_ppa_contract and 'meter_type' in
                self.live_ppa_contract.details):
            if self.live_ppa_contract.details['meter_type'] == "E":
                self.meter_type = 'export'
            else:
                self.meter_type = 'import'

    def set_ppa_contracts(self):
        url = self.corona_client.get_url('ppa-quotes')
        url = url.format('')
        resp = requests.get(url, params=self.params).json()
        self.ppa_contracts = [PPAContract(self.corona_client, **contract) for contract in resp]

    def set_live_ppa_contract(self):
        """
        For now assume that all contracts from Corona are correct and live.

        If multiple contracts exist from get_ppa_contracts for the given
        start_date and end_date, then use the one with highest quote_id i.e.
        latest quote.

        The live_ppa_contract attribute may not accurately represent the true
        'live contract' as if the start_date and end_date contains two
        back-to-back contracts where one ends and the other starts within the
        given period (i.e. starts/ends in the middle of a month for billing)
        then
        """
        if self.ppa_contracts:
            quote_id = 0
            latest_contract = None
            for contract in self.ppa_contracts:
                if (contract.details['quote_id'] and
                        contract.details['quote_id'] > quote_id):
                    quote_id = contract.details['quote_id']
                    latest_contract = contract
            self.live_ppa_contract = latest_contract

    def get_start_live_end_live(self, contracts):
        """
        Get total start and end date of all contracts
        :param contracts:
        :return:
        """

        start_dates = []
        end_dates = []

        for contract in contracts:
            start_dates.append(contract.details['contract_start_date'])
            end_dates.append(contract.details['contract_end_date'])

        self.start_live_date = min(start_dates)
        self.end_live_date = min(end_dates)

        # Finding the end of the contract, to ensure continuity
        for index, contract in enumerate(contracts):
            if contract.details['contract_start_date'] <= self.end_live_date + datetime.timedelta(days=1) and \
                    index != 0:
                self.end_live_date = contract.details['contract_end_date']

    def get_continuous_start_end_live(self, contracts):
        """
        Similar to get_start_live_end_live, but gives start and end of current live period, so accounts for
        time where we have lost the customer
        :param contracts:
        :return:
        """
        if self.live_ppa_contract:
            self.start_live_date = self.live_ppa_contract.details['contract_start_date']
            self.end_live_date = self.live_ppa_contract.details['contract_end_date']
            if len(contracts):
                for index, contract in enumerate(contracts):
                    if contract.details['contract_start_date'] == self.end_live_date + relativedelta(days=1):
                        self.end_live_date = contract.details['contract_end_date']
                    if contract.details['contract_end_date'] == self.start_live_date - relativedelta(days=1):
                        self.start_live_date = contract.details['contract_start_date']

    @staticmethod
    def get_continuous_dates(contract, date_initial, date_final):

        start_contract = contract.details['contract_start_date']
        end_contract = contract.details['contract_end_date']

        start = max(start_contract, date_initial.date())
        end = min(end_contract, date_final.date())

        if end < date_initial.date():
            return None, None
        if start > date_final.date():
            return None, None

        return start, end

    def set_all_info(self):
        self._add_params()
        self.set_ppa_contracts()
        self.set_live_ppa_contract()
        site_resp = self.get_site_info()
        self.set_site_name(site_resp)
        self.set_company_id(site_resp)
        self.set_site_postcode(site_resp)
        # self.set_lat_lon()
        self.set_meter_type()
        self.set_billing_details(site_resp)
        self.set_registration_details()
        self.get_continuous_start_end_live(self.ppa_contracts)
