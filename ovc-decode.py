#!/usr/bin/env python
#
# OV-chipkaart decoder: main program
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#        
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License at http://www.gnu.org/licenses/gpl.txt
# By using, editing and/or distributing this software you agree to
# the terms and conditions of this license.
#
# (c)2010 by Willem van Engen <dev-rfid@willem.engen.nl>
#
import sys
import struct

from ovc import *
from ovc.util import mfclassic_getsector


if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.stderr.write('Usage: %s <ovc_dump> [<ovc_dump_2> [...]]\n'%sys.argv[0])
		sys.exit(1)

	for fn in sys.argv[1:]:
		inp = open(fn, 'r')
		data = inp.read()
		inp.close()

		if len(data) == 4096:	# mifare classic 4k
			# TODO card id, expdate, birthdate, etc.
			# transactions
			sdata = mfclassic_getsector(data, 0)

			#card ID (first 4 bytes)
			id = 0
			for i in range(0, 4):
				id = id * 256
				id = id + ord(sdata[i])
			print "Kaard id: " + str(id)

			#expiration date
			tmp = 0
			for i in range(27, 30):
				tmp = tmp * 256
				tmp = tmp + ord(sdata[i])
			date = datetime.date(1997, 1, 1)
			date += datetime.timedelta(tmp >> 4)
			print "Verloop datum kaart: " + str(date)

			#birthday
			t = 0
			sdata = mfclassic_getsector(data, 22)
			year  = (ord(sdata[14]) / 16) * 10 + ord(sdata[14]) % 16
			year  = year * 100 + (ord(sdata[15]) / 16) * 10 + ord(sdata[15]) % 16
			month = (ord(sdata[16]) / 16) * 10 + ord(sdata[16]) % 16
			day   = (ord(sdata[17]) / 16) * 10 + ord(sdata[17]) % 16
			date = datetime.date(year, month, day)
			print "Geboortedatum: " + str(date)

			for sector in range(32, 35):
				sdata = mfclassic_getsector(data, sector)[:-0x10]
				for chunk in range(0, len(sdata), 0x30):
					if ord(sdata[chunk]) == 0: continue
					print OvcClassicTransaction(sdata[chunk:chunk+0x30])
			for sector in range(35, 39):
				sdata = mfclassic_getsector(data, sector)[:-0x10]
				for chunk in range(0, len(sdata), 0x20):
					if ord(sdata[chunk]) == 0: continue
					print OvcClassicTransaction(sdata[chunk:chunk+0x20])

		elif len(data) == 64:	# mifare ultralight GVB
			# TODO card id, otp, etc.
			for chunk in range(0x10, len(data)-0x10, 0x10):
				# skip empty slots
				if data[chunk:chunk+2] == '\xff\xff': continue
				# print data
				t = OvcULTransaction(data[chunk:chunk+0x10])
				t.company = OvcCompany(2)
				print t

		else:
			sys.stderr.write('%s: expected 4096 or 64 bytes of ov-chipkaart dump file\n'%fn)
			sys.exit(2)

