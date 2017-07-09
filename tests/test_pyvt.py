from unittest import TestCase
from unittest.mock import patch
from bs4 import BeautifulSoup
from pyvt import Timetable, TimetableError, Section


class TestTimetableHelpers(TestCase):

    def setUp(self):
        self.timetable = Timetable()

    @patch('pyvt.Timetable._parse_row')
    def test_parse_table_single_entry(self, mock_row):
        with open('./tests/test_data/test_crn_request_table.html', 'r') as file:
            bs = BeautifulSoup(file.read(), 'html.parser')
            self.timetable._parse_table(bs)
            mock_row.assert_called_once()

    @patch('pyvt.Timetable._parse_row')
    def test_parse_table_no_results(self, mock_row):
        with open('./tests/test_data/test_table_no_results.html', 'r') as file:
            table = BeautifulSoup(file.read(), 'html.parser')
            self.assertIsNone(self.timetable._parse_table(table))
            mock_row.assert_not_called()

    @patch('pyvt.Timetable._parse_row')
    def test_parse_table_multiple_results(self, mock_row):
        with open('./tests/test_data/test_class_lookup_multiple_results.html', 'r') as file:
            html = BeautifulSoup(file.read(), 'html.parser')
            self.timetable._parse_table(html)
            self.assertEqual(3, mock_row.call_count)

    def test_parse_row_simple(self):
        with open('./tests/test_data/test_row.html', 'r') as file:
            row = BeautifulSoup(file.read(), 'html.parser')
            data = self.timetable._parse_row(row)
            c = Section(crn='17583', code='STAT 4705', name='Statistics for Engr', lecture_type='L',
                        credits='3', capacity='60', instructor='GR Terrell',
                        days='T R', start_time='9:30AM', end_time='10:45AM', location='WMS 220', exam_type='09T')
            self.assertEqual(c, data)

    @patch('requests.post')
    def test_make_request_bad_status(self, mock_post):
        mock_post.return_value.status_code = 400
        with self.assertRaises(TimetableError):
            self.timetable._make_request({'dummy': 'data'})
        self.assertEqual(2, self.timetable.sleep_time)

    @patch('requests.post')
    def test_make_request_simple(self, mock_post):
        mock_post.return_value.content = '<html></html>'
        mock_post.return_value.status_code = 200
        self.assertTrue(isinstance(self.timetable._make_request({'dummy': 'data'}), BeautifulSoup))

    @patch('pyvt.datetime')
    def test_default_term_year(self, mock_date):
        mock_date.today.return_value.year = 2017
        mock_date.today.return_value.month = 1
        self.assertEqual('201701', self.timetable._default_term_year)

    @patch('pyvt.datetime')
    def test_default_term_year_in_between_terms(self, mock_date):
        mock_date.today.return_value.year = 2017
        mock_date.today.return_value.month = 3
        self.assertEqual('201701', self.timetable._default_term_year)

    @patch('requests.post')
    def test_timetable_error_growth(self, mock_post):
        mock_post.return_value.status_code = 404
        for i in range(10):
            try:
                self.timetable._make_request({'dummy': 'data'})
            except TimetableError:
                continue
        self.assertEqual(1024, self.timetable.sleep_time)

    @patch('requests.post')
    def test_timetable_error_thrown_message(self, mock_post):
        mock_post.return_value.status_code = 404
        try:
            self.timetable._make_request({'dummy': 'data'})
        except TimetableError as e:
            self.assertEqual('The VT Timetable is down or the request was bad. Status Code was: 404'
                             , str(e))


