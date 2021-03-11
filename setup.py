from setuptools import setup, find_packages

setup(
    name='dsaps',
    version='1.0.0',
    description='',
    packages=find_packages(exclude=['tests']),
    author='Eric Hanson',
    author_email='ehanson@mit.edu',
    install_requires=[
        'requests',
        'structlog',
        'attrs',
        'click',
        'lxml',
    ],
    entry_points={
        'console_scripts': [
            'dsaps=dsaps.cli:main',
        ]
    },
    python_requires='>=3.8',
)
