from setuptools import setup

setup(
    name='nsides',
    packages=['nsides'],
    include_package_data=True,
    install_requires=[
        'pymysql',
        'pymongo',
        'flask',
        'Flask-PyMongo',
        'flask-login'
    ]
)
