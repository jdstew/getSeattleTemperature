#!/usr/bin/env python

# Get Seattle Temperature Application
# Targeted for Google App Engine use
# Copyright (c) 2012 Jeffrey Stewart
# 
# Licensed under the Open Software License v. 3.0 (OSL-3.0)
# (Re: www.opensource.org)
#
# File: getSeattleTemp.App
# Created: 2012-09-27

import urllib # used to open a URL stream
import xml.dom.minidom # used to parse the XML file retrieved
import math # used to compute the apparent temperature
import jinja2 # used to render the HTML template output
import os # used to create a directory reference to the HTML template
import webapp2 # used to output the HTML to the requesting browser

class getSeattleTempApp(webapp2.RequestHandler):

    def convertFahrenheitToCelsius(self, fahrenheit): 
        return (fahrenheit-32.0)*5.0/9.0
        
    def convertCelciusToFahrenheit(self, celsius):
        return (9.0/5.0)*celsius+32.0
        
    def convertMPHToMetersSecond(self, speed): 
        return speed * 0.44704
    
    # vapor pressure is the rate of evaporation
    def getVaporPressure(self, relativeHumidity, temperatureC): # relative humidity (0-100), temperature in Celcius
        return relativeHumidity/100.0*6.105*math.exp(17.27*temperatureC/(237.7+temperatureC))
        
    def getApparentTemperature (self, temperatureC, vaporPressure, windSpeedMS): # temp in C, wind in m/s
        return temperatureC + 0.33*vaporPressure - 0.70*windSpeedMS - 4.00
        
    def get(self):
        # The station identifier (e.g. KBFI) in the URL below can be replaced with any NWS station.
        xmlContent = urllib.urlopen('http://www.wrh.noaa.gov/mesowest/mwXJList.php?sid=KBFI&format=xml')
        domTree = xml.dom.minidom.parseString(xmlContent.read())

        windSpeedMPH = 0.0 # defaluts to calm condition, since this value is ommitted from xml file when calm
        windCardinalDirection = '<blank>' # defaults to blank, since this may be ommitted occasionally
        
        # warning: although I requested the XML file specification, the NWS did not reply to my email.  
        # The structure and element/attribute naming convention is dependent upon NWS XML file structure.
        variableNodes = domTree.getElementsByTagName('variable') # 'variable' is a type of element in the xml file
        for variableNode in variableNodes:
            attributeNodeMap = variableNode.attributes
            i = 0
            while i < attributeNodeMap.length:
                attribute = attributeNodeMap.item(i)
                i += 1

            if attributeNodeMap.item(0).value == "T":
                if attributeNodeMap.item(1).name == "value": # warning: the index of the 'value' attribute is assumed
                    temperatureF = float(attributeNodeMap.item(1).value)
            if attributeNodeMap.item(0).value == "RH":
                if attributeNodeMap.item(1).name == "value": # warning: the index of the 'value' attribute is assumed
                    relativeHumidity = float(attributeNodeMap.item(1).value)
            if attributeNodeMap.item(0).value == "FF":
                if attributeNodeMap.item(1).name == "value": # warning: the index of the 'value' attribute is assumed
                    windSpeedMPH = float(attributeNodeMap.item(1).value)
            if attributeNodeMap.item(0).value == "DDCARD":
                if attributeNodeMap.item(1).name == "value": # warning: the index of the 'value' attribute is assumed
                    windCardinalDirection = attributeNodeMap.item(1).value
           
        temperatureC = self.convertFahrenheitToCelsius(temperatureF)
        windSpeedMS = self.convertMPHToMetersSecond(windSpeedMPH)
        vaporPressure = self.getVaporPressure(relativeHumidity, temperatureC)
        apparentTempC = self.getApparentTemperature (temperatureC, vaporPressure, windSpeedMS)
        apparentTempF = self.convertCelciusToFahrenheit(apparentTempC)
            
        template_values = {
            'apparentTempF': int(round(apparentTempF)),
            'temperatureF': int(round(temperatureF)),
            'windSpeedMPH': int(round(windSpeedMPH)),
            'windCardinalDirection': windCardinalDirection        
        }

        jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
        template = jinja_environment.get_template('getSeattleTempApp.html')
        self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([
     ('/getSeattleTempApp', getSeattleTempApp),
], debug=True)
