# pyvt

[![Coverage Status](https://coveralls.io/repos/github/kevincianfarini/pyvt/badge.svg?branch=master)](https://coveralls.io/github/kevincianfarini/pyvt?branch=master)
[![Build Status](https://travis-ci.org/kevincianfarini/pyvt.svg?branch=master)](https://travis-ci.org/kevincianfarini/pyvt)
[![PyPI version](https://badge.fury.io/py/py-vt.svg)](https://badge.fury.io/py/py-vt)


A Virginia Tech Timetable of Classes Python API

### Installation

```shell
pip install py-vt
```

### Usage

Import the Timetable
```python
from pyvt import Timetable
```

The API provides access to the Timetable through a Timetable object.

```python
timetable = Timetable()
```

The timetable object provides some useful methods for pulling data from the VT Timetable.

```python
timetable.crn_lookup('17583', term_year='201701', open_only=False)
```

returns the class section object from the timetable with the CRN 17583 in the term year `201701`, regardless of whether or not the class is full to capacity. Alternatively if you would like to only find sections that are open:

```python
timetable.crn_lookup('17583', term_year='201701')
```

All methods of the timetable provide a default argument of ```open_only=True``` and ```term_year=None``` when making timetable requests. Upon a lookup, if term year is None it will be defaulted to the most recent term year. There is more on this in the Term Year section.

Some of the other most commonly used lookup methods are as follows:

```python

def crn_lookup(self, crn_code, term_year=None, open_only=True):
    ...
```
```crn_lookup(...)``` will return either a single ```Section(...)``` object or ```None``` depending on the success of the query. None is returned if there were no available class sections based of the arguments.

The following methods return either a list of ```Section(...)``` objects or ```None``` depending on the success of the query.

```python
def class_lookup(self, subject_code, class_number, term_year=None, open_only=True):
    ...

def cle_lookup(self, cle_code, term_year=None, open_only=True):
    ...

def subject_lookup(self, subject_code, term_year=None, open_only=True):
    ...
```

More refined searches can be accomplished using the ```refined_lookup(...)``` method

```python
def refined_lookup(self, crn_code=None, subject_code=None, class_number=None, cle_code=None, term_year=None, open_only=True):
```

### Usage Codes

Some of the codes that need to be used with this API are solely to satisfy the needs of the VT Timetable posts. Some helpful codes are as follows.

```python
len(crn_code) >= 3

subj_codes = [
    'STAT',
    'MATH',
    'CS',
    'ECE',
    ...
]

len(class_number) == 4

cle_codes = {
    'AR%': 'All Curriculums',
    'AR01': 'Area 1 Classes',
    'AR02': 'Area 2 Classes',
    ...
    'AR07': 'Area 7 Classes'
}
```

### The Term Years

The Virginia Tech Timetable offers class section lookups for specific term years. If you would like to work with the current term year, you can leave ```term_year=None``` untouched in the timetable method calls. Upon making the request, the term year will be defaulted to be the most recent term year.
Term years happen each year in the months August, January, June, and July. A default term year call in March would result in returning class sections for the last active term year, which is in January. The Spring semester. This is to avoid making calls to the VT Timetable with term years that are not yet available.

Alternatively, if you know that a certain term year is available but not the default, you can pass in a term year to the lookup methods. Term years follow a simple YYYYMM pattern as shown:

```python
term_years = {
    'Spring 2017':      '201701',
    'Summer I 2017':    '201706',
    'Summer II 2017':   '201707',
    'Fall 2017':        '201709',
    ...
}
```

### The Section Object

Class sections returned from the timetable come in the form of a ```Section()``` object. All Section objects have the follows properties:

```python
section_attrs = ['crn', 'code', 'name', 'lecture_type', 'credits', 'capacity', 'instructor', 'days', 'start_time', 'end_time', 'location', 'exam_type']
```

Either a single section object or a list of section objects will be returned to you upon a successful query to the VT Timetable. You can access information about class sections from the above attributes.

### The TimetableError

A Timetable error is thrown when either a bad request is made or the VT Timetable is down. In effect, when the status code of the request is not 200. The thrown error can be used to try and gracefully fail to an extent. The TimetableError provides a ```sleep_time``` attribute to allow for a runtime pause.

```python
from pyvt import TimetableError

try:
    timetable.crn_lookup(...)
except TimetableError as e:
    time.sleep(e.sleep_time)
```

The idea behind this is that if the request was bad, your program will sleep for a short amount of time. However if the VT Timetable is down, and multiple successive ```TimetableErrors``` are raised, then ```sleep_time``` grows exponentially to avoid overwhelming the server.
