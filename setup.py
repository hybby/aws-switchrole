from setuptools import find_packages, setup
import sys


kw = {}

setup(
    name='aws-switchrolel',
    version='0.1',
    author='hybby',
    author_email='dev@fanduel.com',
    url='https://github.com/hybby/aws-switchrole',
    description='aws-switchrole',
    packages=find_packages(),
    install_requires=[
        'awscli>=1.15.25',
        'pyperclip>=1.6.0',
    ],
    include_package_data=True,
    entry_points='''
        [console_scripts]
        aws-switchrole=aws_switchrole.aws_switchrole:main
    ''',
    **kw
)
