from distutils.core import setup

setup(
    name='IAConnector',
    version='0.1',
    url='https://www.inter-actief.utwente.nl/',
    author='Jan-Jelle Kester',
    author_email='janjelle@jjkester.nl',
    description='OAuth and API consumer for the Inter-Actief web site',
    license='MIT',
    packages=['iaconnector'],
    install_requires=['requests>=2.9,<3', 'requests-oauthlib>=0.6,<0.7'],
)
