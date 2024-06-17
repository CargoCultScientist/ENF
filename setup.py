from setuptools import setup, find_packages

setup(
    name='enf',
    version='0.1.0',
    packages=find_packages(
        include=['enf', 'enf.*'],
        exclude=['cache', 'plots']
    ),
    install_requires=[
        'requests~=2.31.0',
        'numpy~=1.23.0',
        'pandas~=2.2.2',
        'matplotlib~=3.8.4',
        'stumpy~=1.12.0',
        'scipy~=1.13.0',
        'joblib==1.4.2'
    ],
    author='Ricardo Dodds',
    author_email='ricdodds@fellow.bellingcat.com',
    description='ENF analysis tools',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ricdodds/enf',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
