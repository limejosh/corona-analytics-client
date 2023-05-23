from setuptools import setup, find_packages
import re


def find_version(fname):
    """Attempts to find the version number in the file names fname.
    Raises RuntimeError if not found.
    """
    version = ''
    with open(fname, 'r') as fp:
        reg = re.compile(r'__version__ = [\'"]([^\'"]*)[\'"]')
        for line in fp:
            m = reg.match(line)
            if m:
                version = m.group(1)
                break
    if not version:
        raise RuntimeError('Cannot find version information')
    return version


__version__ = find_version('corona_analytics_client/__init__.py')



setup(
    name='corona_analytics_client',
    version=__version__,
    description='corona_analytics_client.',
    install_requires=['lj_clients==1.0.3', 'requests==2.31.0', 'geopy==1.11.0'],
    author='Limejump',
    author_email='tech@limejump.com',
    packages=find_packages(),
)
