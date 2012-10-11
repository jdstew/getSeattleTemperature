#!/usr/bin/env python

import urllib
import xml.dom.minidom

def main():
    xmlContent = urllib.urlopen('http://www.wrh.noaa.gov/mesowest/mwXJList.php?sid=KSLC&format=xml')
    domTree = xml.dom.minidom.parseString(xmlContent.read())
    variableNodes = domTree.getElementsByTagName('variable')
    for variableNode in variableNodes:
        attributeNodeMap = variableNode.attributes
        i = 0
        attributeString = ''
        while i < attributeNodeMap.length:
            attribute = attributeNodeMap.item(i)
            attributeString = attributeString + attribute.value + ', '
            i += 1
        print attributeString
    


# Why is this boiler plate...it will call the main() function, unless 
# it is included as a module in another Python script file.
if __name__ == '__main__':
    main()
