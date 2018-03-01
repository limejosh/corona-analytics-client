import datetime

from corona_analytics_client.access_ppa import MPAN
from lj_clients.clients import CoronaClient

from settings import corona_config


def set_all_info_mpan():

    """
    Get information from corona for a specific asset with contract...

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

    mpan:
    -----
    MPAN (21 digits) that you want to get the information from

    str: '008457871300060312681'

    corona_client:
    --------------
    To decide where to look for the information

    corona_client: CoronaClient('prod')

    """
    start = datetime.date(2017, 6, 1)
    end = datetime.date(2017, 6, 30)
    contracted_ppa = True
    remove_cancelled_contracts = False
    mpan = '008457871300060312681'
    mpan = '008457971050001299895'
    mpan = '008450052000054816061'
    corona_client = CoronaClient(base_url=corona_config['host'],
                                 headers=corona_config['headers'],
                                 version=1.0)

    m = MPAN(corona_client, mpan, start, end, contracted_ppa, remove_cancelled_contracts)
    m.set_all_info()
    print(m)


if __name__ == "__main__":
    set_all_info_mpan()
