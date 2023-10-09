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
    'python-dotenv'
]

flask_requires = [
    'flask===2.0.1', 'flask_restful===0.3.9', 'flask-restx===0.5.0',  # to create Flask server
    'gevent===21.8.0', 'greenlet===1.1.1',  # to run flask server
    'werkzeug===2.0.1',
]

extra_requires = ['botocore', 'boto3',]

setup(
    name="cumulus_lambda_functions",
    version="5.5.5",
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=['mock', 'nose', 'sphinx', 'sphinx_rtd_theme', 'coverage', 'pystac', 'python-dotenv', 'jsonschema'],
    test_suite='nose.collector',
    author=['Wai Phyo'],
    author_email=['wai.phyo@jpl.nasa.gov'],
    license='NONE',
    include_package_data=True,
    python_requires="==3.9",
    entry_points={
    }
)
