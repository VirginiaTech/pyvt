from setuptools import setup, find_packages

setup(
    name='py-vt',
    description='A Python API for the Virginia Tech Timetable of Classes',
    version='0.0.7',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6'
    ],
    keywords='Virgina Tech Timetable API',
    packages=find_packages(),
    install_requires=[
        'beautifulsoup4==4.7.1',
        'requests==2.21.0'
    ]
)