import requests
import sys
import xmltodict
import time
import threading
import os.path
import csv
import weakref
import utility_funcs

class Failure(Exception) :
	pass

class HTTPFailure(Failure) :
	pass
class APIFailure(Failure) :
	pass

class CachingXMLAPI(object) :
	def __init__(self, key=None, timeout=60.0) :
		self.cache = {}
		self.key = key
		self.timeout = timeout
		self.cachelock = threading.Lock()

	def req(self, uri) :
		with self.cachelock :
			if uri in self.cache :
				exp, data = self.cache[uri]
				if time.time() >= exp :
					del self.cache[uri]
				else :
					return data

		#print 'GET %s' % uri
		resp = requests.get(uri)
		if resp.status_code != 200 :
			raise HTTPFailure(resp.status_code)

		data = xmltodict.parse(resp.content)
		self.cache[uri] = (time.time() + self.timeout, data)
		return data

class Line(object) :
	all = []
	bycode = {}

	def __init__(self, name, code) :
		self.name = name
		self.code = code
		self.stops = []

		self.all.append(self)
		self.bycode[self.code] = self
	
	def add_stop(self, stop) :
		self.stops.append(stop)

	@property
	def stations(self) :
		stations = set()
		for stop in self.stops :
			stations.add(stop.station)
		return list(stations)

	def __repr__(self) :
		return str(self)
	def __str__(self) :
		return '%s Line' % self.name

class GeoObject(object) :
	def to_km(self, other) :
		return utility_funcs.distance(self.loc, other.loc)

	def to_mi(self, other) :
		km = self.to_km(other)
		return km * 0.62137119223733396962

class FindName(object) :
	@classmethod
	def find(cls, text) :
		levens = dict()
		for obj in cls.all :
			leven = utility_funcs.levenshtein(text, obj.name)
			levens.setdefault(leven, [])
			levens[leven].append(obj)
		try :
			return levens[min(levens.keys())]
		except ValueError :
			return []

class Station(GeoObject, FindName) :
	all = []
	byid = {}

	def __init__(self, id, name, descr, lat, lon) :
		self.id = id
		self.name = name
		self.descr = descr
		self.loc = lat, lon
		self.stops = []

		self.all.append(self)
		self.byid[self.id] = self

	def arrivals(self, api=None) :
		if api is None :
			api = Train.getapi()
		return api.arrivals(mapid=self.id)

	@property
	def lines(self) :
		return list(set(reduce(lambda l1,l2: l1+l2, [stop.lines for stop in self.stops])))

	def add_stop(self, stop) :
		self.stops.append(stop)

	def __repr__(self) :
		return str(self)
	def __str__(self) :
		return 'Station %s' % self.name

class Stop(GeoObject) :
	all = []
	byid = {}

	def __init__(self, id, name, station, dir_code) :
		self.id = id
		self.name = name
		self.station = station
		self.dir_code = dir_code
		self.lines = []

		self.station.add_stop(self)
		self.all.append(self)
		self.byid[self.id] = self

	def add_line(self, line) :
		self.lines.append(line)
		line.add_stop(self)

	def arrivals(self, api=None) :
		if api is None :
			api = Train.getapi()
		return api.arrivals(stpid=self.id)

	@property
	def loc(self) :
		return self.station.loc

	def __repr__(self) :
		return str(self)
	def __str__(self) :
		return '%s-bound Stop %s at %s' % (self.dir_code, self.name, self.station)

Line.Blue = Line('Blue', 'Blue')
Line.Brown = Line('Brown', 'Brn')
Line.Red = Line('Red', 'Red')
Line.Green = Line('Green', 'G')
Line.Purple = Line('Purple', 'P')
Line.Purple = Line('Pink', 'Pink')
Line.PurpleExpress = Line('Purple Express', 'Pexp')
Line.Yellow = Line('Yellow', 'Y')
Line.Orange = Line('Orange', 'Org')

