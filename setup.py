from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name='agent_Job_scheduler',
    version='0.0.10',
    packages=['agent'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
    ],
    url='https://github.com/MohammadRezaG/agent',
    license='Apache License 2.0',
    author='Mohammad Reza Golsorkhi',
    author_email='Mgol2077@outlook.com',
    description='agent is a python job scheduler',
    long_description=readme(),
    keywords='funniest joke comedy flying circus',
    test_suite='nose.collector',
    tests_require=['nose'],
    include_package_data=True
)
