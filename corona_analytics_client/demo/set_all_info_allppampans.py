import datetime

from lj_clients.clients import CoronaClient

from corona_analytics_client.access_ppa import AllPPAMPANs
from corona_analytics_client.access_ppa import MPAN
from corona_analytics_client.settings import corona_config


def set_all_info_allppampans():

    """
    Get information from corona for all assets with contract...

    Requirements:
    -------------
    If this script is run outside of the VPC, then you will require a ssh tunnel
    to Corona.

    Inputs:
    -------

    start_date:
    -----------
    Start date of the time period to be checked. Note, it has to be date, not datetime.

    datetime.date: datetime.date(2016, 5, 29)

    end_date:
    ---------
    Start date of the time period to be checked. Note, it has to be date, not datetime.

    datetime.date: datetime.date(2017, 6, 22)

    contracted_ppa:
    ---------------
    Whether you want to include MPANs that have the contracted ppa field in corona set to true or false

    bool

    remove_cancelled_contracts:
    ---------------------------
    Whether you want to include MPANs removed from the list whose contracts have been cancelled in corona

    bool

    corona_client:
    --------------
    To decide where to look for the information

    corona_client: CoronaClient('prod')

    """
    start = datetime.date(2017, 11, 1)
    end = datetime.date(2017, 11, 30)
    contracted_ppa = True
    remove_cancelled_contracts = False
    corona_client = CoronaClient(base_url=corona_config['host'],
                                 headers=corona_config['headers'],
                                 version=1.0)

    all_mpans = AllPPAMPANs(
        corona_client, start, end, contracted_ppa, remove_cancelled_contracts)
    mpan_list = all_mpans.get_all_ppa_mpans()
    mpan_dict = {}
    for mpan in mpan_list:
        m = MPAN(corona_client, mpan, start, end)
        m.set_all_info()
        mpan_dict[mpan] = m
        if m.live_ppa_contract and m.live_ppa_contract.details and m.live_ppa_contract.details['technology']:
            tech_type = m.live_ppa_contract.details['technology']
        else:
            tech_type = None
        print(m.full_mpan + "\t" + str(m.site_name) + '\t' + str(m.site_postcode) + '\t' + str(tech_type))

    print(mpan_dict)


if __name__ == "__main__":
    set_all_info_allppampans()
