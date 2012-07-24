import unittest
import ordat.cta

class LTests(unittest.TestCase) :
	def _findsOneStation(self, q, station_id) :
		found = ordat.cta.Station.find(q)
		self.assertEquals(len(found), 1)
		self.assertEquals(found[0].id, station_id)

	def test_find_logan(self) :
		self._findsOneStation('Logan Square', 41020)
		self._findsOneStation('Logan Sq', 41020)
		self._findsOneStation('Logan', 41020)

	def test_find_clarklake(self) :
		self._findsOneStation('Clark/Lake', 40380)
		self._findsOneStation('Clark and Lake', 40380)
		self._findsOneStation('Clark Lack', 40380)
