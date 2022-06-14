from setuptools import find_packages, setup

install_requires = [
    'fastjsonschema',
    'xmltodict',
    'requests===2.27.1'
]

flask_requires = [
    'flask===2.0.1', 'flask_restful===0.3.9', 'flask-restx===0.5.0',  # to create Flask server
    'gevent===21.8.0', 'greenlet===1.1.1',  # to run flask server
    'werkzeug===2.0.1',
]

extra_requires = ['botocore', 'boto3',]

setup(
    name="cumulus_lambda_functions",
    version="1.4.5",
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=['mock', 'nose', 'sphinx', 'sphinx_rtd_theme', 'coverage'],
    test_suite='nose.collector',
    author=['Wai Phyo'],
    author_email=['wai.phyo@jpl.nasa.gov'],
    license='NONE',
    include_package_data=True,
    python_requires="==3.7",
    entry_points={
    }
)
