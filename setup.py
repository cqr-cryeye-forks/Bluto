from setuptools import setup

setup(
    name='Bluto',
    version='3.0.1',
    author='Mykola Borshchov',
    author_email='nickolaiborshchov@gmail.com',
    url='https://github.com/cqr-cryeye-forks/Bluto',
    packages=['Bluto'],
    include_package_data=True,
    license='LICENSE.txt',
    description='''
    DNS Recon | Brute Forcer | DNS Zone Transfer | DNS Wild Card Checks
    DNS Wild Card Brute Forcer | Email Enumeration | Staff Enumeration
    Compromised Account Checking''',
    long_description=open('README.md').read(),
    scripts=['Bluto/bluto'],
    install_requires=[
        "docopt",
        "dnspython",
        "termcolor",
        "BeautifulSoup4",
        "requests[security]",
        "pythonwhois",
        "lxml",
        "oletools",
        "pdfminer"
    ],
)
