from setuptools import setup

setup(
    name='feel_rested',
    version='0.1',
    url='https://github.com/FeelRobotics/FeelRested',
    packages=['feel_rested'],
    include_package_data=True,
    description='Quick build a flexible REST API',
    install_requires=['djangorestframework'],
)
