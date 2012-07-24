import unittest
import ordat.cta

class LTests(unittest.TestCase) :
	def _findsOneStation(self, q, station_id) :
		found = ordat.cta.Station.find(q)
		self.assertEquals(len(found), 1)
		self.assertEquals(found[0].id, station_id)

	def _findsOneLine(self, q, line_code) :
		found = ordat.cta.Line.find(q)
		self.assertEquals(len(found), 1)
		self.assertEquals(found[0].code, line_code)

	def test_find_logan(self) :
		self._findsOneStation('Logan Square', 41020)
		self._findsOneStation('Logan Sq', 41020)
		self._findsOneStation('Logan', 41020)

	def test_find_clarklake(self) :
		self._findsOneStation('Clark/Lake', 40380)
		self._findsOneStation('Clark and Lake', 40380)
		self._findsOneStation('Clark Lack', 40380)

	def test_find_lines(self) :
		self._findsOneLine("Blue", "Blue")
		self._findsOneLine("G", "G")
		self._findsOneLine("Purple Express", "Pexp")
		self._findsOneLine("PurpExpress", "Pexp")
		self._findsOneLine("Purple", "P")
		self._findsOneLine("Purp", "P")
