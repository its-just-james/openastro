#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    This file is part of openastro.org.

    OpenAstro.org is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    OpenAstro.org is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with OpenAstro.org.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys, os.path


#config class
class openAstroCfg:

	def __init__(self):
		self.version = VERSION
		dprint("-------------------------------")
		dprint('  OpenAstro.org '+str(self.version))
		dprint("-------------------------------")
		self.homedir = os.path.expanduser("~")

		#check for astrodir
		self.astrodir = os.path.join(self.homedir, '.openastro.org')
		if os.path.isdir(self.astrodir) == False:
			os.mkdir(self.astrodir)

		#check for tmpdir
		self.tmpdir = os.path.join(self.astrodir, 'tmp')
		if os.path.isdir(self.tmpdir) == False:
			os.mkdir(self.tmpdir)

		#check for swiss local dir
		self.swissLocalDir = os.path.join(self.astrodir, 'swiss_ephemeris')
		if os.path.isdir(self.swissLocalDir) == False:
			os.mkdir(self.swissLocalDir)

		#geonames database
		self.geonamesdb = os.path.join(DATADIR, 'geonames.sql' )

		#icons
		icons = os.path.join(DATADIR,'icons')
		self.iconWindow = os.path.join(icons, 'openastro.svg')
		self.iconAspects = os.path.join(icons, 'aspects')

		#basic files
		self.tempfilename = os.path.join(self.tmpdir,"openAstroChart.svg")
		self.tempfilenameprint = os.path.join(self.tmpdir,"openAstroChartPrint.svg")
		self.tempfilenametable = os.path.join(self.tmpdir,"openAstroChartTable.svg")
		self.tempfilenametableprint = os.path.join(self.tmpdir,"openAstroChartTablePrint.svg")
		self.xml_ui = os.path.join(DATADIR, 'openastro-ui.xml')
		self.xml_svg = os.path.join(DATADIR, 'openastro-svg.xml')
		self.xml_svg_table = os.path.join(DATADIR, 'openastro-svg-table.xml')

		#sqlite databases
		self.astrodb = os.path.join(self.astrodir, 'astrodb.sql')
		self.peopledb = os.path.join(self.astrodir, 'peopledb.sql')
		# self.famousdb = os.path.join(DATADIR, 'famous.sql' )  ## bah to celevrity
		return

	def checkSwissEphemeris(self,num):
		#00 = -01-600
		#06 = 600 - 1200
		#12 = 1200 - 1800
		#18 = 1800 - 2400
		#24 = 2400 - 3000
		seas='ftp://ftp.astro.com/pub/swisseph/ephe/seas_12.se1'
		semo='ftp://ftp.astro.com/pub/swisseph/ephe/semo_12.se1'
		sepl='ftp://ftp.astro.com/pub/swisseph/ephe/sepl_12.se1'
