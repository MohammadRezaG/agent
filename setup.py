from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name='agent_Job_scheduler',
    version='0.2.1.dev5',
    packages=['agent'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.9',
    ],
    keywords='tasks jobs periodic task interval periodic_job periodicjob flask style decorator agent job scheduler time agent_Job agent_Job_scheduler',

    project_urls={
        'Documentation': 'https://github.com/MohammadRezaG/agent/wiki',
        'Source': 'https://github.com/MohammadRezaG/agent',
        'Tracker': 'https://github.com/MohammadRezaG/agent/issues',
    },
    install_requires=[
    ],
    license='Apache License 2.0',
    author='Mohammad Reza Golsorkhi',
    author_email='Mgol2077@outlook.com',
    description='agent is a python job scheduler',
    long_description=readme(),
    python_requires='>=3.8',
    test_suite='nose.collector',
    tests_require=['nose'],
    include_package_data=True,
    zip_safe=True
)
