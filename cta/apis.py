import requests
import sys
import xmltodict
import time
import threading

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

		#print 'GET %s' % uri
		resp = requests.get(uri)
		if resp.status_code != 200 :
			raise Failure(resp.status_code)

		data = xmltodict.parse(resp.content)
		self.cache[uri] = (time.time(), data)
		return data

class Train(CachingXMLAPI) :
	def arrivals(self, **kw) :
		kw['key'] = self.apikey
		# TODO care about security and encoding, or do I even need to bother? I'm a client.
		args = '&'.join([('%s=%s' % (k,v)) for (k,v) in kw.items()])
		return self.req('http://lapi.transitchicago.com/api/1.0/ttarrivals.aspx?%s' % args)
