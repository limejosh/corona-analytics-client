#PYTHONPATH=. py.test --cov-config .coveragerc --cov corona_analytics_client --cov-report html --junitxml result.xml -s -k 'not test_requirements.txt'
PYTHONPATH=. make -C docs html
