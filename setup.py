from setuptools import setup, find_packages

install_requires = [
    'gevent',
    'gevent-openssl',
    'python-decouple',
    'python-dotenv',
    'requests',
    'ujson',
    'azure-mgmt-resource'
]

tests_requires = [
    'pytest',
    'pytest-cov',
    'pytest-pep8',
    'pytest-timeout',
    'pytest-instafail',
    'pytest-vcr',
    'vcrpy',
    'bandit',
    'flake8',
    'coverage',
    'responses',
    'freezegun',
]

dev_requires = [
    'pylint',
    'ipython',
    'autopep8',
    'black',
]

doc_requires = [
    'Sphinx',
    'sphinx_rtd_theme',
]

extras_requires = {
    'tests': tests_requires,
    'dev': dev_requires,
    'doc': doc_requires,
}

setup(
    name='mce-lib-azure',
    version="0.1.0",
    description='MCE - SDK for Azure',
    url='https://github.com/multi-cloud-explorer/mce-lib-azure.git',
    license='GPLv3+',
    packages=find_packages(),
    include_package_data=True, 
    tests_require=tests_requires,
    install_requires=install_requires,
    extras_require=extras_requires,
    test_suite='tests',
    zip_safe=False,
    author='Stephane RAULT',
    author_email="stephane.rault@radicalspam.org",
    python_requires='>=3.7',
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
    entry_points={
        'console_scripts': [
            'mce-az = mce_azure.core:main',
            'mce-az-providers = mce_azure.providers:main'
        ],
    }
)
