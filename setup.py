from setuptools import setup, find_packages

setup(name='personalsite',
    version='1.0',
    description='Source for richwareham.com',
    author='Rich Wareham',
    author_email='rich@richwareham.com',
    url='https://www.richwareham.com/',
    packages=find_packages(),
    install_requires=[
        'Flask',
        'sqlalchemy',
        'flask-oauthlib',
        'docopt',
    ],
)
