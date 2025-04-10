from setuptools import find_packages, setup

install_requires = [
    'mdps-ds-lib',
    'urllib3===1.26.11',
    'fastapi',
    'mangum',
    'uvicorn',
    'pygeofilter',
    'python-dotenv'
]

setup(
    name="cumulus_lambda_functions",
    version="9.11.1",
    packages=find_packages(),
    install_requires=install_requires,
    package_data={
        '': ['stac_browser/**/*', 'stac_browser/*'],
    },
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
