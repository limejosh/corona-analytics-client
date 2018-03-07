import requests
import os


class CompanyParamsMixin(object):
    """
    Company Params Mixin
    """
    name = None
    params = {}

    def _add_params(self):
        """
        Following fields which can be queried for companies:
        company name

        Note that company_id doesn't use the params kwarg in requests.get()
        but adds in the company id directly into the url.
        """
        if self.name:
            self.params['name'] = self.name


class ParentCompany(CompanyParamsMixin):
    pass


class Company(CompanyParamsMixin):
    """
    This is the Company level in Corona and mimics the details at that level.
    Not all functionality is present such as Sites, company number or parent
    company but this will be added as soon as Corona is developed.

    So far company name, id and billing details are found given on of the first
    two fields.

    :param corona_client:
    :param str name:
    :param company_id:
    """
    def __init__(self, corona_client, name=None, company_id=None):

        self.corona_client = corona_client
        self.name = name
        self.company_id = company_id
        self.company_number = None
        self.parent_company = None
        self.billing_details = None
        self.sites = []
        self.params = {}

    def get_companies_response(self):
        """
        Depending on what information is given in init, query with id or name.
        :return: corona response
        """
        url = self.corona_client._get_url('companies')
        if self.company_id:
            url = os.path.join(url, str(self.company_id))
            return requests.get(url).json()
        if self.name:
            return requests.get(url, params=self.params).json()[0]

    def get_billing_response(self):
        url = self.corona_client._get_url('billing-info')
        query_string = "?company={}".format(str(self.company_id))
        billing_url = os.path.join(url, query_string)
        return requests.get(billing_url).json()

    def get_site_response(self):
        url = self.corona_client._get_url('sites')
        site_url = os.path.join(url, str(self.company_id))
        return requests.get(site_url).json()

    def set_sites(self):
        pass

    def set_billing_details(self):
        resp = self.get_billing_response()
        if resp:
            self.billing_details = resp[0]

    def set_company_info(self):
        """
        Method to set all the company information. This is the main access
        method to set information.
        """
        self._add_params()
        if self.company_id or self.name:
            resp = self.get_companies_response()
            if resp:
                self.name = resp['name']
                self.company_id = resp['id']
                self.set_billing_details()
                # self.set_sites()
