from setuptools import setup, find_packages

setup(
    name='toollabs-webservice',
    version='0.1',
    author='Yuvi Panda',
    author_email='yuvipanda@gmail.com',
    license='Apache2',
    packages=find_packages(),
    scripts=[
        'scripts/webservice-runner',
        'scripts/webservice',
        'scripts/deprecated-tomcat-starter',
    ],
    description='Infrastructure for running webservices on tools.wmflabs.org',
    install_requires=[
        'PyYAML',
        'pykube'
    ]
)