class TestTimetableLookups(TestCase):

    def setUp(self):
        self.timetable = Timetable()

    def test_refined_lookup_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.timetable.refined_lookup(crn_code='17')
        with self.assertRaises(ValueError):
            self.timetable.refined_lookup(class_number='100')
        with self.assertRaises(ValueError):
            self.timetable.refined_lookup(class_number='1000')

    @patch('pyvt.Timetable._make_request')
    @patch('pyvt.Timetable._parse_table')
    def test_refined_lookup_full_request(self, mock_parse, mock_request):
        mock_parse.return_value = []
        mock_request.return_value = '<html></html>'
        request = {'crn_code': '17583', 'subject_code': 'STAT', 'class_number': '4705',
                   'cle_code': 'AR%'}
        self.timetable.refined_lookup(**request)
        called_request = {
            'crn': '17583',
            'subj_code': 'STAT',
            'CRSE_NUMBER': '4705',
            'CORE_CODE': 'AR%',
            'open_only': 'on',
            'TERMYEAR': '201701'
        }
        called_request.update(self.timetable.base_request)
        mock_request.assert_called_once()

    @patch('pyvt.Timetable._make_request')
    @patch('pyvt.Timetable._parse_table')
    def test_refined_lookup_return_values(self, mock_parse, mock_request):
        mock_parse.return_value = []
        mock_request.return_value = ''
        self.assertIsNone(self.timetable.refined_lookup(crn_code='17583'))
        mock_parse.return_value = None
        self.assertIsNone(self.timetable.refined_lookup(crn_code='17583'))
        mock_parse.return_value = [Section(), Section()]
        self.assertEqual(2, len(self.timetable.refined_lookup('17583')))

    @patch('pyvt.Timetable.refined_lookup')
    def test_crn_lookup_call_args(self, mock_lookup):
        self.timetable.crn_lookup('17583', None, False)
        args = {'crn_code': '17583', 'open_only': False, 'term_year': None}
        mock_lookup.assert_called_once_with(**args)

    @patch('pyvt.Timetable.refined_lookup')
    def test_crn_lookup_return_values(self, mock_lookup):
        mock_lookup.return_value = None
        self.assertIsNone(self.timetable.crn_lookup('17583'))
        mock_lookup.return_value = [Section()]
        self.assertTrue(isinstance(self.timetable.crn_lookup('17583'), Section))

    @patch('pyvt.Timetable.refined_lookup')
    def test_class_lookup_args(self, mock_lookup):
        self.timetable.class_lookup('STAT', '4705', None, False)
        mock_lookup.assert_called_once_with(subject_code='STAT', class_number='4705', term_year=None, open_only=False)

    @patch('pyvt.Timetable.refined_lookup')
    def test_cle_lookup_args(self, mock_lookup):
        self.timetable.cle_lookup('AR01', None, False)
        mock_lookup.assert_called_once_with(cle_code='AR01', term_year=None, open_only=False)

    @patch('pyvt.Timetable.refined_lookup')
    def test_subject_lookup_args(self, mock_lookup):
        self.timetable.subject_lookup('STAT', None, False)
        mock_lookup.assert_called_once_with(subject_code='STAT', term_year=None, open_only=False)


class TestSection(TestCase):

    def setUp(self):
        self.section1 = Section(crn='17583', code='STAT 4705', name='Statistics for Engr', lecture_type='L',
                               credits='3', capacity='60', instructor='GR Terrell',
                               days='T R', start_time='9:30AM', end_time='10:45AM', location='WMS 220',
                               exam_type='09T')

        self.section2 = Section(crn='17583', code='STAT 4705', name='Statistics for Engr', lecture_type='L',
                                credits='3', capacity='60', instructor='GR Terrell',
                                days='T R', start_time='9:30AM', end_time='10:45AM', location='WMS 220',
                                exam_type='09T')

        self.section3 = Section(crn='17584', code='MATH 2214', name='Intro Diff Equations', lecture_type='L',
                                credits='3', capacity='66', instructor='ER Rappold',
                                days='M W', start_time='4:00PM', end_time='5:15PM', location='GOODW 135',
                                exam_type='CTE')

    def test_section_str(self):
        self.assertEqual("Statistics for Engr (17583) on T R at (9:30AM, 10:45AM)", str(self.section1))

    def test_section_eq(self):
        self.assertEqual(self.section1, self.section2)

    def test_section_ne1(self):
        self.assertNotEqual(self.section1, self.section3)

    def test_section_ne2(self):
        self.assertNotEqual("Junk", self.section1)

    def test_section_repr(self):
        self.assertEqual("Intro Diff Equations (17584) on M W at (4:00PM, 5:15PM)", repr(self.section3))

    def test_section_hash(self):
        self.assertEqual(17583, hash(self.section1))


class TestTimetableError(TestCase):

    def setUp(self):
        self.e = TimetableError("Test", 1)

    def test_timetable_unavailable_message(self):
        self.assertEqual("Test", str(self.e))

    def test_timetable_unavailable_exception_sleep_time(self):
        self.assertEqual(1, self.e.sleep_time)
