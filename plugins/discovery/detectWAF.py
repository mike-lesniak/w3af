'''
detectWAF.py

Copyright 2006 Andres Riancho

This file is part of w3af, w3af.sourceforge.net .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

'''

from core.data.fuzzer.fuzzer import *
import core.controllers.outputManager as om
from core.controllers.w3afException import w3afException
import core.data.kb.knowledgeBase as kb
import core.data.kb.info as info
from core.controllers.basePlugin.baseDiscoveryPlugin import baseDiscoveryPlugin
import socket
from core.controllers.w3afException import w3afRunOnce

class detectWAF(baseDiscoveryPlugin):
    '''
    Identify if a Web Application Firewall is present and if possible identify the vendor and version.
    @author: Andres Riancho ( andres.riancho@gmail.com )
    '''
    
    def __init__(self):
        baseDiscoveryPlugin.__init__(self)
        self._run = True
        
    def discover(self, fuzzableRequest ):
        '''
        @parameter fuzzableRequest: A fuzzableRequest instance that contains (among other things) the URL to test.
        '''
        if not self._run:
            # This will remove the plugin from the discovery plugins to be runned.
            raise w3afRunOnce()
        else:
            # I will only run this one time. All calls to detectWAF return the same url's ( none! )
            self._run = False
            self._identifyURLScan( fuzzableRequest )
            self._identifyModSecurity( fuzzableRequest )
            self._identifySecureIIS( fuzzableRequest )

        return []
    
    def _identifySecureIIS(self,  fuzzableRequest):
        '''
        Try to verify if SecureIIS is installed or not.
        '''
        # And now a final check for SecureIIS
        h = fuzzableRequest.getHeaders()
        h['Transfer-Encoding'] = createRandAlpha(1024 + 1)
        lockResponse2 = self._urlOpener.GET( fuzzableRequest.getURL(), headers=h, useCache=True )
        if lockResponse2.getCode() == 404:
            self._reportFinding('SecureIIS', response)
        
    def _identifyModSecurity(self,  fuzzableRequest):
        '''
        Try to verify if mod_security is installed or not AND try to get the installed version.
        '''
        pass
    
    def _identifyURLScan(self,  fuzzableRequest):
        '''
        Try to verify if URLScan is installed or not.
        '''
        # detect using GET
        # Get the original response
        originalResponse = self._urlOpener.GET( fuzzableRequest.getURL(), useCache=True )
        if originalResponse.getCode() != 404:
            # Now add the if header and try again
            h = fuzzableRequest.getHeaders()
            h['If'] = createRandAlpha(8)
            ifResponse = self._urlOpener.GET( fuzzableRequest.getURL(), headers=h, useCache=True )
            
            h = fuzzableRequest.getHeaders()
            h['Translate'] = createRandAlpha(8)
            translateResponse = self._urlOpener.GET( fuzzableRequest.getURL(), headers=h, useCache=True )
            
            h = fuzzableRequest.getHeaders()
            h['Lock-Token'] = createRandAlpha(8)
            lockResponse = self._urlOpener.GET( fuzzableRequest.getURL(), headers=h, useCache=True )
            
            h = fuzzableRequest.getHeaders()
            h['Transfer-Encoding'] = createRandAlpha(8)
            transferEncodingResponse = self._urlOpener.GET( fuzzableRequest.getURL(), headers=h, useCache=True )
        
            if ifResponse.getCode() == 404 or translateResponse.getCode() == 404 or\
            lockResponse.getCode() == 404 or transferEncodingResponse.getCode() == 404:
                self._reportFinding('URLScan', response)

    
    def _reportFinding( self, name, response ):
        i = info.info()
        i.setURL( fuzzableRequest.getURL() )
        i.setDesc( 'The remote web server seems to have a '+name+'.' )
        i.setName('Found '+name)
        kb.kb.append( self, name, i )
        om.out.information( i.getDesc() )
    
    def getOptionsXML(self):
        '''
        This method returns a XML containing the Options that the plugin has.
        Using this XML the framework will build a window, a menu, or some other input method to retrieve
        the info from the user. The XML has to validate against the xml schema file located at :
        w3af/core/ui/userInterface.dtd
        
        @return: XML with the plugin options.
        ''' 
        return  '<?xml version="1.0" encoding="ISO-8859-1"?>\
        <OptionList>\
        </OptionList>\
        '

    def setOptions( self, OptionList ):
        '''
        This method sets all the options that are configured using the user interface 
        generated by the framework using the result of getOptionsXML().
        
        @parameter OptionList: A dictionary with the options for the plugin.
        @return: No value is returned.
        ''' 
        pass
        
    def getPluginDeps( self ):
        '''
        @return: A list with the names of the plugins that should be runned before the
        current one.
        '''
        return []

    def getLongDesc( self ):
        '''
        @return: A DETAILED description of the plugin functions and features.
        '''
        return '''
        Identify if a Web Application Firewall is present and if possible identify the vendor and version.
        '''
