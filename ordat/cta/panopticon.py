from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
import time
import ordat.cta.apis as apis
from functools import reduce

class Tracker(object) :
	L_POLL = 300
	
	def __init__(self) :
		self.now = None
		self.then = None
		self.l_updated = None
		self.all_arrivals = []
	
	def step(self) :
		# track previous timestamp, and current.
		self.then = self.now
		self.now = time.time()
		
		# compute a key (.run_number, .stop.id)
		def k(a) :
			return a.run_number, a.stop.id
	
		if self.l_updated is None or self.now - self.l_updated > self.L_POLL :
			self.l_updated = self.now

			print('polling all stations')
			
			fresh_keys = set()
			self.old_arrivals = self.all_arrivals
			self.all_arrivals = list()
			arrival_sets = []
			for station in apis.Station.all :
				try :
					arrival_sets.append(station.arrivals())
				except apis.NetworkFailure :
					print('network issue, ignoring')
					pass
				except apis.APIFailure as af :
					print('api failure (ignored):', af)
					pass

			for a in reduce(lambda a1,a2: a1+a2, arrival_sets) :
				fresh_keys.add(k(a))
				self.all_arrivals.append(a)
			for oa in self.old_arrivals :
				if k(oa) not in fresh_keys :
					self.all_arrivals.append(oa)
			
			print('done polling all stations')
		
		run_nums = set([arrival.run_number for arrival in self.all_arrivals])
		for rn in run_nums :
			arrs = [arr for arr in self.all_arrivals if arr.run_number == rn]
			arrs.sort(cmp=lambda x, y: cmp(x.arrives_ts,y.arrives_ts))
			
			past = [a for a in arrs if a.arrives_ts < self.now]
			future = [a for a in arrs if a.arrives_ts > self.now]
			
			# TODO handle what happens if it's right on the money...
			
			if past and future :
				a = past[-1]
				b = future[0]
				r = (self.now - a.arrives_ts) / (b.arrives_ts - a.arrives_ts)
				alat, alon = a.station.loc
				blat, blon = b.station.loc
				lat = alat + (blat - alat) * r
				lon = alon + (blon - alon) * r

				# TODO beyond just lat/lon & line
				yield (rn, a.line, lat, lon)
			elif past :
				pass#print 'run number %d only has past schedules: %s' % (rn, past)
			elif future :
				pass#print 'run number %d only has future schedules: %s' % (rn, future)
			else :
				pass#print 'run number %d seems to have no scheds...' % rn
