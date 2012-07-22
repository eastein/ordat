import requests
import sys
import xmltodict
import time
import threading
import os.path
import csv

class Failure(Exception) :
	pass

class CachingXMLAPI(object) :
	def __init__(self, apikey=None, timeout=30) :
		self.cache = {}
		self.apikey = apikey
		self.timeout = timeout
		self.cachelock = threading.Lock()

	def req(self, uri) :
		with self.cachelock :
			if uri in self.cache :
				exp, data = self.cache[uri]
				if exp <= time.time() + self.timeout :
					return data
				else :
					del self.cache[uri]

		#print 'GET %s' % uri
		resp = requests.get(uri)
		if resp.status_code != 200 :
			raise Failure(resp.status_code)

		data = xmltodict.parse(resp.content)
		self.cache[uri] = (time.time(), data)
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
	
	@property
	def stations(self) :
		raise NotImplemented

	def __repr__(self) :
		return str(self)
	def __str__(self) :
		return '%s Line' % self.name

class Station(object) :
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

	def add_stop(self, stop) :
		self.stops.append(stop)

	def __repr__(self) :
		return str(self)
	def __str__(self) :
		return 'Station %s' % self.name

class Stop(object) :
	all = []

	def __init__(self, id, name, station, dir_code) :
		self.id = id
		self.name = name
		self.station = station
		self.dir_code = dir_code
		
		self.station.add_stop(self)
		self.all.append(self)

	@property
	def loc(self) :
		return self.station.loc

	def __repr__(self) :
		return str(self)
	def __str__(self) :
		return 'Stop %s at %s' % (self.name, self.station)

Line.Blue = Line('Blue', 'Blue')
Line.Brown = Line('Brown', 'Brn')
Line.Red = Line('Red', 'Red')
Line.Green = Line('Green', 'G')
Line.Purple = Line('Purple', 'P')
Line.PurpleExpress = Line('Purple Express', 'Pexp')
Line.Yellow = Line('Yellow', 'Y')
Line.Orange = Line('Orange', 'Org')

def load() :
	f = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cta_L_stops.csv')

	linecodes = set([l.code for l in Line.all])

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

load()

class Train(CachingXMLAPI) :
	def arrivals(self, **kw) :
		kw['key'] = self.apikey
		# TODO care about security and encoding, or do I even need to bother? I'm a client.
		args = '&'.join([('%s=%s' % (k,v)) for (k,v) in kw.items()])
		return self.req('http://lapi.transitchicago.com/api/1.0/ttarrivals.aspx?%s' % args)
