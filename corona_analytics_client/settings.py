LIMEJUMP_ENV = 'dev'

CORONA_SUPER_TOKENS = {'local': 'w7818hISDW970y3ZWvZF3r7626Q4OYFM',
                       'dev': 'w7818hISDW970y3ZWvZF3r7626Q4OYFM',
                       'preprod': 'L9nbBNSAPksGAhF7Dw13Ri9ihDLT1W4X',
                       'prod': '207202O372yd32I49u9b52Ge4s143viv'}

corona_config = {
  'host': 'http://corona.limejump.{}:8202/api/'.format(LIMEJUMP_ENV),
  'headers': {"Authorization": CORONA_SUPER_TOKENS[LIMEJUMP_ENV]},
  'token': 'apisupertoken',
}
