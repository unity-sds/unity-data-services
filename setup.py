from setuptools import find_packages, setup

install_requires = [
    'elasticsearch===7.13.4',
    'urllib3===1.26.11',
    'requests_aws4auth',
    'requests===2.31.0',
    'pystac', 'jsonschema',
    'fastjsonschema',
    'xmltodict',
    'tenacity',
    'fastapi',
    'mangum',
    'uvicorn',
    'requests',
    'pygeofilter',
    'python-dotenv'
]

extra_requires = ['botocore', 'boto3',]

setup(
    name="cumulus_lambda_functions",
    version="6.4.1",
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=['mock', 'nose', 'sphinx', 'sphinx_rtd_theme', 'coverage', 'pystac', 'python-dotenv', 'jsonschema', 'pytest-mock'],
    test_suite='nose.collector',
    author=['Wai Phyo'],
    author_email=['wai.phyo@jpl.nasa.gov'],
    license='NONE',
    include_package_data=True,
    python_requires="==3.9",
    entry_points={
    }
)
