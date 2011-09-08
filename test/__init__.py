# -*- coding: utf-8
import unittest
from copy import copy

from transform import Entry

class TestEntry(unittest.TestCase): #{{{1
	input = [
		u"1701019999",u"ANNA",u"ANDREASSON",
		u"C/O ARNE PERSSON",u"FEJKGATAN 11A",u"12345",u"ÅSTAD",
		u"SVERIGE",u"5555555555",u"fajk_mail-plupp@snutt.plutt.com",
		u"TYCIE"
	]
	output = {
		'ssn'      : u"1701019999",
		'firstname': u"ANNA",
		'lastname' : u"ANDREASSON",
		'co'       : u"C/O ARNE PERSSON",
		'address'  : u"FEJKGATAN 11A",
		'zip_code' : u"12345",
		'city'     : u"ÅSTAD",
		'country'  : u"SVERIGE",
		'phone'    : u"5555555555",
		'email'    : u"fajk_mail-plupp@snutt.plutt.com",
		'program'  : u"TYCIE"
	}
	def test_000_initializer_should_be_sane(self): #{{{2
		self.assertIsNotNone(Entry())
	
	def test_003_after_creating_entry_fields_should_reflect_initial_data(self): #{{{2
		result = Entry(*self.input)
		self.assertEqual(self.output['firstname'], result.firstname)
		self.assertEqual(self.output['lastname'], result.lastname)
		self.assertEqual(self.output['ssn'], result.ssn)
		self.assertEqual(self.output['co'], result.co)
		self.assertEqual(self.output['address'], result.address)
		self.assertEqual(self.output['zip_code'], result.zip_code)
		self.assertEqual(self.output['city'],result.city)
		self.assertEqual(self.output['country'],result.country)
		self.assertEqual(self.output['phone'],result.phone)
		self.assertEqual(self.output['email'],result.email)
		self.assertEqual(self.output['program'],result.program)
	
	def test_004_entry_should_handle_lower_case_fields(self): #{{{2
		input = copy(self.input)
		input[Entry.FIELD_ORDER_DICT['firstname']] = input[Entry.FIELD_ORDER_DICT['firstname']].lower()
		input[Entry.FIELD_ORDER_DICT['lastname']]  = input[Entry.FIELD_ORDER_DICT['lastname']].lower()
		input[Entry.FIELD_ORDER_DICT['co']]        = input[Entry.FIELD_ORDER_DICT['co']].lower()
		input[Entry.FIELD_ORDER_DICT['address']]   = input[Entry.FIELD_ORDER_DICT['address']].lower()
		input[Entry.FIELD_ORDER_DICT['city']]      = input[Entry.FIELD_ORDER_DICT['city']].lower()
		input[Entry.FIELD_ORDER_DICT['country']]   = input[Entry.FIELD_ORDER_DICT['country']].lower()
		input[Entry.FIELD_ORDER_DICT['program']]   = input[Entry.FIELD_ORDER_DICT['program']].lower()

		result = Entry(*input)
		self.assertEqual(self.output['firstname'], result.firstname)
		self.assertEqual(self.output['lastname'], result.lastname)
		self.assertEqual(self.output['co'], result.co)
		self.assertEqual(self.output['address'], result.address)
		self.assertEqual(self.output['city'],result.city)
		self.assertEqual(self.output['country'],result.country)
		self.assertEqual(self.output['program'],result.program)
	
	def test_005_entry_should_handle_ssn_with_dash(self): #{{{2
		input = copy(self.input)
		input[Entry.FIELD_ORDER_DICT['ssn']] = u"170101-9999"
		result = Entry(*input)
		self.assertEqual(u"1701019999", result.ssn)
	
	def test_006_entry_should_handle_ssn_with_10_numbers(self): #{{{2
		input = copy(self.input)
		input[Entry.FIELD_ORDER_DICT['ssn']] = u"19170101-9999"
		result = Entry(*input)
		self.assertEqual(u"1701019999", result.ssn)
	
	def test_007_entry_should_handle_many_strange_characters(self): #{{{2
		data = [
				u"",
				u"áóúéíý àòùèì",
				u"äöüëïÿ âôûêîû",
				u"ãõñç",u"",u"",
				u"",u"",u"",u"",u""
			]
		result = Entry(*data)
		self.assertEqual(u"ÁÓÚÉÍÝ ÀÒÙÈÌ", result.firstname)
		self.assertEqual(u"ÄÖÜËÏŸ ÂÔÛÊÎÛ", result.lastname)
		self.assertEqual(u"ÃÕÑÇ", result.co)
	
	def test_008_entry_should_handle_spaces_and_characters_in_zip(self): #{{{2
		input = copy(self.input)
		input[Entry.FIELD_ORDER_DICT['zip_code']] = u"SE-123 45"

		result = Entry(*input)

		self.assertEqual(u"12345", result.zip_code)
	
	def test_009_entry_should_handle_funny_asterisks_in_ssn(self): #{{{2
		input = copy(self.input)
		input[Entry.FIELD_ORDER_DICT['ssn']] = u"19170101-1*34"

		result = Entry(*input)
		self.assertEqual(u"1701011*34", result.ssn)
	
	def test_010_entry_should_handle_empty_ssn(self): #{{{2
		input = copy(self.input)
		input[Entry.FIELD_ORDER_DICT['ssn']] = u"-"
		result = Entry(*input)
		self.assertEqual(u"0000000000", result.ssn)
	
	def test_011_entry_should_convert_to_string_nicely(self): #{{{2
		result = unicode(Entry(*self.input))
		expected = u'"1701019999"\t"ANNA"\t"ANDREASSON"\t"C/O ARNE PERSSON"\t"FEJKGATAN 11A"\t"12345"\t"ÅSTAD"\t"SVERIGE"\t"5555555555"\t"fajk_mail-plupp@snutt.plutt.com"\t"TYCIE"'
		self.assertEqual(expected, result)
	
	def test_012_entry_should_downcase_email(self): #{{{2
		input = copy(self.input)
		input[Entry.FIELD_ORDER_DICT['email']] = u"FAJK_MAIL-plupp@SNUTT.plutt.com"

		result = Entry(*input)
		self.assertEqual(u"fajk_mail-plupp@snutt.plutt.com", result.email)

	def test_013_entry_should_handle_strange_ssn_with_t_in_it(self): #{{{2
		input = copy(self.input)
		input[Entry.FIELD_ORDER_DICT['ssn']] = u"19170101-T090"
		result = Entry(*input)
		self.assertEqual(u"170101T090", result.ssn)
		
	def test_014_entry_should_be_valid(self): #{{{2
		result = Entry(*self.input)
		self.assertTrue(result.is_valid())
	
	def test_015entry_should_pad_ssn_with_zeroes(self): #{{{2
		input = copy(self.input)
		input[Entry.FIELD_ORDER_DICT['ssn']] = u"170101-090"
		result = Entry(*input)
		self.assertEqual(u"1701010900", result.ssn)
