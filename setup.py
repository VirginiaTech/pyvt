from setuptools import setup, find_packages

setup(
    name='py-vt',
    description='A Python API for the Virginia Tech Timetable of Classes',
    version='0.0.5',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6'
    ],
    keywords='Virgina Tech Timetable API',
    packages=find_packages(),
    install_requires=[
        'beautifulsoup4==4.5.1',
        'requests==2.12.4'
    ]
)