"""Generic proxy to an INCF DAI hub"""

import urllib
import httplib2
import logging

from incf.dai.response import Response

logger = logging.getLogger('incf.dai')

class HubProxy(object):
    """ Generic proxy to an INCF DAI hub """

    def __init__(self, base_url, minimal=False, offline=False):
        self.base_url = base_url
        # no cache for the time being
        # self.proxy = httplib2.Http('.cache')
        if offline:
            self.proxy = LocalProxy()
        else:
            self.proxy = httplib2.Http()
            if not minimal:
                self.capabilities = self.get_capabilities()

    def __call__(self, service_id, version=None, **kw):
        """Generic call method invoking
        <base_url>&version=<version>&request=<service_id><querystring>
        where the <querystring> is constructed from the keyword arguments"""
        url = self.base_url
        if version is not None:
            version_string = "&version=%s" % version
            url += version_string
        url = url + '&request=' + service_id +'&'
        query_string = urllib.urlencode(kw)
        url += query_string
        logger.info("Calling %s" % url)
        return Response(self.proxy.request(url, "GET"))

    # Every hub is required to provide this

    def GetCapabilities(self, output='xml'):
        """A list of all services provided by the hub"""
        return self('GetCapabilities', output=output)

    def DescribeProcess(self, version="1.0.0", output='xml'):
        """Detailed description of services at the hub"""
        return self('DescribeProcess', version=version, output=output)

    
    # some private helper methods

    def get_capabilities(self):
        """Call 'GetCapabilities' and return the extracted method ids"""
        response =  self('GetCapabilities', output='xml')
        key_1 = 'wps_ProcessOfferings'
        key_2 = 'wps_Process'
        return tuple([l['ows_Identifier']
                      for l in response[key_1][key_2]]
                     )
    

# helper class for offline testing

class LocalProxy(object):
    """Dummy proxy for offline testing"""
    def request(self, url, *args, **kw):
        """Fake a request by printing the URL that would be called
        and returning a minimal response tuple."""
        print "Calling", url
        return ("Dummy header", "<xml>Foo</xml>")
    
