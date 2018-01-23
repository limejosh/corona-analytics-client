from corona_analytics_client.access_company import Company
from lj_clients.clients import CoronaClient


def set_company_info_name():

    company_name = 'JJ Power Limited'
    corona_client = CoronaClient('prod')

    company = Company(corona_client, name=company_name)
    company.set_company_info()
    print(company)


def set_company_info_id():

    company_id = 4
    corona_client = CoronaClient('prod')

    company = Company(corona_client, company_id=company_id)
    company.set_company_info()
    print(company)

if __name__ == "__main__":
    set_company_info_name()
    set_company_info_id()
