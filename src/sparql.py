#!/usr/bin/python
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
#
# ProcessText.py
# Copyright (C) Pilolli 2012 <pilolli.pietro@gmail.com>
# 
# vox-launcher is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# vox-launcher is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
from SPARQLWrapper import SPARQLWrapper2, SPARQLWrapper, TURTLE
import sys, getopt
import speechd


# The sparql endpoint.
endpoint='http://dbpedia.org/sparql'


# This class run queryes on the sparql service.
class Sparql():

  def speak(self, item, lang):
    client = speechd.SSIPClient('vox-launcher')
    client.set_priority(speechd.client.Priority.IMPORTANT)
    client.set_pause_context(0)
    client.set_language(lang)
    client.speak(item)
    client.close()
  
  def run(self, item, lang):
    
    try:
      sparql = SPARQLWrapper2(endpoint)
      query = ('SELECT DISTINCT * WHERE {'
                      '?item rdfs:label "' + item + '"@en.'
                      '?item rdfs:comment ?result.'
                      'FILTER ( lang(?result) = "' + lang + '" )'
               '}')

      sparql.setQuery(query)
      res = sparql.query()
      if len(res.bindings) > 0:
        res = res.bindings[0]['result'].value
        self.speak(res, lang)
        return True
    
    except:
      return False
    
    return False
      