def load() :
	f = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cta_L_stops.csv')

	linecodes = set(Line.bycode.keys())

	for sd in csv.DictReader(open(f)) :
		stop_id = long(sd['STOP_ID'])
		dir_code = sd['DIRECTION_ID']
		stop_name = sd['STOP_NAME']
		lat, lon = float(sd['LAT']), float(sd['LON'])
		station_name = sd['STATION_NAME']
		station_desc = sd['STATION_DESCRIPTIVE_NAME']
		station_id = long(sd['PARENT_STOP_ID'])

		if not station_id :
			print 'ERROR bad station_id %s in sd %s' % (station_id, sd)
			continue

		# TODO more validation

		if station_id in Station.byid :
			station = Station.byid[station_id]
		else :
			station = Station(station_id, station_name, station_desc, lat, lon)

		stop = Stop(stop_id, stop_name, station, dir_code)
		for k,v in sd.items() :
			if k in Line.bycode and long(v) == 1 :
				line = Line.bycode[k]
				stop.add_line(line)

load()

class Arrival(object) :
	@classmethod
	def totime(cls, s) :
		return time.strptime(s, '%Y%m%d %H:%M:%S')

	def __init__(self, raw) :
		try :
			self.line = Line.bycode[raw['rt']]
			self.station = Station.byid[long(raw['staId'])]
			self.stop = Stop.byid[long(raw['stpId'])]
			self.arrives = Arrival.totime(raw['arrT'])
			self.predicted = Arrival.totime(raw['prdt'])
			self.run_number = long(raw['rn'])
			self.raw = raw
		finally :
			if not hasattr(self, 'raw') :
				print 'error! for debugging, here is the raw...' 
				print raw

	@property
	def arrives_ts(self) :
		"""
		Arrival time in epoch.
		"""
		return time.mktime(self.arrives)

	@property
	def predicted_ts(self) :
		"""
		When the prediction was generated, in epoch.
		"""
		return time.mktime(self.predicted)

	def __repr__(self) :
		return str(self)
	def __str__(self) :
		return '%s/%s run %d at %s' % (self.line, self.stop.name, self.run_number, self.arrives)

"""
{
           u'arrT': u'20120722 18:30:19',
           u'destNm': u'Forest Park',
           u'destSt': u'0',
           u'flags': None,
           u'isApp': u'0',
           u'isDly': u'0',
           u'isFlt': u'0',
           u'isSch': u'0',
           u'prdt': u'20120722 18:13:19',
           u'rn': u'217',
           u'rt': u'Blue',
           u'staId': u'40590',
           u'staNm': u'Damen',
           u'stpDe': u'Service toward Forest Park',
           u'stpId': u'30116',
           u'trDr': u'5'},
"""

class Train(CachingXMLAPI) :
	trains = weakref.WeakSet()

	class Empty(Exception) :
		"""
		No API instances are active in the process, so we're left without any available.  Make one first.
		"""
		pass

	def __init__(self, *a, **kw) :
		self.trains.add(self)
		CachingXMLAPI.__init__(self, *a, **kw)

	@classmethod
	def getapi(cls) :
		try :
			return list(cls.trains)[0]
		except :
			raise cls.Empty

	def arrivals(self, **kw) :
		kw['key'] = self.key
		args = '&'.join([('%s=%s' % (k,v)) for (k,v) in kw.items()])
		url = 'http://lapi.transitchicago.com/api/1.0/ttarrivals.aspx?%s' % args
		data = self.req(url)['ctatt']
		if data['errNm'] :
			raise APIFailure('CTA Traintracker API Failure: %s' % data['errNm'])

		tmst = Arrival.totime(data['tmst'])

		# 0 etas present...
		if 'eta' not in data :
			return []

		# 1 eta present..
		etas = data['eta']
		if isinstance(etas, dict) :
			etas = [etas]

		# there we go, now we have a list at least

		a = list()		
		for eta in etas :
			a.append(Arrival(eta))
		return a
