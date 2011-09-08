#!/usr/bin/env python
# -*- coding: utf-8
"""
Transform script.

This will strip everything but asterisks and numbers from the ssn-field.
If other charachters should remain they should be added to
``characters_in_ssn`` below.
"""

# Configuration
"""
Valid charachters in SSN. These are not stripped from the SSN-field.
Beware that only the last 10 characters are saved to the output-file
after invalid characters are removed.
"""
valid_characters_in_ssn = '*0123456789T'

## Input
"""
Input encoding, should probably be utf-16 since that autodetects both
utf-16le and utf-16be. (Excel uses utf-16le)
I've tried this and at least the mailed file worked with utf-16.
"""
input_encoding = 'utf-16'

"""
Input dialect. The CSV-dialect of the input file
"""
input_dialect = 'excel-tab'

## Output
"""
Encoding for output, should probably be latin-1. (Excel uses utf-16le)
"""
output_encoding = 'latin-1'

"""
Output dialect. The CSV-dialect of the output file.
"""
output_dialect = 'excel-tab'

"""
Output qouting. The default is 'ALL' which adds "" around all fields.
"""
output_quoting = 'ALL'


# The script, you probably don't want to edit below this line ################
# Imports {{{1
import re
import csv,sys,os,codecs,cStringIO

# Helpers {{{1
def _handle_ssn(value): #{{{2
	"""Extracts the last 10 digits from value"""
	return re.sub(r"[^%s]"%valid_characters_in_ssn,"", value)[-10:].ljust(10,'0')

def _handle_zip(value): #{{{2
	"""Extracts tha last 5 digits"""
	return re.sub(r"[^\d]","", value)[-5:]

class Entry: #{{{1
	"""Represents an entry in a datafile"""
	FIELD_ORDER_DICT = { #{{{2
		"ssn" : 0,
		"firstname" : 1,
		"lastname" : 2,
		"co" : 3,
		"address" : 4,
		"zip_code" : 5,
		"city" : 6,
		"country" : 7,
		"phone" : 8,
		"email" : 9,
		"program" : 10
	}

	FIELD_ORDER_ARRAY = [ #{{{2
		"ssn", "firstname", "lastname", "co", "address",
		"zip_code", "city", "country", "phone", "email",
		"program"
	]
	
	UPPER_FIELDS = [ #{{{2
			"firstname","lastname","address","co","city","country","program"
			]
	
	LOWER_FIELDS = [ #{{{2
			"email"
			]
	
	REQUIRED_FIELDS = []

	def __init__(self,*args,**kwargs): #{{{2
		if 0 < len(args):
			for key in self.FIELD_ORDER_DICT.iterkeys():
				self.__setattr__(key, args[self.FIELD_ORDER_DICT[ key ]])
		for key in kwargs.iterkeys():
			self.__setattr__(key, args[self.FIELD_ORDER_DICT[ key ]])

	def __setattr__(self, name, value): #{{{2
		if name in self.UPPER_FIELDS:
			self.__dict__[name] = value.upper()
		elif name in self.LOWER_FIELDS:
			self.__dict__[name] = value.lower()
		elif "ssn" == name:
			self.__dict__[name] = _handle_ssn(value)
		elif "zip_code" == name:
			self.__dict__[name] = _handle_zip(value)
		else:
			self.__dict__[name] = value
	
	def as_array(self): #{{{2
		order = self.FIELD_ORDER_ARRAY
		return [self.__dict__[v] for v in order]

	def is_valid(self): #{{{2
		valid = True
		for key in self.REQUIRED_FIELDS:
			valid = valid and (0 < len(self.__dict__[key]))
		return valid

	def __unicode__(self): #{{{2
		return u"\t".join([u'"%s"' % v for v in self.as_array()])

class UTF8Recoder: #{{{1
	"""
	Iterator that reads an encoded stream and reencodes the input to UTF-8
	"""
	def __init__(self, f, encoding):
		self.reader = codecs.getreader(encoding)(f)

	def __iter__(self):
		return self

	def next(self):
		return self.reader.next().encode("utf-8")

class UnicodeReader: #{{{1
	"""
	A CSV reader which will iterate over lines in the CSV file "f",
	which is encoded in the given encoding.
	"""

	def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
		f = UTF8Recoder(f, encoding)
		self.reader = csv.reader(f, dialect=dialect, **kwds)

	def next(self):
		row = self.reader.next()
		return [unicode(s, "utf-8") for s in row]

	def __iter__(self):
		return self

class UnicodeWriter: #{{{1
	"""
	A CSV writer which will write rows to CSV file "f",
	which is encoded in the given encoding.
	"""

	def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
		# Redirect output to a queue
		self.queue = cStringIO.StringIO()
		self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
		self.stream = f
		self.encoder = codecs.getincrementalencoder(encoding)()

	def writerow(self, row):
		self.writer.writerow([s.encode("utf-8") for s in row])
		# Fetch UTF-8 output from the queue ...
		data = self.queue.getvalue()
		data = data.decode("utf-8")
		# ... and reencode it into the target encoding
		data = self.encoder.encode(data)
		# write to the target stream
		self.stream.write(data)
		# empty queue
		self.queue.truncate(0)

	def writerows(self, rows):
		for row in rows:
			self.writerow(row)

def usage(scriptname): #{{{1
	print >> sys.stderr, "A really simple transform script"
	print >> sys.stderr
	print >> sys.stderr, "usage: %s <inputfile> [outputfile]" % scriptname
	print >> sys.stderr
	print >> sys.stderr, "\tTransforms a TSV-file to uppercase and cleans out a few stray characters"
	print >> sys.stderr, "\tThis script will overwrite the outfile without confirmation"

if __name__ == '__main__': #{{{1
	if len(sys.argv) < 2:
		usage(sys.argv[0])
		sys.exit(-1)
	filename = sys.argv[1]
	if len(sys.argv) > 2:
		outfile = sys.argv[2]
	else:
		outfile,_ = os.path.splitext(filename)
		outfile += '.txt'
	
	if not os.access(filename, os.R_OK):
		print >> sys.stderr, "%s is not a readable file" % filename
	
	# Input is most likely utf-16le but let the codex deal with BOM and such
	reader = UnicodeReader(open(filename,'rb'), dialect=input_dialect, encoding=input_encoding)
	# Output is a little bit trickier
	output = open(outfile,'wb')
	if('utf-16le' == output_encoding):
		output.write(codecs.BOM_UTF16_LE)
	elif('utf-16be' == output_encoding):
		output.write(codecs.BOM_UTF16_BE)
	quoting = getattr(csv,'QUOTE_%s'%output_quoting,csv.QUOTE_ALL)
	writer = UnicodeWriter(output, dialect=output_dialect, quoting=quoting, encoding=output_encoding)

	print >> sys.stderr, "Converting from: %-50s[%8s]" % (filename,input_encoding)
	print >> sys.stderr, "             to: %-50s[%8s]" % (outfile,output_encoding)
	# Discard three lines from input
	reader.next()
	reader.next()
	reader.next()

	entry_count = 0
	# Comence!
	for row in reader:
		e = Entry(*row)
		writer.writerow( e.as_array() )
		entry_count += 1
	
	output.close()
	print >> sys.stderr, '"Successfully" converted %d entries...' % entry_count

