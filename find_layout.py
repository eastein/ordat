import cta
import sys

# TODO remove blue specificity
#stations = cta.Line.Blue.stations
#lines = [cta.Line.Blue]

stations = cta.Station.all
lines = cta.Line.all

train = cta.Train(key=sys.argv[1])

def cmp_arrts(a, b) :
	return long.__cmp__(long(a.arrives_ts), long(b.arrives_ts))

def compute_stop_edges() :
	all_arrivals = reduce(lambda a1,a2: a1+a2, [station.arrivals() for station in stations])

	runs = dict()
	for arr in all_arrivals :
		runs.setdefault(arr.run_number, list())
		runs[arr.run_number].append(arr)

	delays = dict()
	for rid, ra in runs.items() :
		#print 'sorting run %d' % rid
	
		ra = [a for a in ra if not a.fault and not a.delay]
		ra.sort(cmp=cmp_arrts)
		n = len(ra)
		if n < 2 :
			continue
		delay_count = 0
		for i in range(n - 1) :
			for _j in range(n - 1 - i) :
				j = _j + 1
				dtime = ra[j].arrives_ts - ra[i].arrives_ts
				stop1 = ra[i].stop
				stop2 = ra[j].stop
				if dtime < 1.0 :
					#print 'what the hell, that is one fast train dude.'
					continue
				if ra[i].line != ra[j].line :
					#print 'wait, %s and %s are the same run, but different lines! trains are fucking nuts.' % (ra[i], ra[j])
					continue
			
				line = ra[i].line

				delays.setdefault(line, dict())
				delays[line].setdefault(stop1, dict())
				delays[line][stop1].setdefault(stop2, list())
				delays[line][stop1][stop2].append(dtime)
				delay_count += 1

		#print 'processed %d delays for run %d' % (delay_count, rid)

	#print 'now finding delays'
	# TODO fix the assumption that one stop + line combo is going to go to a deterministic stop. could have many options. may need to make delays separate by destination name.....


	for line, d in delays.items() :
		if line not in lines :
			continue
	
		#print line
		for stop1, outbound in d.items() :
			shortest = 10000000000000000
			next = None
			for stop2, delaylist in outbound.items() :
				d = min(delaylist)
				if d < shortest :
					shortest = d
					next = stop2

				mins = d / 60.0
				hours = d / 3600.0
				#print '%s : %s -> %s (stp %d -> %d) = %0.3f mph, %0.2f minutes' % (line.name, stop1.station.name, stop2.station.name, stop1.id, stop2.id, stop1.to_mi(stop2) / hours, mins)
				
			if next :
				print '%s : %s -> %s (stp %d -> %d) = %d sec' % (line.name, stop1.station.name, next.station.name, stop1.id, next.id, long(d))

compute_stop_edges()
