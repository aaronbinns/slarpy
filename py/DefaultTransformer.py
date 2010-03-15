#!/usr/bin/python

import re
from lxml import etree
from lxml.etree import Element

class DefaultTransformer():

    html=None
    bodyPath=None
    bodyMax=None
    cruft=None
    xml=None

    def __init__( self, html, bodyPath='/html/body', bodyMax=None, cruft='//script|//style', **kw ):
        self.bodyPath = bodyPath
        self.bodyMax  = bodyMax
        self.cruft    = cruft
        self.html = html
        self.xml  = Element('doc')

    def transform(self):
        self.header( )
        self.body( )
        return self.xml
        
    def header(self):
        fields = []
        for (k,v) in self.html.metas.items():
            fields += self._fields( k, v )
        for f in fields:
            self.xml.append( f )

    def body(self):
        bodyNodes = self.html.doc.xpath( self.bodyPath )

        if self.cruft:
            for c in self.html.doc.xpath( self.cruft ):
                c.getparent().remove(c)

        if self.bodyMax is not None:
            bodyNodes = bodyNodes[0:self.bodyMax]

        # Assemble the body by iterating through all the nodes and
        # catenating non-empty TEXT ones, with a single space
        # separator.
        body=u''
        for b in bodyNodes:
            for n in b.iter(tag=etree.Element):
                if n.text:
                    body += self._scrub(unicode(n.text).strip()) + u' '

        fields = self._fields( 'content', [ body ] )
        for f in fields:
            self.xml.append( f )
            
    def _fields(self,name,values):
        fields = []
        for value in values:
            field = Element( 'field', name=name )
            field.text = self._scrub(value);
            fields.append( field )
        return fields

    # Scrub out any valid Unicode characters that are prohibited in
    # an XML document.  Mostly control characters.
    def _scrub(self,value):
        value = re.sub( u'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x84\x86-\x9f]', ' ', value )
        return value
