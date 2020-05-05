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
# basics
import os.path, math, socket, webbrowser, pytz

#template processing
from string import Template

#copyfile
from shutil import copyfile

#GTK, cairo to display svg
from gi import require_version
require_version('Rsvg', '2.0')
require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject, Rsvg, cairo

# Cairo svg class moved to openastro/drawsvg.py
## THIS SEEMS SOMEWHAT BROKEN
## CHECK FILE EXPORTS FOR TABLE FORMATTING ERRORS

class drawSVG(Gtk.DrawingArea):
	def __init__(self):
		super().__init__()
		self.connect("draw", self.exposeEvent)

	def setSVG(self,svg):
		self.svg = Rsvg.Handle.new_from_file(svg)
		width=self.svg.props.width*openAstro.zoom
		height=self.svg.props.height*openAstro.zoom
		self.set_size_request(int(width),int(height))
		dprint('drawSVG.setSVG file %s' % (svg))

	def exposeEvent(self,widget,event):
		#try:
		#	context = self.get_window().cairo_create()
		#except AttributeError as err:
		#	print(err)
		#	return True

		if self.svg != None:
			self.svg.render_cairo(event)

			#set a clip region for the expose event
			#context.rectangle(event.area.x, event.area.y,event.area.width, event.area.height)
			#rect=event.copy_clip_rectangle_list()
			#context.rectangle(rect[0][0],rect[0][1],rect[0][2],rect[0][3])
			#context.clip()

class mainWindow:
	def __init__(self):

		#gtktopwindow
		self.window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
		self.window.connect("destroy", lambda w: Gtk.main_quit())
		self.window.set_title("OpenAstro.org")
		self.window.set_icon_from_file(cfg.iconWindow)
		self.window.maximize()

		self.vbox = Gtk.VBox()

		#uimanager
		self.uimanager = Gtk.UIManager()
		self.ui_mid = self.uimanager.add_ui_from_file(cfg.xml_ui)
		accelgroup = self.uimanager.get_accel_group()
		self.window.add_accel_group(accelgroup)

		#actions definitions
		self.actions = [('File', None, _('Chart') ),
								('Quit', Gtk.STOCK_QUIT, _("Quit!"), None,'Quit the Program', self.quit_cb),
	                     ('History', None, _('History') ),
	                     ('newChart', Gtk.STOCK_NEW, _('New Chart'), None, 'New Chart', self.eventDataNew ),
	                     ('importXML', Gtk.STOCK_OPEN, _('Open Chart'), None, 'Open Chart', self.doImport ),
	                     ('exportXML', Gtk.STOCK_SAVE, _('Save Chart'), None, 'Save Chart', self.doExport ),
	                     ('export', Gtk.STOCK_SAVE_AS, _('Save as') ),
	                     ('exportPNG', None, _('PNG Image'), None, 'PNG Image', self.doExport ),
	                     ('exportSVG', None, _('SVG Image'), None, 'SVG Image', self.doExport ),
	                     ('exportJPG', None, _('JPG Image'), None, 'JPG Image', self.doExport ),
	                     ('exportPDF', None, _('PDF File'), None, 'PDF File', self.doPrint ),
	                     ('import', None, _('Import') ),
	                     ('importOroboros', None, _('Oroboros (*.xml)'), None, 'Oroboros (*.xml)', self.doImport ),
	                     ('importAstrolog32', None, _('Astrolog (*.dat)'), None, 'Astrolog (*.dat)', self.doImport ),
	                     ('importSkylendar', None, _('Skylendar (*.skif)'), None, 'Skylendar (*.skif)', self.doImport ),
	                     ('importZet8', None, _('Zet8 Dbase (*.zbs)'), None, 'Zet8 Dbase (*.zbs)', self.doImport ),
	                     ('Event', None, _('Event') ),
	                     ('EditEvent', Gtk.STOCK_EDIT, _('Edit Event'), None, 'Event Data', self.eventData ),
	                     ('OpenDatabase', Gtk.STOCK_HARDDISK, _('Open Database'), None, 'Open Database', self.openDatabase ),
								('QuickOpenDatabase', None, _('Quick Open Database') ),
	                     # ('OpenDatabaseFamous', Gtk.STOCK_HARDDISK, _('Open Famous People Database'), None, 'Open Database Famous', self.openDatabaseFamous ),
	                     ('Settings', None, _('Settings') ),
	                     ('Special', None, _('Chart Type') ),
	                     ('ZoomRadio', None, _('Zoom') ),
								('Planets', None, _('Planets & Angles'), None, 'Planets & Angles', self.settingsPlanets ),
								('Aspects', None, _('Aspects'), None, 'Aspects', self.settingsAspects ),
								('Colors', None, _('Colors'), None, 'Colors', self.settingsColors ),
								('Labels', None, _('Labels'), None, 'Labels', self.settingsLabel ),
								('Location', Gtk.STOCK_HOME, _('Set Home Location'), None, 'Set Location', self.settingsLocation ),
								('Configuration', Gtk.STOCK_PREFERENCES, _('Configuration'), None, 'Configuration', self.settingsConfiguration ),
								('Radix', None, _('Radix Chart'), None, 'Transit Chart', self.specialRadix ),
								('Transit', None, _('Transit Chart'), None, 'Transit Chart', self.specialTransit ),
								('Synastry', None, _('Synastry Chart'), None, 'Synastry Chart...', lambda w: self.openDatabaseSelect(_("Select for Synastry"),"Synastry") ),
								('Composite', None, _('Composite Chart'), None, 'Composite Chart...', lambda w: self.openDatabaseSelect(_("Select for Composite"),"Composite") ),
								('Combine', None, _('Combine Chart'), None, 'Combine Chart...', lambda w: self.openDatabaseSelect(_("Select for Combine"),"Combine") ),
								('Solar', None, _('Solar Return'), None, 'Solar Return...', self.specialSolar ),
								('SecondaryProgression', None, _('Secondary Progressions'), None, 'Secondary Progressions...', self.specialSecondaryProgression ),
								('Tables', None, _('Tables') ),
								('MonthlyTimeline', None, _('Monthly Timeline'), None, 'Monthly Timeline', self.tableMonthlyTimeline ),
								('CuspAspects', None, _('Cusp Aspects'), None, 'Cusp Aspects', self.tableCuspAspects ),
								('Extra', None, _('Extra') ),
								('exportDB', None, _('Export Database'), None, 'Export Database', self.extraExportDB ),
								('importDB', None, _('Import Database'), None, 'Import Database', self.extraImportDB ),
								('About', None, _('About') ),
								('AboutInfo', Gtk.STOCK_INFO, _('Info'), None, 'Info', self.aboutInfo )  ,
	                     ('AboutSupport', Gtk.STOCK_HELP, _('Support'), None, 'Support', lambda w: webbrowser.open_new('http://www.openastro.org/?Support') )
	                     ]

		#update UI
		self.updateUI()

		# Create a MenuBar
		menubar = self.uimanager.get_widget('/MenuBar')
		self.vbox.pack_start(menubar, expand=False, fill=True, padding=0)

		#make first SVG
		self.tempfilename = openAstro.makeSVG()

		# Draw svg pixbuf
		self.draw = drawSVG()
		self.draw.setSVG(self.tempfilename)
		scrolledwindow = Gtk.ScrolledWindow()
		scrolledwindow.add_with_viewport(self.draw)
		scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
		self.vbox.pack_start(scrolledwindow, expand=True, fill=True, padding=0)

		self.window.add(self.vbox)
		self.window.show_all()

		#check if we need to ask for location
		if openAstro.ask_for_home:
			self.settingsLocation(self.window)

		#check internet connection
		self.checkInternetConnection()

		return

	"""
	'Extra' Menu Items Functions

	extraExportDB
	extraImportDB

	"""

	def extraExportDB(self, widget):
		chooser = Gtk.FileChooserDialog(parent=self.window, title=None,action=Gtk.FileChooserAction.SAVE,
                                  buttons=(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,Gtk.STOCK_SAVE,Gtk.ResponseType.OK))
		chooser.set_current_folder(cfg.homedir)
		chooser.set_current_name('openastro-database.sql')
		filter = Gtk.FileFilter()
		filter.set_name(_("OpenAstro.org Databases (*.sql)"))
		filter.add_pattern("*.sql")
		chooser.add_filter(filter)
		response = chooser.run()

		if response == Gtk.ResponseType.OK:
			copyfile(cfg.peopledb, chooser.get_filename())

		elif response == Gtk.ResponseType.CANCEL:
					dprint('Dialog closed, no files selected')
		chooser.destroy()

	def extraImportDB(self, widget):
		chooser = Gtk.FileChooserDialog(parent=self.window, title=_("Please select database to import"),action=Gtk.FileChooserAction.OPEN,
                                  buttons=(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
		chooser.set_current_folder(cfg.homedir)
		filter = Gtk.FileFilter()
		filter.set_name(_("OpenAstro.org Databases (*.sql)"))
		filter.add_pattern("*.sql")
		chooser.add_filter(filter)
		response = chooser.run()

		if response == Gtk.ResponseType.OK:
			db.databaseMerge(cfg.peopledb,chooser.get_filename())

		elif response == Gtk.ResponseType.CANCEL:
					dprint('Dialog closed, no files selected')
		chooser.destroy()

	"""

	Function to check if we have an internet connection
	for geonames.org geocoder

	"""
	def checkInternetConnection(self):

		if db.getAstrocfg('use_geonames.org') == "0":
			self.iconn = False
			dprint('iconn: not using geocoding!')
			return

		#from openastromod import timeoutsocket
		#timeoutsocket.setDefaultSocketTimeout(2)
		HOST='api.geonames.org'
		PORT=80
		s = None

		try:
			socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM)
		except socket.error as msg:
			self.iconn = False
			dprint('No Internet connection (getaddrinfo)')
			return

		for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM):
			af, socktype, proto, canonname, sa = res
			try:
				s = socket.socket(af, socktype, proto)
			except socket.error as msg:
				s = None
				continue
			try:
				s.connect(sa)
			except (socket.error, timeoutsocket.Timeout):
				s.close()
				s = None
				continue
			break

		if s is None:
			self.iconn = False
			dprint('No Internet connection')
		else:
			self.iconn = True
			dprint('Connected to Internet')
			#timeoutsocket.setDefaultSocketTimeout(20)
			s.close()
		return

	"""

	Check for zoom function

	"""

	def zoom(self, action, current):
		#check for zoom level
		if current.get_name() == 'z80':
			openAstro.zoom=0.8
		elif current.get_name() == 'z150':
			openAstro.zoom=1.5
		elif current.get_name() == 'z200':
			openAstro.zoom=2
		else:
			openAstro.zoom=1

		#redraw svg
		openAstro.makeSVG()
		self.draw.queue_draw()
		self.draw.setSVG(self.tempfilename)
		return

	"""
	Export Function
	"""

	def doExport(self, widget):

		chooser = Gtk.FileChooserDialog(parent=self.window,title=None,action=Gtk.FileChooserAction.SAVE,
                                  buttons=(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,Gtk.STOCK_SAVE,Gtk.ResponseType.OK))
		chooser.set_current_folder(cfg.homedir)


		filter = Gtk.FileFilter()
		if widget.get_name() == 'exportPNG':
			chooser.set_current_name(openAstro.name+'.png')
			filter.set_name(_("PNG Image Files (*.png)"))
			filter.add_mime_type("image/png")
			filter.add_pattern("*.png")
		elif widget.get_name() == 'exportJPG':
			chooser.set_current_name(openAstro.name+'.jpg')
			filter.set_name(_("JPG Image Files (*.jpg)"))
			filter.add_mime_type("image/jpeg")
			filter.add_pattern("*.jpg")
			filter.add_pattern("*.jpeg")
		elif widget.get_name() == 'exportSVG':
			chooser.set_current_name(openAstro.name+'.svg')
			filter.set_name(_("SVG Image Files (*.svg)"))
			filter.add_mime_type("image/svg+xml")
			filter.add_pattern("*.svg")
		elif widget.get_name() == 'exportXML':
			chooser.set_current_name(openAstro.name+'.oac')
			filter.set_name(_("OpenAstro Charts (*.oac)"))
			filter.add_mime_type("text/xml")
			filter.add_pattern("*.oac")
		chooser.add_filter(filter)

		filter = Gtk.FileFilter()
		filter.set_name(_("All files (*)"))
		filter.add_pattern("*")
		chooser.add_filter(filter)

		response = chooser.run()

		if response == Gtk.ResponseType.OK:
			if widget.get_name() == 'exportSVG':
				copyfile(cfg.tempfilename, chooser.get_filename())
			elif widget.get_name() == 'exportPNG':
				os.system("%s %s %s" % ('convert',cfg.tempfilename,"'"+chooser.get_filename()+"'"))
			elif widget.get_name() == 'exportJPG':
				os.system("%s %s %s" % ('convert',cfg.tempfilename,"'"+chooser.get_filename()+"'"))
			elif widget.get_name() == 'exportXML':
				openAstro.exportOAC(chooser.get_filename())
		elif response == Gtk.ResponseType.CANCEL:
					dprint('Dialog closed, no files selected')

		chooser.destroy()
		return

	def doImport(self, widget):

		chooser = Gtk.FileChooserDialog(parent=self.window,title=_('Select file to open'),action=Gtk.FileChooserAction.OPEN,
                                  buttons=(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
		chooser.set_current_folder(cfg.homedir)

		filter = Gtk.FileFilter()
		if widget.get_name() == 'importXML':
			filter.set_name(_("OpenAstro Charts (*.oac)"))
			#filter.add_mime_type("text/xml")
			filter.add_pattern("*.oac")
		elif widget.get_name() == 'importOroboros':
			filter.set_name(_("Oroboros Charts (*.xml)"))
			#filter.add_mime_type("text/xml")
			filter.add_pattern("*.xml")
		elif widget.get_name() == 'importSkylendar':
			filter.set_name(_("Skylendar Charts (*.skif)"))
			filter.add_pattern("*.skif")
		elif widget.get_name() == 'importAstrolog32':
			filter.set_name(_("Astrolog32 Charts (*.dat)"))
			filter.add_pattern("*.dat")
		elif widget.get_name() == 'importZet8':
			filter.set_name(_("Zet8 Databases (*.zbs)"))
			filter.add_pattern("*.zbs")
		chooser.add_filter(filter)
		response = chooser.run()

		if response == Gtk.ResponseType.OK:
			if widget.get_name() == 'importXML':
				openAstro.importOAC(chooser.get_filename())
			elif widget.get_name() == 'importOroboros':
				openAstro.importOroboros(chooser.get_filename())
			elif widget.get_name() == 'importSkylendar':
				openAstro.importSkylendar(chooser.get_filename())
			elif widget.get_name() == 'importAstrolog32':
				openAstro.importAstrolog32(chooser.get_filename())
			elif widget.get_name() == 'importZet8':
				openAstro.importZet8(chooser.get_filename())
			self.updateChart()
		elif response == Gtk.ResponseType.CANCEL:
					dprint('Dialog closed, no files selected')
		chooser.destroy()
		return

	def specialRadix(self, widget):
		openAstro.type="Radix"
		openAstro.charttype=openAstro.label["radix"]
		openAstro.transit=False
		openAstro.makeSVG()
		self.draw.queue_draw()
		self.draw.setSVG(self.tempfilename)

	def specialTransit(self, widget):
		openAstro.type="Transit"
		openAstro.t_geolon=float(openAstro.home_geolon)
		openAstro.t_geolat=float(openAstro.home_geolat)

		now = datetime.datetime.now()
		timezone_str = zonetab.nearest_tz(openAstro.t_geolat,openAstro.t_geolon,zonetab.timezones())[2]
		#aware datetime object
		dt_input = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)
		dt = pytz.timezone(timezone_str).localize(dt_input)
		#naive utc datetime object
		dt_utc = dt.replace(tzinfo=None) - dt.utcoffset()
		#transit data
		openAstro.t_year=dt_utc.year
		openAstro.t_month=dt_utc.month
		openAstro.t_day=dt_utc.day
		openAstro.t_hour=openAstro.decHourJoin(dt_utc.hour,dt_utc.minute,dt_utc.second)
		openAstro.t_timezone=openAstro.offsetToTz(dt.utcoffset())
		openAstro.t_altitude=25

		#make svg with transit
		openAstro.charttype="%s (%s-%02d-%02d %02d:%02d)" % (openAstro.label["transit"],dt.year,dt.month,dt.day,dt.hour,dt.minute)
		openAstro.transit=True
		openAstro.makeSVG()
		self.draw.queue_draw()
		self.draw.setSVG(self.tempfilename)

	def specialSolar(self, widget):
		# create a new window
		self.win_SS = Gtk.Dialog()
		self.win_SS.set_icon_from_file(cfg.iconWindow)
		self.win_SS.set_title(_("Select year for Solar Return"))
		self.win_SS.connect("delete_event", lambda w,e: self.win_SS.destroy())
		self.win_SS.move(150,150)
		self.win_SS.set_border_width(5)
		self.win_SS.set_size_request(300,100)

		#create a table
		table = Gtk.Table(2, 1, False)
		table.set_col_spacings(0)
		table.set_row_spacings(0)
		table.set_border_width(10)

		#options
		table.attach(Gtk.Label(_("Select year for Solar Return")), 0, 1, 0, 1, xoptions=Gtk.AttachOptions.SHRINK, yoptions=Gtk.AttachOptions.SHRINK, xpadding=10)
		entry=Gtk.Entry()
		entry.set_max_length(4)
		entry.set_width_chars(4)
		entry.set_text(str(datetime.datetime.now().year))
		table.attach(entry, 1, 2, 0, 1, xoptions=Gtk.AttachOptions.SHRINK, yoptions=Gtk.AttachOptions.SHRINK, xpadding=10)

		#make the ui layout with ok button
		self.win_SS.vbox.pack_start(table, True, True, 0)

		#ok button
		button = Gtk.Button(stock=Gtk.STOCK_OK)
		button.connect("clicked", self.specialSolarSubmit, entry)
		button.set_can_default(True)
		self.win_SS.action_area.pack_start(button, True, True, 0)
		button.grab_default()

		#cancel button
		button = Gtk.Button(stock=Gtk.STOCK_CANCEL)
		button.connect("clicked", lambda w: self.win_SS.destroy())
		self.win_SS.action_area.pack_start(button, True, True, 0)

		self.win_SS.show_all()
		return

	def specialSolarSubmit(self, widget, entry):
		intyear = int(entry.get_text())
		openAstro.localToSolar(intyear)
		self.win_SS.destroy()
		self.updateChart()
		return

	def specialSecondaryProgression(self, widget):
		# create a new window
		self.win_SSP = Gtk.Dialog(parent=self.window)
		self.win_SSP.set_icon_from_file(cfg.iconWindow)
		self.win_SSP.set_title(_("Enter Date"))
		self.win_SSP.connect("delete_event", lambda w,e: self.win_SSP.destroy())
		self.win_SSP.move(150,150)
		self.win_SSP.set_border_width(5)
		self.win_SSP.set_size_request(320,180)

		#create a table
		table = Gtk.Table(1, 4, False)
		table.set_col_spacings(0)
		table.set_row_spacings(0)
		table.set_border_width(10)

		#options
		table.attach(Gtk.Label(_("Select date for Secondary Progression")+":"), 0, 1, 0, 1, xoptions=Gtk.AttachOptions.SHRINK, yoptions=Gtk.AttachOptions.SHRINK, xpadding=10, ypadding=10)
		hbox = Gtk.HBox(spacing=4)  # pack_start(child, expand=True, fill=True, padding=0)
		entry={}

		hbox.pack_start(Gtk.Label(_('Year')+": "), False, False, 0)
		entry['Y']=Gtk.Entry()
		entry['Y'].set_max_length(4)
		entry['Y'].set_width_chars(4)
		entry['Y'].set_text(str(datetime.datetime.now().year))
		hbox.pack_start(entry['Y'], False, False, 0)
		hbox.pack_start(Gtk.Label(_('Month')+": "), False, False, 0)
		entry['M']=Gtk.Entry()
		entry['M'].set_max_length(2)
		entry['M'].set_width_chars(2)
		entry['M'].set_text('%02d'%(datetime.datetime.now().month))
		hbox.pack_start(entry['M'], False, False, 0)
		hbox.pack_start(Gtk.Label(_('Day')+": "), False, False, 0)
		entry['D']=Gtk.Entry()
		entry['D'].set_max_length(2)
		entry['D'].set_width_chars(2)
		entry['D'].set_text(str(datetime.datetime.now().day))
		hbox.pack_start(entry['D'], False, False, 0)
		table.attach(hbox,0,1,1,2, xoptions=Gtk.AttachOptions.SHRINK, yoptions=Gtk.AttachOptions.SHRINK, xpadding=10, ypadding=10)

		hbox = Gtk.HBox(spacing=4)
		hbox.pack_start(Gtk.Label(_('Hour')+": "), False, False, 0)
		entry['h']=Gtk.Entry()
		entry['h'].set_max_length(2)
		entry['h'].set_width_chars(2)
		entry['h'].set_text('%02d'%(datetime.datetime.now().hour))
		hbox.pack_start(entry['h'], False, False, 0)
		hbox.pack_start(Gtk.Label(_('Min')+": "), False, False, 0)
		entry['m']=Gtk.Entry()
		entry['m'].set_max_length(2)
		entry['m'].set_width_chars(2)
		entry['m'].set_text('%02d'%(datetime.datetime.now().minute))
		hbox.pack_start(entry['m'], False, False, 0)
		table.attach(hbox,0,1,2,3, xoptions=Gtk.AttachOptions.SHRINK, yoptions=Gtk.AttachOptions.SHRINK, xpadding=10, ypadding=10)

		#make the ui layout with ok button
		self.win_SSP.vbox.pack_start(table, True, True, 0)

		#ok button
		button = Gtk.Button(stock=Gtk.STOCK_OK)
		button.connect("clicked", self.specialSecondaryProgressionSubmit, entry)
		button.set_can_default(True)
		self.win_SSP.action_area.pack_start(button, True, True, 0)
		button.grab_default()

		#cancel button
		button = Gtk.Button(stock=Gtk.STOCK_CANCEL)
		button.connect("clicked", lambda w: self.win_SSP.destroy())
		self.win_SSP.action_area.pack_start(button, True, True, 0)

		self.win_SSP.show_all()
		return

	def specialSecondaryProgressionSubmit(self, widget, entry):
		dt	= datetime.datetime(int(entry['Y'].get_text()),int(entry['M'].get_text()),int(entry['D'].get_text()),int(entry['h'].get_text()),int(entry['m'].get_text()))
		openAstro.localToSecondaryProgression(dt)
		self.win_SSP.destroy()
		self.updateChart()
		return

	def tableMonthlyTimeline(self, widget):
		dialog = Gtk.Dialog(_("Select Month"),
                     self.window,
                     0,
                     (Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                      Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))

		dialog.set_destroy_with_parent(True)
		dialog.connect("destroy", lambda w: dialog.destroy())
		dialog.set_size_request(200, 200)
		dialog.move(50,50)
		self.tMTentry={}
		dialog.vbox.pack_start(Gtk.Label(_('Year')+": "), False, False, 0)
		self.tMTentry['Y']=Gtk.Entry()
		self.tMTentry['Y'].set_max_length(4)
		self.tMTentry['Y'].set_width_chars(4)
		self.tMTentry['Y'].set_text(str(datetime.datetime.now().year))
		dialog.vbox.pack_start(self.tMTentry['Y'], False, False, 0)
		dialog.vbox.pack_start(Gtk.Label(_('Month')+": "), False, False, 0)
		self.tMTentry['M']=Gtk.Entry()
		self.tMTentry['M'].set_max_length(2)
		self.tMTentry['M'].set_width_chars(2)
		self.tMTentry['M'].set_text('%02d'%(datetime.datetime.now().month))
		dialog.vbox.pack_start(self.tMTentry['M'], False, False, 0)
		dialog.show_all()

		ret = dialog.run()
		if ret == Gtk.ResponseType.ACCEPT:
			self.tMTentry['Y']=self.tMTentry['Y'].get_text()
			self.tMTentry['M']=self.tMTentry['M'].get_text()
			dialog.destroy()
			self.tableMonthlyTimelineShow()
		else:
			dialog.destroy()
		return

	def tableMonthlyTimelinePrint(self, pages, pdf, window, name):
		settings = None
		print_op = Gtk.PrintOperation()
		print_op.set_unit(Gtk.Unit.MM)
		if settings != None:
			print_op.set_print_settings(settings)
		print_op.connect("begin_print", self.tableMonthlyTimelinePrintBegin, pages)
		print_op.connect("draw_page", self.tableMonthlyTimelinePrintDraw)

		if pdf:
			chooser = Gtk.FileChooserDialog(title=_("Select Export Filename"),action=Gtk.FileChooserAction.SAVE,
                                  buttons=(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,Gtk.STOCK_SAVE,Gtk.ResponseType.OK))
			chooser.set_current_folder(cfg.homedir)
			chooser.set_current_folder(cfg.homedir)
			chooser.set_current_name(name)
			filter = Gtk.FileFilter()
			filter.set_name(_("PDF Files (*.pdf)"))
			filter.add_pattern("*.pdf")
			chooser.add_filter(filter)
			response = chooser.run()
			if response == Gtk.ResponseType.OK:
				print_op.set_export_filename(chooser.get_filename())
				chooser.destroy()
				res = print_op.run(Gtk.PrintOperationAction.EXPORT, window)
			else:
				chooser.destroy()
				print_op.cancel()
				res = None

		else:
			res = print_op.run(Gtk.PrintOperationAction.PRINT_DIALOG, window)

		if res == Gtk.PrintOperationResult.ERROR:
			error_dialog = Gtk.MessageDialog(window,0,Gtk.MESSAGE_ERROR,Gtk.ButtonS_CLOSE,"Error printing:\n")
			error_dialog.set_destroy_with_parent(True)
			error_dialog.connect("response", lambda w,id: w.destroy())
			error_dialog.show()
		elif res == Gtk.PrintOperationResult.APPLY:
			settings = print_op.get_print_settings()


	def tableMonthlyTimelinePrintBegin(self, operation, context, pages):
		operation.set_n_pages(pages)
		operation.set_use_full_page(False)
		ps = Gtk.PageSetup()
		ps.set_orientation(Gtk.PageOrientation.PORTRAIT)
		ps.set_paper_size(Gtk.PaperSize(Gtk.PAPER_NAME_A4))
		operation.set_default_page_setup(ps)

	def tableMonthlyTimelinePrintDraw(self, operation, context, page_nr):
		cr = context.get_cairo_context()
		#draw svg
		printing={}
		printing['pagenum']=page_nr
		printing['width']=context.get_width()
		printing['height']=context.get_height()
		printing['dpi_x']=context.get_dpi_x()
		printing['dpi_y']=context.get_dpi_y()
		if(self.tabletype == "timeline"):
			self.tableMonthlyTimelineShow(printing)
			#draw svg for printing
			Rsvg.set_default_dpi(900)
			svg = Rsvg.Handle.new_from_file(cfg.tempfilenametableprint)
			svg.render_cairo(cr)
		elif(self.tabletype == "cuspaspects"):
			self.tableCuspAspects(None,printing)
			#draw svg for printing
			Rsvg.set_default_dpi(900)
			svg = Rsvg.Handle.new_from_file(cfg.tempfilenametableprint)
			svg.render_cairo(cr)


	def tableMonthlyTimelineShow(self, printing=None):
		self.tabletype="timeline"
		y = int(self.tMTentry['Y'])
		m = int(self.tMTentry['M'])
		tz = datetime.timedelta(seconds=float(openAstro.timezone)*float(3600))
		startdate = datetime.datetime(y,m,1,12) - tz
		q,r = divmod(startdate.month, 12)
		enddate = datetime.datetime(startdate.year+q, r+1, 1,12)
		delta = enddate - startdate
		atgrid={}
		astypes={}
		retrogrid={}
		for d in range(delta.days):
			cdate = startdate + datetime.timedelta(days=d)
			tmoddata = ephemeris.ephData(cdate.year,cdate.month,cdate.day,cdate.hour,
				openAstro.geolon,openAstro.geolat,openAstro.altitude,openAstro.planets,
				openAstro.zodiac,db.astrocfg)
			#planets_sign,planets_degree,planets_degree_ut,planets_retrograde,houses_degree
			#houses_sign,houses_degree_ut

			for i in range(len(openAstro.planets)):
				start=openAstro.planets_degree_ut[i]
				for x in range(i+1):
					end=tmoddata.planets_degree_ut[x]
					diff=float(openAstro.degreeDiff(start,end))
					#skip asc/dsc/mc/ic on tmoddata
					if 23 <= x <= 26:
						continue
					#skip moon on tmoddate
					if x == 1:
						continue
					#loop orbs
					if (openAstro.planets[i]['visible'] == 1) & (openAstro.planets[x]['visible'] == 1):
						for z in range(len(openAstro.aspects)):
							#only major aspects
							if openAstro.aspects[z]['is_major'] != 1:
								continue
							#check for personal planets and determine orb
							orb_before = 4
							orb_after = 4
							#check if we want to display this aspect
							if	( float(openAstro.aspects[z]['degree']) - orb_before ) <= diff <= ( float(openAstro.aspects[z]['degree']) + orb_after ):
								orb = diff - openAstro.aspects[z]['degree']
								if orb < 0:
									orb = orb/-1
								#aspect grid dictionary
								s="%02d%02d%02d"%(i,z,x)
								astypes[s]=(i,x,z)

								if s not in retrogrid:
									retrogrid[s]={}
								retrogrid[s][d]=tmoddata.planets_retrograde[x]

								if s not in atgrid:
									atgrid[s]={}
								atgrid[s][d]=orb
		#sort
		keys = list(astypes.keys())
		keys.sort()
		pages = int(math.ceil(len(keys)/65.0))

		out = ""
		#make numbers of days in month
		dx=[80]
		skipdays = [9,19]
		for d in range(delta.days):
			if d in skipdays:
				dx.append(dx[-1]+40)
			else:
				dx.append(dx[-1]+20)

		for p in range(pages):
			if p == 0:
				ystart = 10
			else:
				ystart = (1188 * p) + 62
			pagelen = (len(keys)+1)-p*65
			if pagelen > 65:
				pagelen = 66
			ylen = ((len(keys)+1)-p*65)*16
			for a in range(delta.days):
				out += '<text x="%s" y="%s" style="fill: %s; font-size: 10">%02d</text>\n'%(
					dx[a],ystart,openAstro.colors['paper_0'],a+1)
				out += '<line x1="%s" y1="%s" x2="%s" y2="%s" style="stroke: %s; stroke-width: .5; stroke-opacity:1;"/>\n'%(
					dx[a]-5,ystart,dx[a]-5,ystart+pagelen*16,openAstro.colors['paper_0'])
				#skipdays line
				if a in skipdays:
					out += '<line x1="%s" y1="%s" x2="%s" y2="%s" style="stroke: %s; stroke-width: .5; stroke-opacity:1;"/>\n'%(
						dx[a]-5+20,ystart,dx[a]-5+20,ystart+pagelen*16,openAstro.colors['paper_0'])


			#last line
			out += '<line x1="%s" y1="%s" x2="%s" y2="%s" style="stroke: %s; stroke-width: .5; stroke-opacity:1;"/>\n'%(
					dx[-1]-5,ystart,dx[-1]-5,ystart+pagelen*16,openAstro.colors['paper_0'])

		#get the number of total aspects
		c = 0
		for m in range(len(keys)):
			i,x,z = astypes[keys[m]]
			c += 1
			pagenum = int(math.ceil(c/65.0))
			pagey = (pagenum - 1) * 200
			y = (c*16) + pagey
			#horizontal lines
			out += '<line x1="%s" y1="%s" x2="%s" y2="%s" style="stroke: %s; stroke-width: .5; stroke-opacity:1;"/>\n'%(
				0,y-1,dx[skipdays[0]]+15,y-1,openAstro.colors['paper_0'])
			for s in range(len(skipdays)):
				if s is len(skipdays)-1:
					out += '<line x1="%s" y1="%s" x2="%s" y2="%s" style="stroke: %s; stroke-width: .5; stroke-opacity:1;"/>\n'%(
						dx[skipdays[s]+1]-5,y-1,dx[-1],y-1,openAstro.colors['paper_0'])
				else:
					out += '<line x1="%s" y1="%s" x2="%s" y2="%s" style="stroke: %s; stroke-width: .5; stroke-opacity:1;"/>\n'%(
						dx[skipdays[s]+1]-5,y-1,dx[skipdays[s+1]]+15,y-1,openAstro.colors['paper_0'])
			#outer planet
			out += '<g transform="translate(0,%s)"><g transform="scale(.5)"><use x="0" y="0" xlink:href="#%s" /></g></g>\n'%(
				y,openAstro.planets[x]['name'])
			#aspect
			out += '<g><use x="20" y="%s" xlink:href="#orb%s" /></g>\n'%(
				y,openAstro.aspects[z]['degree'])
			#inner planet
			out += '<g transform="translate(40,%s)"><g transform="scale(.5)"><use x="0" y="0" xlink:href="#%s" /></g></g>\n'%(y,
				openAstro.planets[i]['name'])
			for d in range(delta.days):
				if d in atgrid[keys[m]]:
					orb = atgrid[keys[m]][d]
					op = .1+(.7-(orb/(4/.7))) #4 is maxorb
					if op > 1:
						op = 1
					strop = str(float(orb))
					out += '<rect x="%s" y="%s" width="20" height="16" style="fill: %s; fill-opacity:%s;" />'%(
						dx[d]-5,y-1,openAstro.colors["aspect_%s" %(openAstro.aspects[z]['degree'])],op)
					#check for retrograde outer planet
					if retrogrid[keys[m]][d]:
						out += '<g transform="translate(%s,%s)"><g transform="scale(.3)">\
							<use x="0" y="0" xlink:href="#retrograde" style="fill:%s; fill-opacity:.8;" /></g></g>\n'%(
							dx[d]+10,y+10,openAstro.colors['paper_0'],)
					out += '<text x="%s" y="%s" style="fill: %s; font-size: 10">%s</text>\n'%(
						dx[d],y+9,openAstro.colors['paper_0'],strop[:3])

				else:
					out += ""

		#template
		td = {}
		td['paper_color_0']=openAstro.colors["paper_0"]
		td['paper_color_1']=openAstro.colors["paper_1"]
		for i in range(len(openAstro.planets)):
			td['planets_color_%s'%(i)]=openAstro.colors["planet_%s"%(i)]
		for i in range(12):
			td['zodiac_color_%s'%(i)]=openAstro.colors["zodiac_icon_%s" %(i)]
		for i in range(len(openAstro.aspects)):
			td['orb_color_%s'%(openAstro.aspects[i]['degree'])]=openAstro.colors["aspect_%s" %(openAstro.aspects[i]['degree'])]
		td['stringTitle'] = "%s Timeline for %s"%(
			startdate.strftime("%B %Y"),openAstro.name)

		pagesY = (1188 * pages)+10 #ten is buffer between pages
		if printing: # why hardcoded page size values?
			td['svgWidth'] = printing['width']
			td['svgHeight'] = printing['height']
			td['viewbox'] = "0 %s 840 1188" %( printing['pagenum']*(1188+10) )
		else:
			td['svgWidth'] = 1050
			td['svgHeight'] = (td['svgWidth']/840.0)* pagesY
			td['viewbox'] = "0 0 840 %s" %( pagesY )


		td['data'] = out

		#pages rectangles
		pagesRect,x,y,w,h="",0,0,840,1188
		for p in range(pages):
			if p == 0:
				offset=0
			else:
				offset=10
			pagesRect += '<rect x="%s" y="%s" width="%s" height="%s" style="fill: %s;" />'%(
				x,y+(p*1188)+offset,w,h,openAstro.colors['paper_1'],)

		td['pagesRect'] = pagesRect

		#read and write template
		f=open(cfg.xml_svg_table)
		template=Template(f.read()).substitute(td)
		f.close()
		if printing:
			f=open(cfg.tempfilenametableprint,"w")
		else:
			f=open(cfg.tempfilenametable,"w")
		f.write(template)
		f.close()

		if printing == None:
			self.win_TMT = Gtk.Window(Gtk.WindowType.TOPLEVEL)
			self.win_TMT.connect("destroy", lambda w: self.win_TMT.destroy())
			self.win_TMT.set_title("OpenAstro.org Timeline")
			self.win_TMT.set_icon_from_file(cfg.iconWindow)
			self.win_TMT.set_size_request(td['svgWidth']+30, 700)
			self.win_TMT.move(50,50)
			vbox = Gtk.VBox()
			hbox = Gtk.HBox()
			button = Gtk.Button(_('Print'))
			button.connect("clicked", lambda w: self.tableMonthlyTimelinePrint(pages,pdf=False,window=self.win_TMT,name="timeline-%s.pdf"%(openAstro.name)))
			hbox.pack_start(button,False,False,0)
			button = Gtk.Button(_('Save as PDF'))
			button.connect("clicked", lambda w: self.tableMonthlyTimelinePrint(pages,pdf=True,window=self.win_TMT,name="timeline-%s.pdf"%(openAstro.name)))
			hbox.pack_start(button,False,False,0)
			vbox.pack_start(hbox,False,False,0)
			draw = drawSVG()
			draw.setSVG(cfg.tempfilenametable)
			scrolledwindow = Gtk.ScrolledWindow()
			scrolledwindow.add_with_viewport(draw)
			scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
			vbox.pack_start(scrolledwindow, True, True, 0)

			self.win_TMT.add(vbox)
			self.win_TMT.show_all()
		return

	def tableCuspAspects(self, widget, printing=None):
		self.tabletype="cuspaspects"
		#data
		out='<g transform="scale(1.5)">'
		xindent=50
		yindent=200
		box=14
		style='stroke:%s; stroke-width: 1px; stroke-opacity:.6; fill:none' % (openAstro.colors['paper_0'],)
		textstyle="font-size: 11px; color: %s" % (openAstro.colors['paper_0'],)
		#draw cusps
		for cusp in range(len(openAstro.houses_degree_ut)):
				x = xindent - box
				y = yindent - (box*(cusp+1))
				out += '<text \
						x="%s" \
						y="%s" \
						style="%s">%s</text>\n\
						'%(x-30, y+box-5, textstyle, openAstro.label['cusp']+" "+str(cusp+1))

		revr=range(len(openAstro.planets))
		for a in revr:
			if 23 <= a <= 26:
				continue; #skip asc/dsc/mc/ic
			if a == 11 or a == 13 or a == 21 or a == 22:
				continue; #skip ?,?,intp. apogee, intp. perigee

			start=openAstro.planets_degree_ut[a]
			#first planet
			out += '<rect x="%s" \
						y="%s" \
						width="%s" \
						height="%s" \
						style="%s"/>\n' %(xindent,yindent,box,box,style)
			out += '<use transform="scale(0.4)" \
					x="%s" \
					y="%s" \
					xlink:href="#%s" />\n\
					'%((xindent+2)*2.5, (yindent+1)*2.5, openAstro.planets[a]['name'])

			yorb=yindent - box
			for b in range(12):
				end=openAstro.houses_degree_ut[b]
				diff=openAstro.degreeDiff(start,end)
				out += '<rect x="%s" \
					y="%s" \
					width="%s" \
					height="%s" \
					style="%s"/>\n\
					'%(xindent,yorb,box,box,style)
				for z in range(len(openAstro.aspects)):
					if	( float(openAstro.aspects[z]['degree']) - float(openAstro.aspects[z]['orb']) ) <= diff <= ( float(openAstro.aspects[z]['degree']) + float(openAstro.aspects[z]['orb']) ) and openAstro.aspects[z]['visible_grid'] == 1:
							out += '<use \
								x="%s" \
								y="%s" \
								xlink:href="#orb%s" />\n\
								'%(xindent,yorb+1,openAstro.aspects[z]['degree'])
				yorb=yorb-box

			xindent += box

		#add cusp to cusp
		xindent = 50
		yindent = 400
		#draw cusps
		for cusp in range(len(openAstro.houses_degree_ut)):
				x = xindent - box
				y = yindent - (box*(cusp+1))
				out += '<text \
						x="%s" \
						y="%s" \
						style="%s">%s</text>\n\
						'%(x-30, y+box-5, textstyle, openAstro.label['cusp']+" "+str(cusp+1))

		for a in range(12):
			start=openAstro.houses_degree_ut[a]
			#first planet
			out += '<rect x="%s" \
						y="%s" \
						width="%s" \
						height="%s" \
						style="%s"/>\n' %(xindent,yindent,box,box,style)
			out += '<text \
						x="%s" \
						y="%s" \
						style="%s">%s</text>\n\
						'%((xindent+2), (yindent+box-4), textstyle, ""+str(a+1))

			yorb=yindent - box
			for b in range(12):
				end=openAstro.houses_degree_ut[b]
				diff=openAstro.degreeDiff(start,end)
				out += '<rect x="%s" \
					y="%s" \
					width="%s" \
					height="%s" \
					style="%s"/>\n\
					'%(xindent,yorb,box,box,style)
				for z in range(len(openAstro.aspects)):
					if	( float(openAstro.aspects[z]['degree']) - float(openAstro.aspects[z]['orb']) ) <= diff <= ( float(openAstro.aspects[z]['degree']) + float(openAstro.aspects[z]['orb']) ) and openAstro.aspects[z]['visible_grid'] == 1:
							out += '<use \
								x="%s" \
								y="%s" \
								xlink:href="#orb%s" />\n\
								'%(xindent,yorb+1,openAstro.aspects[z]['degree'])
				yorb=yorb-box

			xindent += box

		out += "</g>"


		#template
		td = {}
		td['paper_color_0']=openAstro.colors["paper_0"]
		td['paper_color_1']=openAstro.colors["paper_1"]
		for i in range(len(openAstro.planets)):
			td['planets_color_%s'%(i)]=openAstro.colors["planet_%s"%(i)]
		for i in range(12):
			td['zodiac_color_%s'%(i)]=openAstro.colors["zodiac_icon_%s" %(i)]
		for i in range(len(openAstro.aspects)):
			td['orb_color_%s'%(openAstro.aspects[i]['degree'])]=openAstro.colors["aspect_%s" %(openAstro.aspects[i]['degree'])]
		td['stringTitle'] = "Cusp Aspects for %s"%(openAstro.name)

		pages=1
		pagesY = (1188 * pages)+10 #ten is buffer between pages
		if printing:
			td['svgWidth'] = printing['width']
			td['svgHeight'] = printing['height']
			td['viewbox'] = "0 %s 840 1188" %( printing['pagenum']*(1188+10) )
		else:
			td['svgWidth'] = 1050
			td['svgHeight'] = (td['svgWidth']/840.0)* pagesY
			td['viewbox'] = "0 0 840 %s" %( pagesY )

		td['data'] = out
		td['pagesRect'] = '<rect x="0" y="0" width="840" height="1188" style="fill: %s;" />' % (openAstro.colors['paper_1'],)

		#read and write template
		f=open(cfg.xml_svg_table)
		template=Template(f.read()).substitute(td)
		f.close()
		if printing:
			f=open(cfg.tempfilenametableprint,"w")
		else:
			f=open(cfg.tempfilenametable,"w")
		f.write(template)
		f.close()

		#display svg
		if printing == None:
			self.win_TCA = Gtk.Window(Gtk.WindowType.TOPLEVEL)
			self.win_TCA.connect("destroy", lambda w: self.win_TCA.destroy())
			self.win_TCA.set_title("OpenAstro.org Cusp Aspects")
			self.win_TCA.set_icon_from_file(cfg.iconWindow)
			self.win_TCA.set_size_request(td['svgWidth']+30, 700)
			self.win_TCA.move(50,50)
			vbox = Gtk.VBox()
			hbox = Gtk.HBox()
			button = Gtk.Button(_('Print'))
			button.connect("clicked", lambda w: self.tableMonthlyTimelinePrint(pages=1,pdf=False,window=self.win_TCA,name="cusp-aspects-%s.pdf"%(openAstro.name)))
			hbox.pack_start(button,False,False,0)
			button = Gtk.Button(_('Save as PDF'))
			button.connect("clicked", lambda w: self.tableMonthlyTimelinePrint(pages=1,pdf=True,window=self.win_TCA,name="cusp-aspects-%s.pdf"%(openAstro.name)))
			hbox.pack_start(button,False,False,0)
			vbox.pack_start(hbox,False,False,0)
			draw = drawSVG()
			draw.setSVG(cfg.tempfilenametable)
			scrolledwindow = Gtk.ScrolledWindow()
			scrolledwindow.add_with_viewport(draw)
			scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
			vbox.pack_start(scrolledwindow,True,True,0)
			self.win_TCA.add(vbox)
			self.win_TCA.show_all()
		return

	def aboutInfo(self, widget):
		dialog=Gtk.Dialog('Info',self.window,0,(Gtk.STOCK_OK, Gtk.ResponseType.DELETE_EVENT))
		dialog.set_icon_from_file(cfg.iconWindow)
		dialog.connect("response", lambda w,e: dialog.destroy())
		dialog.connect("close", lambda w,e: dialog.destroy())
		about_text = _('OpenAstro.org - Open Source Astrology')+'\n\n'+_('Version')+' '+cfg.version+'\n'+_('Author')+': Pelle van der Scheer'
		dialog.vbox.pack_start(Gtk.Label(about_text),True,True,0)
		dialog.show_all()
		return

	# def openDatabaseFamous(self, widget):
	# 	self.openDatabase(widget,db.getDatabaseFamous(limit="500"))

	# def nameSearch(self, widget):
	# 	self.listmodel.clear()
	# 	self.DB = db.getDatabaseFamous(limit="15",search=self.namesearch.get_text())
	# 	for i in range(len(self.DB)):
	# 		h,m,s = openAstro.decHour(float(self.DB[i]["hour"]))
	# 		dt_utc=datetime.datetime(int(self.DB[i]["year"]),int(self.DB[i]["month"]),int(self.DB[i]["day"]),h,m,s)
	# 		dt = dt_utc + datetime.timedelta(seconds=float(self.DB[i]["timezone"])*float(3600))
	# 		birth_date = str(dt.year)+'-%(#1)02d-%(#2)02d %(#3)02d:%(#4)02d:%(#5)02d' % {'#1':dt.month,'#2':dt.day,'#3':dt.hour,'#4':dt.minute,'#5':dt.second}
	# 		self.listmodel.append([self.DB[i]["name"],birth_date,self.DB[i]["location"],self.DB[i]["id"]])
	# 	return

	# def nameSearchReset(self, widget):
	# 	self.listmodel.clear()
	# 	self.DB = db.getDatabaseFamous(limit="500")
	# 	for i in range(len(self.DB)):
	# 		h,m,s = openAstro.decHour(float(self.DB[i]["hour"]))
	# 		dt_utc=datetime.datetime(int(self.DB[i]["year"]),int(self.DB[i]["month"]),int(self.DB[i]["day"]),h,m,s)
	# 		dt = dt_utc + datetime.timedelta(seconds=float(self.DB[i]["timezone"])*float(3600))
	# 		birth_date = str(dt.year)+'-%(#1)02d-%(#2)02d %(#3)02d:%(#4)02d:%(#5)02d' % {'#1':dt.month,'#2':dt.day,'#3':dt.hour,'#4':dt.minute,'#5':dt.second}
	# 		self.listmodel.append([self.DB[i]["name"],birth_date,self.DB[i]["location"],self.DB[i]["id"]])
	# 	return

	def openDatabase(self, widget, extraDB=None):
		self.win_OD = Gtk.Window(Gtk.WindowType.TOPLEVEL)
		self.win_OD.set_icon_from_file(cfg.iconWindow)
		self.win_OD.set_title(_('Open Database Entry'))
		self.win_OD.set_size_request(600, 450)
		self.win_OD.move(150,150)
		self.win_OD.connect("delete_event", lambda w,e: self.win_OD.destroy())
		#listmodel
		self.listmodel = Gtk.ListStore(str,str,str,int)
		self.win_OD_treeview = Gtk.TreeView(self.listmodel)
		#selection
		self.win_OD_selection = self.win_OD_treeview.get_selection()
		self.win_OD_selection.set_mode(Gtk.SelectionMode.SINGLE)
		#treeview columns
		self.win_OD_tvcolumn0 = Gtk.TreeViewColumn(_('Name'))
		self.win_OD_tvcolumn1 = Gtk.TreeViewColumn(_('Birth Date (Local)'))
		self.win_OD_tvcolumn2 = Gtk.TreeViewColumn(_('Location'))
		#add data from event_natal table
		if extraDB != None:
			self.win_OD_treeview.set_enable_search(False)
			self.DB = extraDB
		else:
			self.win_OD_treeview.set_enable_search(True)
			self.DB = db.getDatabase()

		for i in range(len(self.DB)):
			h,m,s = openAstro.decHour(float(self.DB[i]["hour"]))
			dt_utc=datetime.datetime(int(self.DB[i]["year"]),int(self.DB[i]["month"]),int(self.DB[i]["day"]),h,m,s)
			dt = dt_utc + datetime.timedelta(seconds=float(self.DB[i]["timezone"])*float(3600))
			birth_date = str(dt.year)+'-%(#1)02d-%(#2)02d %(#3)02d:%(#4)02d:%(#5)02d' % {'#1':dt.month,'#2':dt.day,'#3':dt.hour,'#4':dt.minute,'#5':dt.second}
			self.listmodel.append([self.DB[i]["name"],birth_date,self.DB[i]["location"],self.DB[i]["id"]])

		#add columns to treeview
		self.win_OD_treeview.append_column(self.win_OD_tvcolumn0)
		self.win_OD_treeview.append_column(self.win_OD_tvcolumn1)
		self.win_OD_treeview.append_column(self.win_OD_tvcolumn2)
		#cell renderers
		cell0 = Gtk.CellRendererText()
		cell1 = Gtk.CellRendererText()
		cell2 = Gtk.CellRendererText()
		#add cells to columns
		self.win_OD_tvcolumn0.pack_start(cell0, True)
		self.win_OD_tvcolumn1.pack_start(cell1, True)
		self.win_OD_tvcolumn2.pack_start(cell2, True)
		#set the cell attributes to the listmodel column
		self.win_OD_tvcolumn0.set_attributes(cell0, text=0)
		self.win_OD_tvcolumn1.set_attributes(cell1, text=1)
		self.win_OD_tvcolumn2.set_attributes(cell2, text=2)
		#set treeview options
		self.win_OD_treeview.set_search_column(0)
		self.win_OD_tvcolumn0.set_sort_column_id(0)
		self.win_OD_tvcolumn1.set_sort_column_id(1)
		self.win_OD_tvcolumn2.set_sort_column_id(2)
		#add treeview to scrolledwindow
		scrolledwindow = Gtk.ScrolledWindow()
		scrolledwindow.add(self.win_OD_treeview)
		scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)
		vbox=Gtk.VBox()
		vbox.pack_start(scrolledwindow,True,True,0)
		hbox=Gtk.HBox(False,4)
		#buttons
		if extraDB == None:
			button = Gtk.Button(stock=Gtk.STOCK_CANCEL)
			button.connect("clicked", lambda w: self.win_OD.destroy())
			hbox.pack_end(button,False,False,0)
			button = Gtk.Button(stock=Gtk.STOCK_EDIT)
			button.connect("clicked", self.openDatabaseEdit)
			hbox.pack_end(button,False,False,0)
			button = Gtk.Button(stock=Gtk.STOCK_DELETE)
			button.connect("clicked", self.openDatabaseDel)
			hbox.pack_end(button,False,False,0)
			button = Gtk.Button(stock=Gtk.STOCK_OPEN)
			button.connect("clicked", self.openDatabaseOpen)
			hbox.pack_end(button,False,False,0)
		else:
			label=Gtk.Label(_("Search Name")+":")
			self.namesearch = Gtk.Entry()
			self.namesearch.set_max_length(34)
			self.namesearch.set_width_chars(24)
			self.namesearchbutton = Gtk.Button(_('Search'))
			self.namesearchbutton.connect("clicked", self.nameSearch)
			self.namesearch.connect("activate", self.nameSearch)
			self.nameresetbutton = Gtk.Button(_('Reset'))
			self.nameresetbutton.connect("clicked", self.nameSearchReset)

			hbox.pack_end(self.nameresetbutton,False,False,0)
			hbox.pack_end(self.namesearchbutton,False,False,0)
			hbox.pack_end(self.namesearch,False,False,0)
			hbox.pack_end(label,False,False,0)

			button = Gtk.Button(stock=Gtk.STOCK_OPEN)
			button.connect("clicked", self.openDatabaseOpen)
			hbox.pack_start(button,False,False,0)
			button = Gtk.Button(stock=Gtk.STOCK_CLOSE)
			button.connect("clicked", lambda w: self.win_OD.destroy())
			hbox.pack_start(button,False,False,0)


		#display window
		self.win_OD_treeview.connect("row-activated", lambda w,e,f: self.openDatabaseOpen(w))
		vbox.pack_start(hbox,False,False,0)
		self.win_OD.add(vbox)
		self.win_OD_treeview.set_model(self.listmodel)
		self.win_OD.show_all()
		return

	def openDatabaseSelect(self, selectstr, type):

		self.win_OD = Gtk.Window(Gtk.WindowType.TOPLEVEL)
		self.win_OD.set_icon_from_file(cfg.iconWindow)
		self.win_OD.set_title(_('Select Database Entry'))
		self.win_OD.set_size_request(400, 450)
		self.win_OD.move(150,150)
		self.win_OD.connect("delete_event", lambda w,e: self.openDatabaseSelectReject())
		#listmodel
		listmodel = Gtk.ListStore(str,str,str,int)
		self.win_OD_treeview = Gtk.TreeView(listmodel)

		#selection
		self.win_OD_selection = self.win_OD_treeview.get_selection()
		self.win_OD_selection.set_mode(Gtk.SelectionMode.SINGLE)
		#treeview columns
		self.win_OD_tvcolumn0 = Gtk.TreeViewColumn(_('Name'))
		self.win_OD_tvcolumn1 = Gtk.TreeViewColumn(_('Birth Date (Local)'))
		self.win_OD_tvcolumn2 = Gtk.TreeViewColumn(_('Location'))
		#add data from event_natal table
		self.DB = db.getDatabase()
		for i in range(len(self.DB)):
			h,m,s = openAstro.decHour(float(self.DB[i]["hour"]))
			dt_utc=datetime.datetime(int(self.DB[i]["year"]),int(self.DB[i]["month"]),int(self.DB[i]["day"]),h,m,s)
			dt = dt_utc + datetime.timedelta(seconds=float(self.DB[i]["timezone"])*float(3600))
			birth_date = str(dt.year)+'-%(#1)02d-%(#2)02d %(#3)02d:%(#4)02d:%(#5)02d' % {'#1':dt.month,'#2':dt.day,'#3':dt.hour,'#4':dt.minute,'#5':dt.second}
			listmodel.append([self.DB[i]["name"],birth_date,self.DB[i]["location"],self.DB[i]["id"]])
		#add columns to treeview
		self.win_OD_treeview.append_column(self.win_OD_tvcolumn0)
		self.win_OD_treeview.append_column(self.win_OD_tvcolumn1)
		self.win_OD_treeview.append_column(self.win_OD_tvcolumn2)
		#cell renderers
		cell0 = Gtk.CellRendererText()
		cell1 = Gtk.CellRendererText()
		cell2 = Gtk.CellRendererText()
		#add cells to columns
		self.win_OD_tvcolumn0.pack_start(cell0, True)
		self.win_OD_tvcolumn1.pack_start(cell1, True)
		self.win_OD_tvcolumn2.pack_start(cell2, True)
		#set the cell attributes to the listmodel column
		self.win_OD_tvcolumn0.set_attributes(cell0, text=0)
		self.win_OD_tvcolumn1.set_attributes(cell1, text=1)
		self.win_OD_tvcolumn2.set_attributes(cell2, text=2)
		#set treeview options
		self.win_OD_treeview.set_search_column(0)
		self.win_OD_tvcolumn0.set_sort_column_id(0)
		self.win_OD_tvcolumn1.set_sort_column_id(1)
		self.win_OD_tvcolumn2.set_sort_column_id(2)
		#add treeview to scrolledwindow
		scrolledwindow = Gtk.ScrolledWindow()
		scrolledwindow.add(self.win_OD_treeview)
		scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)
		vbox=Gtk.VBox()
		vbox.pack_start(scrolledwindow, True, True, 0)
		hbox=Gtk.HBox()
		#buttons
		button = Gtk.Button(stock=Gtk.STOCK_CANCEL)
		button.connect("clicked", lambda w: self.openDatabaseSelectReject())
		hbox.pack_end(button,False, False, 0)
		button = Gtk.Button(selectstr)
		button.connect("clicked", lambda w: self.openDatabaseSelectReturn(type))
		hbox.pack_end(button,False, False, 0)
		#display window
		vbox.pack_start(hbox,False, False, 0)
		self.win_OD.add(vbox)
		self.win_OD_treeview.set_model(listmodel)
		self.win_OD.show_all()
		return

	def openDatabaseSelectReject(self):
		self.win_OD.destroy()
		return

	def openDatabaseSelectReturn(self, type):
		model = self.win_OD_selection.get_selected()[0]
		iter = self.win_OD_selection.get_selected()[1]
		for i in range(len(self.DB)):
			if self.DB[i]["id"] == model.get_value(iter,3):
				list = self.DB[i]

		#synastry
		if type == "Synastry":
			openAstro.type="Transit"
			openAstro.t_name=str(list["name"])
			openAstro.t_year=int(list["year"])
			openAstro.t_month=int(list["month"])
			openAstro.t_day=int(list["day"])
			openAstro.t_hour=float(list["hour"])
			openAstro.t_geolon=float(list["geolon"])
			openAstro.t_geolat=float(list["geolat"])
			openAstro.t_altitude=int(list["altitude"])
			openAstro.t_location=str(list["location"])
			openAstro.t_timezone=float(list["timezone"])
			openAstro.charttype="%s (%s)" % (openAstro.label["synastry"],openAstro.t_name)
			openAstro.transit=True
			openAstro.makeSVG()

		elif type == "Composite":
			openAstro.type="Composite"
			openAstro.t_name=str(list["name"])
			openAstro.t_year=int(list["year"])
			openAstro.t_month=int(list["month"])
			openAstro.t_day=int(list["day"])
			openAstro.t_hour=float(list["hour"])
			openAstro.t_geolon=float(list["geolon"])
			openAstro.t_geolat=float(list["geolat"])
			openAstro.t_altitude=int(list["altitude"])
			openAstro.t_location=str(list["location"])
			openAstro.t_timezone=float(list["timezone"])
			openAstro.charttype="%s (%s)" % (openAstro.label["composite"],openAstro.t_name)
			openAstro.transit=False
			openAstro.makeSVG()

		elif type == "Combine":
			openAstro.type="Combine"
			openAstro.t_name=str(list["name"])
			openAstro.t_year=int(list["year"])
			openAstro.t_month=int(list["month"])
			openAstro.t_day=int(list["day"])
			openAstro.t_hour=float(list["hour"])
			openAstro.t_geolon=float(list["geolon"])
			openAstro.t_geolat=float(list["geolat"])
			openAstro.t_altitude=int(list["altitude"])
			openAstro.t_location=str(list["location"])
			openAstro.t_timezone=float(list["timezone"])

			#calculate combine between both utc times
			h,m,s = openAstro.decHour(openAstro.hour)
			dt1 = datetime.datetime(openAstro.year,openAstro.month,openAstro.day,h,m,s)
			h,m,s = openAstro.decHour(openAstro.t_hour)
			dt2 = datetime.datetime(openAstro.t_year,openAstro.t_month,openAstro.t_day,h,m,s)

			if dt1 > dt2:
				delta = dt1 - dt2
				hdelta = delta // 2
				combine = dt2 + hdelta
			else:
				delta = dt2 - dt1
				hdelta = delta // 2
				combine = dt1 + hdelta

			#take lon,lat middle
			openAstro.c_geolon = (openAstro.geolon + openAstro.t_geolon)/2.0
			openAstro.c_geolat = (openAstro.geolat + openAstro.t_geolat)/2.0
			openAstro.c_altitude = (openAstro.t_altitude + openAstro.altitude)/2.0
			openAstro.c_year = combine.year
			openAstro.c_month = combine.month
			openAstro.c_day = combine.day
			openAstro.c_hour = openAstro.decHourJoin(combine.hour,combine.minute,combine.second)

			openAstro.charttype="%s (%s)" % (openAstro.label["combine"],openAstro.t_name)
			openAstro.transit=False

			#set new date for printing in svg
			openAstro.year = openAstro.c_year
			openAstro.month = openAstro.c_month
			openAstro.day = openAstro.c_day
			openAstro.hour = openAstro.c_hour
			openAstro.geolat = openAstro.c_geolat
			openAstro.geolon = openAstro.c_geolon
			openAstro.timezone_str = zonetab.nearest_tz(openAstro.geolat,openAstro.geolon,zonetab.timezones())[2]
			#aware datetime object
			dt_input = datetime.datetime(combine.year, combine.month, combine.day, combine.hour, combine.minute, combine.second)
			dt = pytz.timezone(openAstro.timezone_str).localize(dt_input)
			openAstro.timezone=openAstro.offsetToTz(dt.utcoffset())
			openAstro.utcToLocal()
			openAstro.makeSVG()

		self.draw.queue_draw()
		self.draw.setSVG(self.tempfilename)
		self.win_OD.destroy()

	def openDatabaseDel(self, widget):
		#get name from selection
		model = self.win_OD_selection.get_selected()[0]
		iter = self.win_OD_selection.get_selected()[1]
		for i in range(len(self.DB)):
			if self.DB[i]["id"] == model.get_value(iter,3):
				self.ODDlist = self.DB[i]
		name = self.ODDlist["name"]
		dialog=Gtk.Dialog(_('Question'),self.win_OD,0,(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT, Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
		dialog.set_destroy_with_parent(True)
		dialog.connect("close", lambda w,e: dialog.destroy())
		dialog.connect("response",self.openDatabaseDelDo)
		dialog.vbox.pack_start(Gtk.Label(_('Are you sure you want to delete')+' '+name+'?'),True,True,0)
		dialog.show_all()
		return

	def openDatabaseDelDo(self, widget, response_id):
		if response_id == Gtk.ResponseType.ACCEPT:
			#get id from selection
			del_id = self.ODDlist["id"]
			#delete database entry
			sql='DELETE FROM event_natal WHERE id='+str(del_id)
			db.pquery([sql])
			dprint('deleted database entry: '+self.ODDlist["name"])
			widget.destroy()
			self.win_OD.destroy()
			self.openDatabase(self.window)
			self.updateUI()
		else:
			widget.destroy()
			dprint('rejected database deletion')
		return

	def openDatabaseOpen(self, widget):
		model = self.win_OD_selection.get_selected()[0]
		iter = self.win_OD_selection.get_selected()[1]
		for i in range(len(self.DB)):
			if self.DB[i]["id"] == model.get_value(iter,3):
				list = self.DB[i]
		openAstro.type="Radix"
		openAstro.charttype=openAstro.label["radix"]
		openAstro.transit=False
		self.updateChartList(widget, list)
		self.win_OD.destroy()
		return

	def openDatabaseEdit(self, widget):
		model = self.win_OD_selection.get_selected()[0]
		iter = self.win_OD_selection.get_selected()[1]
		for i in range(len(self.DB)):
			if self.DB[i]["id"] == model.get_value(iter,3):
				self.oDE_list = self.DB[i]
		openAstro.type="Radix"
		openAstro.charttype=openAstro.label["radix"]
		openAstro.transit=False
		self.updateChartList(widget, self.oDE_list)
		self.eventData( widget , edit=True )
		return

	def openDatabaseEditAsk(self, widget):
		#check for duplicate name without duplicate id
		en = db.getDatabase()
		for i in range(len(en)):
			if en[i]["name"] == self.name.get_text() and self.oDE_list["id"] != en[i]["id"]:
				dialog=Gtk.Dialog(_('Duplicate'),self.window2,0,(Gtk.STOCK_OK, Gtk.ResponseType.DELETE_EVENT))
				dialog.set_icon_from_file(cfg.iconWindow)
				dialog.connect("response", lambda w,e: dialog.destroy())
				dialog.connect("close", lambda w,e: dialog.destroy())
				dialog.vbox.pack_start(Gtk.Label(_('There is allready an entry for this name, please choose another')),True,True,0)
				dialog.show_all()
				return
		#ask for confirmation
		dialog=Gtk.Dialog(_('Question'),self.window2,0,(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT, Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
		dialog.set_destroy_with_parent(True)
		dialog.set_icon_from_file(cfg.iconWindow)
		dialog.connect("close", lambda w,e: dialog.destroy())
		dialog.connect("response",self.openDatabaseEditSave)
		dialog.vbox.pack_start(Gtk.Label(_('Are you sure you want to Save?')),True,True,0)
		dialog.show_all()
		return

	def openDatabaseEditSave(self, widget, response_id):
		if response_id == Gtk.ResponseType.ACCEPT:
			#update chart data
			self.updateChartData()
			#set query to save
			sql = 'UPDATE event_natal SET name=?,year=?,month=?,day=?,hour=?,\
				geolon=?,geolat=?,altitude=?,location=?,timezone=?,notes=?,\
				image=?,countrycode=?,timezonestr=?,geonameid=? WHERE id=?'
			values = (openAstro.name,openAstro.year,openAstro.month,
				openAstro.day,openAstro.hour,openAstro.geolon,openAstro.geolat,openAstro.altitude,
				openAstro.location,openAstro.timezone,'','',openAstro.countrycode,
				openAstro.timezonestr,openAstro.geonameid,self.oDE_list["id"])
			db.pquery([sql],[values])
			dprint('saved edit to database: '+openAstro.name)
			widget.destroy()
			self.window2.destroy()
			self.win_OD.destroy()
			self.openDatabase( self.window )
			self.updateUI()
		else:
			widget.destroy()
			dprint('rejected save to database')
		return

	def doPrint(self, widget):
		settings = Gtk.PrintSettings()
		settings.set_resolution(300)
		print_op = Gtk.PrintOperation()
		print_op.set_unit(Gtk.Unit.MM)
		print_op.set_print_settings(settings)
		print_op.connect("begin_print", self.doPrintBegin)
		print_op.connect("draw_page", self.doPrintDraw)

		chooser = Gtk.FileChooserDialog(parent=self.window, title=_("Select Export Filename"),action=Gtk.FileChooserAction.SAVE,
                                  buttons=(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,Gtk.STOCK_SAVE,Gtk.ResponseType.OK))
		chooser.set_current_folder(cfg.homedir)
		chooser.set_current_name(openAstro.name+'.pdf')
		filter = Gtk.FileFilter()
		filter.set_name(_("PDF Files (*.pdf)"))
		filter.add_pattern("*.pdf")
		chooser.add_filter(filter)
		response = chooser.run()
		if response == Gtk.ResponseType.OK:
			print_op.set_export_filename(chooser.get_filename())
			chooser.destroy()
			res = print_op.run(Gtk.PrintOperationAction.EXPORT, self.window)
		else:
			chooser.destroy()
			print_op.cancel()
			res = None


	def doPrintBegin(self, operation, context):
		operation.set_n_pages(1)
		operation.set_use_full_page(False)
		ps = Gtk.PageSetup()
		ps.set_orientation(Gtk.PageOrientation.LANDSCAPE)
		ps.set_paper_size(Gtk.PaperSize(Gtk.PAPER_NAME_A4))
		operation.set_default_page_setup(ps)

	def doPrintDraw(self, operation, context, page_nr):
		cr = context.get_cairo_context()
		#draw svg
		printing={}
		printing['pagenum']=page_nr
		printing['width']=context.get_width()
		printing['height']=context.get_height()
		printing['dpi_x']=context.get_dpi_x()
		printing['dpi_y']=context.get_dpi_y()

		#make printing svg
		openAstro.makeSVG(printing=printing)

		#draw svg for printing
		svg = Rsvg.Handle.new_from_file(cfg.tempfilenameprint)
		svg.set_dpi(300)
		svg.render_cairo(cr)

		#cr.scale(1.5,1.5)


	"""

	Menu item for general configuration

	settingsConfiguration
	settingsConfigurationSubmit

	"""

	def settingsConfiguration(self, widget):
		# create a new window
		self.win_SC = Gtk.Dialog(parent=self.window)
		self.win_SC.set_icon_from_file(cfg.iconWindow)
		self.win_SC.set_title(_("General Configuration"))
		self.win_SC.connect("delete_event", lambda w,e: self.win_SC.destroy())
		self.win_SC.move(200,150)
		self.win_SC.set_border_width(5)
		self.win_SC.set_size_request(450,450)

		#data dictionary
		data = {}

		#create a table
		table = Gtk.Table(8, 1, False)
		table.set_col_spacings(0)
		table.set_row_spacings(0)
		table.set_border_width(10)

		#description

		#options
		table.attach(Gtk.Label(_("Use Online Geocoding (ws.geonames.org)")), 0, 1, 0, 1, xoptions=Gtk.AttachOptions.SHRINK, yoptions=Gtk.AttachOptions.SHRINK, xpadding=10)
		data['use_geonames.org'] = Gtk.CheckButton()
		table.attach(data['use_geonames.org'], 0, 1, 1, 2, xoptions=Gtk.AttachOptions.SHRINK, yoptions=Gtk.AttachOptions.SHRINK, xpadding=10)
		if db.getAstrocfg('use_geonames.org') == "1":
			data['use_geonames.org'].set_active(True)

		#house system
		data['houses_system'] = Gtk.ComboBoxText.new()
		table.attach(Gtk.Label(_('Houses System')), 0, 1, 2, 3, xoptions=Gtk.AttachOptions.SHRINK, yoptions=Gtk.AttachOptions.SHRINK, xpadding=10)
		table.attach(data['houses_system'], 0, 1, 3, 4, xoptions=Gtk.AttachOptions.SHRINK, yoptions=Gtk.AttachOptions.SHRINK, xpadding=10)
		hsys={
				"P":"Placidus",
				"K":"Koch",
				"O":"Porphyrius",
				"R":"Regiomontanus",
				"C":"Campanus",
				"A":"Equal (Cusp 1 = Asc)",
				"V":"Vehlow Equal (Asc = 1/2 House 1)",
				"W":"Whole",
				"X":"Axial Rotation",
				"H":"Azimuthal or Horizontal System",
				"T":"Polich/Page ('topocentric system')",
				"B":"Alcabitus",
				"G":"Gauquelin sectors",
				"M":"Morinus"
				}
		self.houses_list=["P","K","O","R","C","A","V","W","X","H","T","B","G","M"]
		active=0
		for n in range(len(self.houses_list)):
			data['houses_system'].append_text(hsys[self.houses_list[n]])
			if db.astrocfg['houses_system'] == self.houses_list[n]:
				active = n
		data['houses_system'].set_active(active)

		#position calculation (geo,truegeo,topo,helio)
		data['postype'] = Gtk.ComboBoxText.new()
		table.attach(Gtk.Label(_('Position Calculation')), 0, 1, 4, 5, xoptions=Gtk.AttachOptions.SHRINK, yoptions=Gtk.AttachOptions.SHRINK, xpadding=10)
		table.attach(data['postype'], 0, 1, 5, 6, xoptions=Gtk.AttachOptions.SHRINK, yoptions=Gtk.AttachOptions.SHRINK, xpadding=10)
		postype={

				"geo":openAstro.label["apparent_geocentric"]+" "+_("(default)"),
				"truegeo":openAstro.label["true_geocentric"],
				"topo":openAstro.label["topocentric"],
				"helio":openAstro.label["heliocentric"]
				}
		self.postype_list=["geo","truegeo","topo","helio"]
		active=0
		for n in range(len(self.postype_list)):
			data['postype'].append_text(postype[self.postype_list[n]])
			if db.astrocfg['postype'] == self.postype_list[n]:
				active = n
		data['postype'].set_active(active)

		#chart view (traditional,european)
		data['chartview'] = Gtk.ComboBoxText.new()
		table.attach(Gtk.Label(_('Chart View')), 0, 1, 6, 7, xoptions=Gtk.AttachOptions.SHRINK, yoptions=Gtk.AttachOptions.SHRINK, xpadding=10)
		table.attach(data['chartview'], 0, 1, 7, 8, xoptions=Gtk.AttachOptions.SHRINK, yoptions=Gtk.AttachOptions.SHRINK, xpadding=10)
		chartview={
				"traditional":_("Planets in Zodiac"),
				"european":_("Planets around Zodiac")
				}
		self.chartview_list=["traditional","european"]
		active=0
		for n in range(len(self.chartview_list)):
			data['chartview'].append_text(chartview[self.chartview_list[n]])
			if db.astrocfg['chartview'] == self.chartview_list[n]:
				active = n
		data['chartview'].set_active(active)


		#zodiac type (tropical, sidereal)
		data['zodiactype'] = Gtk.ComboBoxText.new()
		table.attach(Gtk.Label(_('Zodiac Type')), 0, 1, 8, 9, xoptions=Gtk.AttachOptions.SHRINK, yoptions=Gtk.AttachOptions.SHRINK, xpadding=10)
		table.attach(data['zodiactype'], 0, 1, 10, 11, xoptions=Gtk.AttachOptions.SHRINK, yoptions=Gtk.AttachOptions.SHRINK, xpadding=10)
		chartview={
				"tropical":_("Tropical"),
				"sidereal":_("Sidereal")
				}
		self.zodiactype_list=["tropical","sidereal"]
		active=0
		for n in range(len(self.zodiactype_list)):
			data['zodiactype'].append_text(chartview[self.zodiactype_list[n]])
			if db.astrocfg['zodiactype'] == self.zodiactype_list[n]:
				active = n
		data['zodiactype'].set_active(active)


		#sidereal mode
		data['siderealmode'] = Gtk.ComboBoxText.new()
		if db.astrocfg['zodiactype'] != 'sidereal':
			data['siderealmode'].set_sensitive(False)
		def zodiactype_changed(button):
			if self.zodiactype_list[data['zodiactype'].get_active()] != 'sidereal':
				data['siderealmode'].set_sensitive(False)
			else:
				data['siderealmode'].set_sensitive(True)
		data['zodiactype'].connect("changed",zodiactype_changed)
		table.attach(Gtk.Label(_('Sidereal Mode')), 0, 1, 12, 13, xoptions=Gtk.AttachOptions.SHRINK, yoptions=Gtk.AttachOptions.SHRINK, xpadding=10)
		table.attach(data['siderealmode'], 0, 1, 14, 15, xoptions=Gtk.AttachOptions.SHRINK, yoptions=Gtk.AttachOptions.SHRINK, xpadding=10)
		self.siderealmode_chartview={
				"FAGAN_BRADLEY":_("Fagan Bradley"),
				"LAHIRI":_("Lahiri"),
				"DELUCE":_("Deluce"),
				"RAMAN":_("Ramanb"),
				"USHASHASHI":_("Ushashashi"),
				"KRISHNAMURTI":_("Krishnamurti"),
				"DJWHAL_KHUL":_("Djwhal Khul"),
				"YUKTESHWAR":_("Yukteshwar"),
				"JN_BHASIN":_("Jn Bhasin"),
				"BABYL_KUGLER1":_("Babyl Kugler 1"),
				"BABYL_KUGLER2":_("Babyl Kugler 2"),
				"BABYL_KUGLER3":_("Babyl Kugler 3"),
				"BABYL_HUBER":_("Babyl Huber"),
				"BABYL_ETPSC":_("Babyl Etpsc"),
				"ALDEBARAN_15TAU":_("Aldebaran 15Tau"),
				"HIPPARCHOS":_("Hipparchos"),
				"SASSANIAN":_("Sassanian"),
				"J2000":_("J2000"),
				"J1900":_("J1900"),
				"B1950":_("B1950")
				}
		self.siderealmode_list=["FAGAN_BRADLEY",
				"LAHIRI",
				"DELUCE",
				"RAMAN",
				"USHASHASHI",
				"KRISHNAMURTI",
				"DJWHAL_KHUL",
				"YUKTESHWAR",
				"JN_BHASIN",
				"BABYL_KUGLER1",
				"BABYL_KUGLER2",
				"BABYL_KUGLER3",
				"BABYL_HUBER",
				"BABYL_ETPSC",
				"ALDEBARAN_15TAU",
				"HIPPARCHOS",
				"SASSANIAN",
				"J2000",
				"J1900",
				"B1950"]
		active=0
		for n in range(len(self.siderealmode_list)):
			data['siderealmode'].append_text(self.siderealmode_chartview[self.siderealmode_list[n]])
			if db.astrocfg['siderealmode'] == self.siderealmode_list[n]:
				active = n
		data['siderealmode'].set_active(active)

		#language
		data['language'] = Gtk.ComboBoxText.new()
		table.attach(Gtk.Label(_('Language')), 0, 1, 16, 17, xoptions=Gtk.AttachOptions.SHRINK, yoptions=Gtk.AttachOptions.SHRINK, xpadding=10)
		table.attach(data['language'], 0, 1, 18, 19, xoptions=Gtk.AttachOptions.SHRINK, yoptions=Gtk.AttachOptions.SHRINK, xpadding=10)

		data['language'].append_text(_("Default"))
		active=0
		for i in range(len(LANGUAGES)):
			data['language'].append_text(db.lang_label[LANGUAGES[i]])
			if db.astrocfg['language'] == LANGUAGES[i]:
				active = i+1
		data['language'].set_active(active)

		#make the ui layout with ok button
		scrolledwindow = Gtk.ScrolledWindow()
		scrolledwindow.set_border_width(5)
		scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)
		self.win_SC.vbox.pack_start(scrolledwindow, True, True, 0)
		scrolledwindow.add_with_viewport(table)

		#ok button
		button = Gtk.Button(stock=Gtk.STOCK_OK)
		button.connect("clicked", self.settingsConfigurationSubmit, data)
		button.set_can_default(True)
		self.win_SC.action_area.pack_start(button, True, True, 0)
		button.grab_default()

		#cancel button
		button = Gtk.Button(stock=Gtk.STOCK_CANCEL)
		button.connect("clicked", lambda w: self.win_SC.destroy())
		self.win_SC.action_area.pack_start(button, True, True, 0)

		self.win_SC.show_all()
		return

	"""
    Configuration Function
	"""

	def settingsConfigurationSubmit(self, widget, data):
		update=False
		if data['use_geonames.org'].get_active():
			db.setAstrocfg("use_geonames.org","1")
		else:
			db.setAstrocfg("use_geonames.org","0")
		#houses system
		if self.houses_list[data['houses_system'].get_active()] != db.astrocfg['houses_system']:
			update=True
		db.setAstrocfg("houses_system",self.houses_list[data['houses_system'].get_active()])
		#position calculation
		if self.postype_list[data['postype'].get_active()] != db.astrocfg['postype']:
			update=True
		db.setAstrocfg("postype",self.postype_list[data['postype'].get_active()])
		#chart view
		if self.chartview_list[data['chartview'].get_active()] != db.astrocfg['chartview']:
			update=True
		db.setAstrocfg("chartview",self.chartview_list[data['chartview'].get_active()])
		#zodiac type
		if self.zodiactype_list[data['zodiactype'].get_active()] != db.astrocfg['zodiactype']:
			update=True
		db.setAstrocfg("zodiactype",self.zodiactype_list[data['zodiactype'].get_active()])
		#sidereal mode
		if self.siderealmode_list[data['siderealmode'].get_active()] != db.astrocfg['siderealmode']:
			update=True
		db.setAstrocfg("siderealmode",self.siderealmode_list[data['siderealmode'].get_active()])
		#language
		model = data['language'].get_model()
		active = data['language'].get_active()
		if active == 0:
			active_lang = "default"
		else:
			active_lang = LANGUAGES[active-1]
		if active_lang != db.astrocfg['language']:
			update=True
		db.setAstrocfg("language",active_lang)

		#set language to be used
		db.setLanguage(active_lang)
		self.updateUI()

		#updatechart
		if update:
			self.updateChart()
		self.win_SC.destroy()
		return


	"""

	Menu item to set home location:

	settingsLocation
	settingsLocationSubmit
	settingsLocationApply
	settingsLocationDestroy

	"""

	def settingsLocation(self, widget):
		self.settingsLocationMode = True
		# check connection to the internet
		self.checkInternetConnection()
		# create a new window
		self.win_SL = Gtk.Window(Gtk.WindowType.TOPLEVEL)
		self.win_SL.set_icon_from_file(cfg.iconWindow)
		self.win_SL.set_title(_("Please Set Your Home Location"))
		self.win_SL.connect("delete_event", lambda w,e: self.settingsLocationDestroy())
		self.win_SL.move(150,150)
		self.win_SL.set_border_width(10)

		#create a table
		table = Gtk.Table(5, 2, False)
		table.set_col_spacings(15)
		table.set_row_spacings(15)
		self.win_SL.add(table)

		#display of location (non editable)
		table.attach(Gtk.Label(_('Location')+':'), 0, 1, 1, 2)
		self.LLoc=Gtk.Label(openAstro.home_location)
		table.attach(self.LLoc, 1, 2, 1, 2)

		table.attach(Gtk.Label(_('Latitude')+':'), 0, 1, 2, 3)
		self.LLat=Gtk.Label(openAstro.home_geolat)
		table.attach(self.LLat, 1, 2, 2, 3)

		table.attach(Gtk.Label(_('Longitude')+':'), 0, 1, 3, 4)
		self.LLon=Gtk.Label(openAstro.home_geolon)
		table.attach(self.LLon, 1, 2, 3, 4)

		#use geocoders if we have an internet connection else geonames database
		if self.iconn:
			#entry for location (editable)
			hbox=Gtk.HBox()
			label=Gtk.Label(_("City")+": ")
			hbox.pack_start(label, False, False, 0)
			self.geoLoc = Gtk.Entry()
			self.geoLoc.set_max_length(100)
			self.geoLoc.set_width_chars(30)
			self.geoLoc.set_text(openAstro.home_location.partition(',')[0])
			hbox.pack_start(self.geoLoc, False, False, 0)
			label=Gtk.Label(" "+_("Country-code")+": ")
			hbox.pack_start(label, False, False, 0)
			self.geoCC = Gtk.Entry()
			self.geoCC.set_max_length(2)
			self.geoCC.set_width_chars(2)
			self.geoCC.set_text(openAstro.home_countrycode)
			hbox.pack_start(self.geoCC, False, False, 0)
			table.attach(hbox, 0, 2, 0, 1)
		else:
			hbox=Gtk.HBox()
			table.attach(hbox, 0, 2, 0, 1)
			#get nearest home
			self.GEON_nearest = db.gnearest(openAstro.geolat,openAstro.geolon)
			#continents
			self.contbox = Gtk.ComboBox()
			self.contstore = Gtk.ListStore(str,str)
			cell = Gtk.CellRendererText()
			self.contbox.pack_start(cell, False)
			self.contbox.add_attribute(cell, 'text', 0)
			hbox.pack_start(self.contbox, False, False, 0)
			self.contbox.set_wrap_width(1)

			sql = 'SELECT * FROM continent ORDER BY name ASC'
			db.gquery(sql)
			continentinfo=[]
			i = 0
			activecont = 3
			for row in db.gcursor:
				if row['code'] == self.GEON_nearest['continent']:
					activecont=i
					self.GEON_nearest['continent']=None
				self.contstore.append([row['name'],row['code']])
				i += 1
			db.gclose()
			self.contbox.set_model(self.contstore)

			#countries
			self.countrybox = Gtk.ComboBox()
			cell = Gtk.CellRendererText()
			self.countrybox.pack_start(cell, False)
			self.countrybox.add_attribute(cell, 'text', 0)
			hbox.pack_start(self.countrybox, False, False, 0 )
			self.countrybox.set_wrap_width(1)
			self.countrybox.connect('changed', self.eventDataChangedCountrybox)

			#provinces
			self.provbox = Gtk.ComboBox()
			cell = Gtk.CellRendererText()
			self.provbox.pack_start(cell, False)
			self.provbox.add_attribute(cell, 'text', 0)
			hbox.pack_start(self.provbox, False, False, 0 )
			self.provbox.set_wrap_width(1)
			self.provbox.connect('changed', self.eventDataChangedProvbox)

			#cities
			self.citybox = Gtk.ComboBox()
			cell = Gtk.CellRendererText()
			self.citybox.pack_start(cell, False)
			self.citybox.add_attribute(cell, 'text', 0)
			hbox.pack_start(self.citybox, False, False, 0 )
			self.citybox.set_wrap_width(2)
			self.citybox.connect('changed', self.eventDataChangedCitybox)

			self.contbox.connect('changed', self.eventDataChangedContbox)
			self.contbox.set_active(activecont)

		#buttonbox
		buttonbox = Gtk.HBox(False, 5)
		table.attach(buttonbox, 1, 2, 4, 5)

  		#ok button
		button = Gtk.Button(stock=Gtk.STOCK_OK)
		button.connect("clicked", self.settingsLocationSubmit)
		button.set_can_default(True)
		buttonbox.pack_start(button,False,False,0)
		button.grab_default()

		#Test button
		button = Gtk.Button(_('Test'),Gtk.STOCK_APPLY)
		button.connect("clicked", self.settingsLocationApply)
		buttonbox.pack_start(button,False,False,0)

		#Cancel button
		button = Gtk.Button(stock=Gtk.STOCK_CANCEL)
		button.connect("clicked", lambda w: self.settingsLocationDestroy())
		buttonbox.pack_start(button,False,False,0)

		#show all
		self.win_SL.show_all()

	def settingsLocationSubmit(self, widget):
		self.settingsLocationApply(widget)
		if self.geoLocFound:
			self.settingsLocationDestroy()
			return
		else:
			return

	def settingsLocationApply(self, widget):
		#check for internet connection to decide geocode/database
		self.geoLocFound = True
		if self.iconn:
			result = geoname.search(self.geoLoc.get_text(),self.geoCC.get_text())
			if result:
				self.geoLocFound = True
				lat=float(result[0]['lat'])
				lon=float(result[0]['lng'])
				tzstr=result[0]['timezonestr']
				cc=result[0]['countryCode']
				loc='%s, %s' % (result[0]['name'],result[0]['countryName'])
				dprint('settingsLocationApply: %s found; %s %s %s' % (self.geoLoc.get_text(), lat,lon,loc))
			else:
				self.geoLocFound = False
				#revert to defaults
				lat=openAstro.geolat
				lon=openAstro.geolon
				loc=openAstro.location
				cc=openAstro.countrycode
				tzstr=openAstro.timezonestr
				dprint('settingsLocationApply: %s not found, reverting to defaults' % self.geoLoc.get_text() )
				self.geoLoc.set_text('City Not Found, Try Again!')
				return
		else:
			lat = float(self.GEON_lat)
			lon = float(self.GEON_lon)
			loc = self.GEON_loc
			cc = self.GEON_cc
			tzstr = self.GEON_tzstr

		#apply settings to database
		db.setSettingsLocation(lat,lon,loc,cc,tzstr)
		openAstro.home_location=loc
		openAstro.home_geolat=lat
		openAstro.home_geolon=lon
		openAstro.home_countrycode=cc
		openAstro.home_timezonestr=tzstr
		openAstro.location=loc
		openAstro.timezonestr=tzstr
		openAstro.geolat=lat
		openAstro.geolon=lon
		openAstro.countrycode=cc
		openAstro.transit=False
		openAstro.name=_("Here and Now")
		openAstro.type="Radix"
		self.LLat.set_text(str(lat))
		self.LLon.set_text(str(lon))
		self.LLoc.set_text(str(loc))

		#set defaults for chart creation
		now = datetime.datetime.now()
		dt_input = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)
		dt = pytz.timezone(openAstro.timezonestr).localize(dt_input)
		dt_utc = dt.replace(tzinfo=None) - dt.utcoffset()
		openAstro.name=_("Here and Now")
		openAstro.charttype=openAstro.label["radix"]
		openAstro.year=dt_utc.year
		openAstro.month=dt_utc.month
		openAstro.day=dt_utc.day
		openAstro.hour=openAstro.decHourJoin(dt_utc.hour,dt_utc.minute,dt_utc.second)
		openAstro.timezone=openAstro.offsetToTz(dt.utcoffset())
		openAstro.altitude=25
		openAstro.utcToLocal()

		self.updateChart()
		dprint('Setting New Home Location: %s %s %s' % (lat,lon,loc) )
		return

	def settingsLocationDestroy(self):
		self.settingsLocationMode = False
		self.win_SL.destroy()
		return

	"""

	Menu item to set aspect options

	settingsAspects
	settingsAspectsSubmit

	"""

	def settingsAspects(self, widget):
		# create a new window
		self.win_SA = Gtk.Dialog()
		self.win_SA.set_icon_from_file(cfg.iconWindow)
		self.win_SA.set_title(_("Aspect Settings"))
		self.win_SA.connect("delete_event", lambda w,e: self.win_SA.destroy())
		self.win_SA.move(150,150)
		self.win_SA.set_border_width(5)
		self.win_SA.set_size_request(550,450)

		#create a table
		table = Gtk.Table(len(openAstro.aspects)-3, 6, False)
		table.set_col_spacings(0)
		table.set_row_spacings(0)
		table.set_border_width(10)

		#description
		label = Gtk.Label(_("Deg"))
		table.attach(label, 1, 2, 0, 1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
		label = Gtk.Label(_("Aspect Name"))
		table.attach(label, 2, 3, 0, 1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
		label = Gtk.Label(_("Visible\nin Circle"))
		table.attach(label, 3, 4, 0, 1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
		label = Gtk.Label(_("Visible\nin Grid"))
		table.attach(label, 4, 5, 0, 1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
		label = Gtk.Label(_("Orb"))
		table.attach(label, 5, 6, 0, 1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)

		data = []
		x=1
		for i in range(len(openAstro.aspects)):
			#0=degree, 1=name, 2=color, 3=is_major, 4=orb
			data.append({})
			data[-1]['icon'] = Gtk.Image()
			filename=.join(cfg.iconAspects,str(openAstro.aspects[i]['degree'])+'.svg')
			data[-1]['icon'].set_from_file(filename)
			data[-1]['degree'] = openAstro.aspects[i]['degree']
			data[-1]['degree_str'] = Gtk.Label(str(openAstro.aspects[i]['degree']))
			data[-1]['name'] = Gtk.Entry()
			data[-1]['name'].set_max_length(25)
			data[-1]['name'].set_width_chars(15)
			data[-1]['name'].set_text(openAstro.aspects[i]['name'])
			table.attach(data[-1]['icon'], 0, 1, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
			table.attach(data[-1]['degree_str'], 1, 2, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
			table.attach(data[-1]['name'], 2, 3, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
			data[-1]['visible'] = Gtk.CheckButton()
			if openAstro.aspects[i]['visible'] is 1:
				data[-1]['visible'].set_active(True)
			table.attach(data[-1]['visible'], 3, 4, x, x+1, xoptions=Gtk.AttachOptions.EXPAND, xpadding=2, ypadding=2)
			data[-1]['visible_grid'] = Gtk.CheckButton()
			if openAstro.aspects[i]['visible_grid'] is 1:
				data[-1]['visible_grid'].set_active(True)
			table.attach(data[-1]['visible_grid'], 4, 5, x, x+1, xoptions=Gtk.AttachOptions.EXPAND, xpadding=2, ypadding=2)
			data[-1]['orb'] = Gtk.Entry()
			data[-1]['orb'].set_max_length(4)
			data[-1]['orb'].set_width_chars(4)
			data[-1]['orb'].set_text(str(openAstro.aspects[i]['orb']))
			table.attach(data[-1]['orb'], 5, 6, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
			x=x+1

		#make the ui layout with ok button
		scrolledwindow = Gtk.ScrolledWindow()
		scrolledwindow.set_border_width(5)
		scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)
		self.win_SA.vbox.pack_start(scrolledwindow, True, True, 0)
		scrolledwindow.add_with_viewport(table)

		#ok button
		button = Gtk.Button(stock=Gtk.STOCK_OK)
		button.connect("clicked", self.settingsAspectsSubmit, data)
		button.set_can_default(True)
		self.win_SA.action_area.pack_start(button, True, True, 0)
		button.grab_default()

		#cancel button
		button = Gtk.Button(stock=Gtk.STOCK_CANCEL)
		button.connect("clicked", lambda w: self.win_SA.destroy())
		self.win_SA.action_area.pack_start(button, True, True, 0)

		self.win_SA.show_all()
		return

	def settingsAspectsSubmit(self, widget, data):
		query=[]
		for i in range(len(data)):

			if data[i]['visible'].get_active():
				active = 1
			else:
				active = 0

			if data[i]['visible_grid'].get_active():
				active_grid = 1
			else:
				active_grid = 0

			orb = float(data[i]['orb'].get_text().replace(',','.'))
			if orb == int(orb):
				orb = int(orb)

			sql = 'UPDATE settings_aspect SET '
			sql += 'name = "%s", visible = %s' % (data[i]['name'].get_text(),active)
			sql += ', visible_grid = %s, orb = "%s"' % (active_grid,orb)
			sql += ' WHERE degree = '+str(data[i]['degree'])
			query.append(sql)

		#query
		db.query(query)
		#update chart
		self.updateChart()
		#destroy window
		self.win_SA.destroy()

	"""

	Menu item to edit options for planets

	settingsPlanets
	settingsPlanetsSubmit

	"""

	def settingsPlanets(self, obj):
		# create a new window
		self.win_SP = Gtk.Dialog(parent=self.window)
		self.win_SP.set_icon_from_file(cfg.iconWindow)
		self.win_SP.set_title(_("Planets & Angles Settings"))
		self.win_SP.connect("delete_event", lambda w,e: self.win_SP.destroy())
		self.win_SP.move(150,150)
		self.win_SP.set_border_width(5)
		self.win_SP.set_size_request(470,450)

		#create a table
		table = Gtk.Table(len(openAstro.planets)-3, 4, False)
		table.set_border_width(10)
		table.set_col_spacings(0)
		table.set_row_spacings(0)

		#description
		table.set_row_spacing(0,8)
		label = Gtk.Label(_("Planet Label"))
		table.attach(label, 0, 1, 0, 1)
		label = Gtk.Label(_("Symbol"))
		table.attach(label, 1, 2, 0, 1, xoptions=Gtk.AttachOptions.SHRINK, xpadding=10)
		label = Gtk.Label(_("Aspect Line"))
		table.attach(label, 2, 3, 0, 1, xoptions=Gtk.AttachOptions.SHRINK, xpadding=10)
		label = Gtk.Label(_("Aspect Grid"))
		table.attach(label, 3, 4, 0, 1, xoptions=Gtk.AttachOptions.SHRINK, xpadding=10)

		data = []
		x=1
		for i in range(len(openAstro.planets)):
			#planets to skip: 11=true node, 13=osc. apogee, 14=earth, 21=intp. apogee, 22=intp. perigee
			#angles: 23=Asc, 24=Mc, 25=Ds, 26=Ic
			#points: 27=pars fortuna
			if i is 11 or i is 13 or i is 14 or i is 21 or i is 22:
				continue
			#start of the angles
			if i is 23 or i is 27:
				table.set_row_spacing(x-1,20)
				table.set_row_spacing(x,8)
				if i is 27:
					label = Gtk.Label(_("Point Label"))
				else:
					label = Gtk.Label(_("Angle Label"))
				table.attach(label, 0, 1, x, x+1, xoptions=Gtk.AttachOptions.SHRINK, xpadding=10)
				label = Gtk.Label(_("Symbol"))
				table.attach(label, 1, 2, x, x+1, xoptions=Gtk.AttachOptions.SHRINK, xpadding=10)
				label = Gtk.Label(_("Aspect Line"))
				table.attach(label, 2, 3, x, x+1, xoptions=Gtk.AttachOptions.SHRINK, xpadding=10)
				label = Gtk.Label(_("Aspect Grid"))
				table.attach(label, 3, 4, x, x+1, xoptions=Gtk.AttachOptions.SHRINK, xpadding=10)
				x=x+1
			data.append({})
			data[-1]['id'] = openAstro.planets[i]['id']
			data[-1]['label'] = Gtk.Entry()
			data[-1]['label'].set_max_length(25)
			data[-1]['label'].set_width_chars(15)
			data[-1]['label'].set_text(openAstro.planets[i]['label'])
			#data[-1]['label'].set_alignment(xalign=0.0, yalign=0.5)
			table.attach(data[-1]['label'], 0, 1, x, x+1, xoptions=Gtk.AttachOptions.SHRINK, xpadding=10)
			data[-1]['visible'] = Gtk.CheckButton()
			if openAstro.planets[i]['visible'] is 1:
				data[-1]['visible'].set_active(True)
			table.attach(data[-1]['visible'], 1, 2, x, x+1, xoptions=Gtk.AttachOptions.SHRINK, xpadding=2, ypadding=2)

			data[-1]['visible_aspect_line'] = Gtk.CheckButton()
			if openAstro.planets[i]['visible_aspect_line'] is 1:
				data[-1]['visible_aspect_line'].set_active(True)
			table.attach(data[-1]['visible_aspect_line'], 2, 3, x, x+1, xoptions=Gtk.AttachOptions.SHRINK, xpadding=2, ypadding=2)

			data[-1]['visible_aspect_grid'] = Gtk.CheckButton()
			if openAstro.planets[i]['visible_aspect_grid'] is 1:
				data[-1]['visible_aspect_grid'].set_active(True)
			table.attach(data[-1]['visible_aspect_grid'], 3, 4, x, x+1, xoptions=Gtk.AttachOptions.SHRINK, xpadding=2, ypadding=2)
			x=x+1

		#make the ui layout with ok button
		scrolledwindow = Gtk.ScrolledWindow()
		scrolledwindow.set_border_width(5)
		scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)
		self.win_SP.vbox.pack_start(scrolledwindow, True, True, 0)
		scrolledwindow.add_with_viewport(table)

		#ok button
		button = Gtk.Button(stock=Gtk.STOCK_OK)
		button.connect("clicked", self.settingsPlanetsSubmit, data)
		button.set_can_default(True)
		#button.set_property('can_default',True)
		self.win_SP.action_area.pack_start(button, True, True, 0)
		button.grab_default()

		#cancel button
		button = Gtk.Button(stock=Gtk.STOCK_CANCEL)
		button.connect("clicked", lambda w: self.win_SP.destroy())
		self.win_SP.action_area.pack_start(button, True, True, 0)

		self.win_SP.show_all()
		return

	def settingsPlanetsSubmit(self, widget, data):
		query=[]
		for i in range(len(data)):
			sql = 'UPDATE settings_planet SET label = "%s"'%(data[i]['label'].get_text())
			radio={"visible":0,"visible_aspect_line":0,"visible_aspect_grid":0}
			for key,val in radio.items():
				if data[i][key].get_active():
					radio[key]=1
				sql += ', %s = %s' % (key,radio[key])
			sql += ' WHERE id = '+str(data[i]['id'])
			query.append(sql)

		#query
		db.query(query)
		#update chart
		self.updateChart()
		#destroy window
		self.win_SP.destroy()


	"""

	Menu item to set color options

	settingsColors
	settingsColorsSubmit

	"""

	def settingsColorsReset(self, widget, id):
		self.SCdata[id]['code'].set_text(db.defaultColors[self.SCdata[id]['key']])
		self.SCdata[id]['code'].modify_base(Gtk.StateFlags.NORMAL, Gdk.color_parse(db.defaultColors[self.SCdata[id]['key']]))
		return

	def settingsColors(self, widget):
		# initialize settings colors selector
		self.colorseldlg = None

		# create a new window
		self.win_SC = Gtk.Dialog(parent=self.window)
		self.win_SC.set_icon_from_file(cfg.iconWindow)
		self.win_SC.set_title(_("Color Settings"))
		self.win_SC.connect("delete_event", lambda w,e: self.win_SC.destroy())
		self.win_SC.move(150,150)
		self.win_SC.set_border_width(5)
		self.win_SC.set_size_request(470,450)

		#create a table
		table = Gtk.Table(24, 4, False)
		table.set_col_spacings(0)
		table.set_row_spacings(0)
		table.set_border_width(10)

		#data to be processed
		self.SCdata = []
		delimiter="--------------------------------------------"

		#Basic color scheme stuff
		table.attach(Gtk.Label(delimiter),0,4,0,1,xoptions=Gtk.AttachOptions.FILL,xpadding=10)
		table.attach(Gtk.Label(_("Basic Chart Colors")),0,4,1,2,xoptions=Gtk.AttachOptions.FILL,xpadding=10)
		table.attach(Gtk.Label(delimiter),0,4,2,3,xoptions=Gtk.AttachOptions.FILL,xpadding=10)
		x=3
		for i in range(2):
			self.SCdata.append({})
			self.SCdata[-1]['key']="paper_%s"%(i)
			self.SCdata[-1]['name']=Gtk.Label("Paper Color %s"%(i))
			self.SCdata[-1]['code'] = Gtk.Entry()
			self.SCdata[-1]['code'].set_max_length(25)
			self.SCdata[-1]['code'].set_width_chars(10)
			self.SCdata[-1]['code'].set_text(openAstro.colors["paper_%s"%(i)])
			self.SCdata[-1]['code'].modify_base(Gtk.StateFlags.NORMAL, Gdk.color_parse(openAstro.colors["paper_%s"%(i)]))
			self.SCdata[-1]['button'] = Gtk.Button(stock=Gtk.STOCK_SELECT_COLOR)
			self.SCdata[-1]['button'].connect("clicked", self.settingsColorsChanger, len(self.SCdata)-1)
			self.SCdata[-1]['reset'] = Gtk.Button(_("Default"))
			self.SCdata[-1]['reset'].connect("clicked", self.settingsColorsReset, len(self.SCdata)-1)

			table.attach(self.SCdata[-1]['name'], 0, 1, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
			table.attach(self.SCdata[-1]['code'], 1, 2, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
			table.attach(self.SCdata[-1]['button'], 2, 3, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
			table.attach(self.SCdata[-1]['reset'], 3, 4, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
			x+=1
		#Zodiac background colors
		table.attach(Gtk.Label(delimiter),0,4,x,x+1,xoptions=Gtk.AttachOptions.FILL,xpadding=10)
		x+=1
		table.attach(Gtk.Label(_("Zodiac Background Colors")),0,4,x,x+1,xoptions=Gtk.AttachOptions.FILL,xpadding=10)
		x+=1
		table.attach(Gtk.Label(delimiter),0,4,x,x+1,xoptions=Gtk.AttachOptions.FILL,xpadding=10)
		x+=1

		for i in range(12):
			self.SCdata.append({})
			self.SCdata[-1]['key']="zodiac_bg_%s"%(i)
			self.SCdata[-1]['name']=Gtk.Label(openAstro.zodiac[i])
			self.SCdata[-1]['code'] = Gtk.Entry()
			self.SCdata[-1]['code'].set_max_length(25)
			self.SCdata[-1]['code'].set_width_chars(10)
			self.SCdata[-1]['code'].set_text(openAstro.colors["zodiac_bg_%s"%(i)])
			self.SCdata[-1]['code'].modify_base(Gtk.StateFlags.NORMAL, Gdk.color_parse(openAstro.colors["zodiac_bg_%s"%(i)]))
			self.SCdata[-1]['button'] = Gtk.Button(stock=Gtk.STOCK_SELECT_COLOR)
			self.SCdata[-1]['button'].connect("clicked", self.settingsColorsChanger, len(self.SCdata)-1)
			self.SCdata[-1]['reset'] = Gtk.Button(_("Default"))
			self.SCdata[-1]['reset'].connect("clicked", self.settingsColorsReset, len(self.SCdata)-1)

			table.attach(self.SCdata[-1]['name'], 0, 1, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
			table.attach(self.SCdata[-1]['code'], 1, 2, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
			table.attach(self.SCdata[-1]['button'], 2, 3, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
			table.attach(self.SCdata[-1]['reset'], 3, 4, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
			x+=1

		#Circle and Line Colors
		table.attach(Gtk.Label(delimiter),0,4,x,x+1,xoptions=Gtk.AttachOptions.FILL,xpadding=10)
		x+=1
		table.attach(Gtk.Label(_("Circles and Lines Colors")),0,4,x,x+1,xoptions=Gtk.AttachOptions.FILL,xpadding=10)
		x+=1
		table.attach(Gtk.Label(delimiter),0,4,x,x+1,xoptions=Gtk.AttachOptions.FILL,xpadding=10)
		x+=1
		for i in range(3):
			self.SCdata.append({})
			self.SCdata[-1]['key']="zodiac_radix_ring_%s"%(i)
			self.SCdata[-1]['name']=Gtk.Label("%s %s" %(_("Radix Ring"),(i+1)) )
			self.SCdata[-1]['code'] = Gtk.Entry()
			self.SCdata[-1]['code'].set_max_length(25)
			self.SCdata[-1]['code'].set_width_chars(10)
			self.SCdata[-1]['code'].set_text(openAstro.colors["zodiac_radix_ring_%s"%(i)])
			self.SCdata[-1]['code'].modify_base(Gtk.StateFlags.NORMAL, Gdk.color_parse(openAstro.colors["zodiac_radix_ring_%s"%(i)]))
			self.SCdata[-1]['button'] = Gtk.Button(stock=Gtk.STOCK_SELECT_COLOR)
			self.SCdata[-1]['button'].connect("clicked", self.settingsColorsChanger, len(self.SCdata)-1)
			self.SCdata[-1]['reset'] = Gtk.Button(_("Default"))
			self.SCdata[-1]['reset'].connect("clicked", self.settingsColorsReset, len(self.SCdata)-1)

			table.attach(self.SCdata[-1]['name'], 0, 1, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
			table.attach(self.SCdata[-1]['code'], 1, 2, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
			table.attach(self.SCdata[-1]['button'], 2, 3, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
			table.attach(self.SCdata[-1]['reset'], 3, 4, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
			x+=1

		for i in range(4):
			self.SCdata.append({})
			self.SCdata[-1]['key']="zodiac_transit_ring_%s"%(i)
			self.SCdata[-1]['name']=Gtk.Label("%s %s" %(_("Transit Ring"),(i+1)) )
			self.SCdata[-1]['code'] = Gtk.Entry()
			self.SCdata[-1]['code'].set_max_length(25)
			self.SCdata[-1]['code'].set_width_chars(10)
			self.SCdata[-1]['code'].set_text(openAstro.colors["zodiac_transit_ring_%s"%(i)])
			self.SCdata[-1]['code'].modify_base(Gtk.StateFlags.NORMAL, Gdk.color_parse(openAstro.colors["zodiac_transit_ring_%s"%(i)]))
			self.SCdata[-1]['button'] = Gtk.Button(stock=Gtk.STOCK_SELECT_COLOR)
			self.SCdata[-1]['button'].connect("clicked", self.settingsColorsChanger, len(self.SCdata)-1)
			self.SCdata[-1]['reset'] = Gtk.Button(_("Default"))
			self.SCdata[-1]['reset'].connect("clicked", self.settingsColorsReset, len(self.SCdata)-1)

			table.attach(self.SCdata[-1]['name'], 0, 1, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
			table.attach(self.SCdata[-1]['code'], 1, 2, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
			table.attach(self.SCdata[-1]['button'], 2, 3, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
			table.attach(self.SCdata[-1]['reset'], 3, 4, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
			x+=1

		self.SCdata.append({})
		self.SCdata[-1]['key']="houses_radix_line"
		self.SCdata[-1]['name']=Gtk.Label(_("Cusp Radix"))
		self.SCdata[-1]['code'] = Gtk.Entry()
		self.SCdata[-1]['code'].set_max_length(25)
		self.SCdata[-1]['code'].set_width_chars(10)
		self.SCdata[-1]['code'].set_text(openAstro.colors["houses_radix_line"])
		self.SCdata[-1]['code'].modify_base(Gtk.StateFlags.NORMAL, Gdk.color_parse(openAstro.colors["houses_radix_line"]))
		self.SCdata[-1]['button'] = Gtk.Button(stock=Gtk.STOCK_SELECT_COLOR)
		self.SCdata[-1]['button'].connect("clicked", self.settingsColorsChanger, len(self.SCdata)-1)
		self.SCdata[-1]['reset'] = Gtk.Button(_("Default"))
		self.SCdata[-1]['reset'].connect("clicked", self.settingsColorsReset, len(self.SCdata)-1)

		table.attach(self.SCdata[-1]['name'], 0, 1, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
		table.attach(self.SCdata[-1]['code'], 1, 2, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
		table.attach(self.SCdata[-1]['button'], 2, 3, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
		table.attach(self.SCdata[-1]['reset'], 3, 4, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
		x+=1

		self.SCdata.append({})
		self.SCdata[-1]['key']="houses_transit_line"
		self.SCdata[-1]['name']=Gtk.Label(_("Cusp Transit"))
		self.SCdata[-1]['code'] = Gtk.Entry()
		self.SCdata[-1]['code'].set_max_length(25)
		self.SCdata[-1]['code'].set_width_chars(10)
		self.SCdata[-1]['code'].set_text(openAstro.colors["houses_transit_line"])
		self.SCdata[-1]['code'].modify_base(Gtk.StateFlags.NORMAL, Gdk.color_parse(openAstro.colors["houses_transit_line"]))
		self.SCdata[-1]['button'] = Gtk.Button(stock=Gtk.STOCK_SELECT_COLOR)
		self.SCdata[-1]['button'].connect("clicked", self.settingsColorsChanger, len(self.SCdata)-1)
		self.SCdata[-1]['reset'] = Gtk.Button(_("Default"))
		self.SCdata[-1]['reset'].connect("clicked", self.settingsColorsReset, len(self.SCdata)-1)

		table.attach(self.SCdata[-1]['name'], 0, 1, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
		table.attach(self.SCdata[-1]['code'], 1, 2, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
		table.attach(self.SCdata[-1]['button'], 2, 3, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
		table.attach(self.SCdata[-1]['reset'], 3, 4, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
		x+=1

		#Zodiac icon colors
		table.attach(Gtk.Label(delimiter),0,4,x,x+1,xoptions=Gtk.AttachOptions.FILL,xpadding=10)
		x+=1
		table.attach(Gtk.Label(_("Zodiac Icon Colors")),0,4,x,x+1,xoptions=Gtk.AttachOptions.FILL,xpadding=10)
		x+=1
		table.attach(Gtk.Label(delimiter),0,4,x,x+1,xoptions=Gtk.AttachOptions.FILL,xpadding=10)
		x+=1
		for i in range(12):
			self.SCdata.append({})
			self.SCdata[-1]['key']="zodiac_icon_%s"%(i)
			self.SCdata[-1]['name']=Gtk.Label(openAstro.zodiac[i])
			self.SCdata[-1]['code'] = Gtk.Entry()
			self.SCdata[-1]['code'].set_max_length(25)
			self.SCdata[-1]['code'].set_width_chars(10)
			self.SCdata[-1]['code'].set_text(openAstro.colors["zodiac_icon_%s"%(i)])
			self.SCdata[-1]['code'].modify_base(Gtk.StateFlags.NORMAL, Gdk.color_parse(openAstro.colors["zodiac_icon_%s"%(i)]))
			self.SCdata[-1]['button'] = Gtk.Button(stock=Gtk.STOCK_SELECT_COLOR)
			self.SCdata[-1]['button'].connect("clicked", self.settingsColorsChanger, len(self.SCdata)-1)
			self.SCdata[-1]['reset'] = Gtk.Button(_("Default"))
			self.SCdata[-1]['reset'].connect("clicked", self.settingsColorsReset, len(self.SCdata)-1)

			table.attach(self.SCdata[-1]['name'], 0, 1, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
			table.attach(self.SCdata[-1]['code'], 1, 2, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
			table.attach(self.SCdata[-1]['button'], 2, 3, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
			table.attach(self.SCdata[-1]['reset'], 3, 4, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
			x+=1

		#Aspects colors
		table.attach(Gtk.Label(delimiter),0,4,x,x+1,xoptions=Gtk.AttachOptions.FILL,xpadding=10)
		x+=1
		table.attach(Gtk.Label(_("Aspects Colors")),0,4,x,x+1,xoptions=Gtk.AttachOptions.FILL,xpadding=10)
		x+=1
		table.attach(Gtk.Label(delimiter),0,4,x,x+1,xoptions=Gtk.AttachOptions.FILL,xpadding=10)
		x+=1
		for i in range(len(openAstro.aspects)):
			self.SCdata.append({})
			self.SCdata[-1]['key']="aspect_%s"%(openAstro.aspects[i]['degree'])
			self.SCdata[-1]['name']=Gtk.Label(openAstro.aspects[i]['name'])
			self.SCdata[-1]['code'] = Gtk.Entry()
			self.SCdata[-1]['code'].set_max_length(25)
			self.SCdata[-1]['code'].set_width_chars(10)
			self.SCdata[-1]['code'].set_text(openAstro.colors["aspect_%s"%(openAstro.aspects[i]['degree'])])

			self.SCdata[-1]['code'].modify_base(Gtk.StateFlags.NORMAL, Gdk.color_parse(openAstro.colors["aspect_%s"%(openAstro.aspects[i]['degree'])]))
			self.SCdata[-1]['button'] = Gtk.Button(stock=Gtk.STOCK_SELECT_COLOR)
			self.SCdata[-1]['button'].connect("clicked", self.settingsColorsChanger, len(self.SCdata)-1)
			self.SCdata[-1]['reset'] = Gtk.Button(_("Default"))
			self.SCdata[-1]['reset'].connect("clicked", self.settingsColorsReset, len(self.SCdata)-1)

			table.attach(self.SCdata[-1]['name'], 0, 1, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
			table.attach(self.SCdata[-1]['code'], 1, 2, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
			table.attach(self.SCdata[-1]['button'], 2, 3, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
			table.attach(self.SCdata[-1]['reset'], 3, 4, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
			x+=1

		#Planet colors
		table.attach(Gtk.Label(delimiter),0,4,x,x+1,xoptions=Gtk.AttachOptions.FILL,xpadding=10)
		x+=1
		table.attach(Gtk.Label(_("Planet Colors")),0,4,x,x+1,xoptions=Gtk.AttachOptions.FILL,xpadding=10)
		x+=1
		table.attach(Gtk.Label(delimiter),0,4,x,x+1,xoptions=Gtk.AttachOptions.FILL,xpadding=10)
		x+=1
		for i in range(len(openAstro.planets)):
			self.SCdata.append({})
			self.SCdata[-1]['key']="planet_%s"%(i)
			self.SCdata[-1]['name']=Gtk.Label(openAstro.planets[i]['name'])
			self.SCdata[-1]['code'] = Gtk.Entry()
			self.SCdata[-1]['code'].set_max_length(25)
			self.SCdata[-1]['code'].set_width_chars(10)
			self.SCdata[-1]['code'].set_text(openAstro.colors["planet_%s"%(i)])
			self.SCdata[-1]['code'].modify_base(Gtk.StateFlags.NORMAL, Gdk.color_parse(openAstro.colors["planet_%s"%(i)]) )
			self.SCdata[-1]['button'] = Gtk.Button(stock=Gtk.STOCK_SELECT_COLOR)
			self.SCdata[-1]['button'].connect("clicked", self.settingsColorsChanger, len(self.SCdata)-1)
			self.SCdata[-1]['reset'] = Gtk.Button(_("Default"))
			self.SCdata[-1]['reset'].connect("clicked", self.settingsColorsReset, len(self.SCdata)-1)

			table.attach(self.SCdata[-1]['name'], 0, 1, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
			table.attach(self.SCdata[-1]['code'], 1, 2, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
			table.attach(self.SCdata[-1]['button'], 2, 3, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
			table.attach(self.SCdata[-1]['reset'], 3, 4, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
			x+=1

		#Lunar phase colors
		table.attach(Gtk.Label(delimiter),0,4,x,x+1,xoptions=Gtk.AttachOptions.FILL,xpadding=10)
		x+=1
		table.attach(Gtk.Label(_("Lunar Phase Colors")),0,4,x,x+1,xoptions=Gtk.AttachOptions.FILL,xpadding=10)
		x+=1
		table.attach(Gtk.Label(delimiter),0,4,x,x+1,xoptions=Gtk.AttachOptions.FILL,xpadding=10)
		x+=1
		for i in range(3):
			self.SCdata.append({})
			self.SCdata[-1]['key']="lunar_phase_%s"%(i)
			self.SCdata[-1]['name']=Gtk.Label("lunar_phase_%s"%(i))
			self.SCdata[-1]['code'] = Gtk.Entry()
			self.SCdata[-1]['code'].set_max_length(25)
			self.SCdata[-1]['code'].set_width_chars(10)
			self.SCdata[-1]['code'].set_text(openAstro.colors["lunar_phase_%s"%(i)])
			self.SCdata[-1]['code'].modify_base(Gtk.StateFlags.NORMAL, Gdk.color_parse(openAstro.colors["lunar_phase_%s"%(i)]) )
			self.SCdata[-1]['button'] = Gtk.Button(stock=Gtk.STOCK_SELECT_COLOR)
			self.SCdata[-1]['button'].connect("clicked", self.settingsColorsChanger, len(self.SCdata)-1)
			self.SCdata[-1]['reset'] = Gtk.Button(_("Default"))
			self.SCdata[-1]['reset'].connect("clicked", self.settingsColorsReset, len(self.SCdata)-1)

			table.attach(self.SCdata[-1]['name'], 0, 1, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
			table.attach(self.SCdata[-1]['code'], 1, 2, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
			table.attach(self.SCdata[-1]['button'], 2, 3, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
			table.attach(self.SCdata[-1]['reset'], 3, 4, x, x+1, xoptions=Gtk.AttachOptions.FILL, xpadding=10)
			x+=1

		#make the ui layout with ok button
		scrolledwindow = Gtk.ScrolledWindow()
		scrolledwindow.set_border_width(5)
		scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)
		self.win_SC.vbox.pack_start(scrolledwindow, True, True, 0)
		scrolledwindow.add_with_viewport(table)

		#ok button
		button = Gtk.Button(stock=Gtk.STOCK_OK)
		button.connect("clicked", self.settingsColorsSubmit)
		button.set_can_default(True)
		self.win_SC.action_area.pack_start(button, True, True, 0)
		button.grab_default()

		#cancel button
		button = Gtk.Button(stock=Gtk.STOCK_CANCEL)
		button.connect("clicked", lambda w: self.win_SC.destroy())
		self.win_SC.action_area.pack_start(button, True, True, 0)

		self.win_SC.show_all()
		return

	def settingsColorsChanger(self, widget, count):
		input_color = Gdk.color_parse(self.SCdata[count]["code"].get_text())

		self.colorseldlg = Gtk.ColorSelectionDialog(_("Please select a color"),parent=self.win_SC)
		colorsel = self.colorseldlg.get_color_selection()
		colorsel.set_current_color(input_color)
		colorsel.set_has_palette(True)
		response = self.colorseldlg.run()
		if response == Gtk.ResponseType.OK:
			output_color = colorsel.get_current_color()
			r=int( output_color.red / 257 )
			g=int( output_color.green / 257 )
			b=int( output_color.blue / 257 )
			self.SCdata[count]["code"].set_text("#%02X%02X%02X"%(r,g,b))
			self.SCdata[count]['code'].modify_base(Gtk.StateFlags.NORMAL, output_color)
		self.colorseldlg.hide()

		return

	def settingsColorsSubmit(self, widget):
		query=[]
		for i in range(len(self.SCdata)):
			sql = 'UPDATE color_codes SET code = "%s"' % (self.SCdata[i]['code'].get_text())
			sql += ' WHERE name = "%s"' % (self.SCdata[i]['key'])
			query.append(sql)

		#query
		db.query(query)
		#update colors
		openAstro.colors = db.getColors()
		#update chart
		self.updateChart()
		#destroy window
		self.win_SC.destroy()



	"""

	Menu item to edit options for label

	settingsLabel
	settingsLabelSubmit

	"""

	def settingsLabelReset(self, widget, id):
		self.SLdata[id]['value'].set_text(db.defaultLabel[self.SLdata[id]['name']])
		return

	def settingsLabel(self, obj):
		# create a new window
		self.win_SL = Gtk.Dialog(parent=self.window)
		self.win_SL.set_icon_from_file(cfg.iconWindow)
		self.win_SL.set_title(_("Label Settings"))
		self.win_SL.connect("delete_event", lambda w,e: self.win_SL.destroy())
		self.win_SL.move(150,150)
		self.win_SL.set_border_width(5)
		self.win_SL.set_size_request(540,500)

		#create a table
		table = Gtk.Table(len(openAstro.label), 3, False)
		table.set_border_width(10)
		table.set_col_spacings(0)
		table.set_row_spacings(0)

		#description
		table.set_row_spacing(0,8)
		label = Gtk.Label(_("Label"))
		table.attach(label, 0, 1, 0, 1)
		label = Gtk.Label(_("Value"))
		table.attach(label, 1, 2, 0, 1, xoptions=Gtk.AttachOptions.SHRINK, xpadding=10)

		self.SLdata = []
		x=1
		keys = list(openAstro.label.keys())
		keys.sort()
		for key in keys:
			value=openAstro.label[key]
			self.SLdata.append({})
			self.SLdata[-1]['name'] = key
			self.SLdata[-1]['value'] = Gtk.Entry()
			self.SLdata[-1]['value'].set_max_length(50)
			self.SLdata[-1]['value'].set_width_chars(25)
			self.SLdata[-1]['value'].set_text(value)
			self.SLdata[-1]['reset'] = Gtk.Button(_("Default"))
			self.SLdata[-1]['reset'].connect("clicked", self.settingsLabelReset, len(self.SLdata)-1)
			table.attach(Gtk.Label(key), 0, 1, x, x+1, xoptions=Gtk.AttachOptions.SHRINK, xpadding=10)
			table.attach(self.SLdata[-1]['value'], 1, 2, x, x+1, xoptions=Gtk.AttachOptions.SHRINK, xpadding=2, ypadding=2)
			table.attach(self.SLdata[-1]['reset'], 2, 3, x, x+1, xoptions=Gtk.AttachOptions.SHRINK, xpadding=2, ypadding=2)
			x=x+1

		#make the ui layout with ok button
		scrolledwindow = Gtk.ScrolledWindow()
		scrolledwindow.set_border_width(5)
		scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)
		self.win_SL.vbox.pack_start(scrolledwindow, True, True, 0)
		scrolledwindow.add_with_viewport(table)

		#ok button
		button = Gtk.Button(stock=Gtk.STOCK_OK)
		button.connect("clicked", self.settingsLabelSubmit, self.SLdata)
		button.set_can_default(True)
		self.win_SL.action_area.pack_start(button, True, True, 0)
		button.grab_default()

		#cancel button
		button = Gtk.Button(stock=Gtk.STOCK_CANCEL)
		button.connect("clicked", lambda w: self.win_SL.destroy())
		self.win_SL.action_area.pack_start(button, True, True, 0)

		self.win_SL.show_all()
		return

	def settingsLabelSubmit(self, widget, data):
		query=[]
		for i in range(len(data)):
			if data[i]['value'].get_text() != openAstro.label[data[i]['name']]:
				sql = 'UPDATE label SET value = "%s" WHERE name = "%s"'%(data[i]['value'].get_text(),data[i]['name'])
				query.append(sql)
		#query
		db.query(query)
		#update label
		openAstro.label = db.getLabel()
		#update chart
		self.updateChart()
		#destroy window
		self.win_SL.destroy()


	"""

		Update the chart with input list data

	"""

	def updateChartList(self, b, list):
		openAstro.type="Radix"
		openAstro.charttype=openAstro.label["radix"]
		openAstro.name=str(list["name"])
		openAstro.year=int(list["year"])
		openAstro.month=int(list["month"])
		openAstro.day=int(list["day"])
		openAstro.hour=float(list["hour"])
		openAstro.geolon=float(list["geolon"])
		openAstro.geolat=float(list["geolat"])
		openAstro.altitude=int(list["altitude"])
		openAstro.location=str(list["location"])
		openAstro.timezone=float(list["timezone"])
		openAstro.countrycode=''
		if "countrycode" in list:
			openAstro.countrycode=list["countrycode"]
		if "timezonestr" in list:
			openAstro.timezonestr=list["timezonestr"]
		else:
			openAstro.timezonestr=db.gnearest(openAstro.geolat,openAstro.geolon)['timezonestr']
		openAstro.geonameid=None
		if "geonameid" in list:
			openAstro.geonameid=list['geonameid']

		openAstro.utcToLocal()
		openAstro.makeSVG()
		self.draw.queue_draw()
		self.draw.setSVG(self.tempfilename)

	def updateChart(self):
		openAstro.makeSVG()
		self.draw.queue_draw()
		self.draw.setSVG(self.tempfilename)

	def updateChartData(self):
		#check for internet connection
		if self.iconn:
			result = geoname.search(self.geoLoc.get_text(),self.geoCC.get_text())
			if result:
				self.geoLocFound = True
				lat=float(result[0]['lat'])
				lon=float(result[0]['lng'])
				gid=int(result[0]['geonameId'])
				cc=result[0]['countryCode']
				tzstr=result[0]['timezonestr']
				loc='%s, %s' % (result[0]['name'],result[0]['countryName'])
				dprint('updateChartData: %s,%s found; %s %s %s' % (
					self.geoLoc.get_text(),self.geoCC.get_text(),lat,lon,loc))
			else:
				self.geoLocFound = False
				#revert to defaults
				lat=openAstro.geolat
				lon=openAstro.geolon
				loc=openAstro.location
				cc=openAstro.countrycode
				tzstr=openAstro.timezonestr
				gid=openAstro.geonameid
				dprint('updateChartData: %s,%s not found, reverting to defaults' % (
					self.geoLoc.get_text(),self.geoCC.get_text()) )
				self.geoLoc.set_text(_('City not found! Try Again.'))
				return
		else:
			#using geonames database
			self.geoLocFound = True
			lat = float(self.GEON_lat)
			lon = float(self.GEON_lon)
			loc = self.GEON_loc
			cc = self.GEON_cc
			tzstr = self.GEON_tzstr
			gid = self.GEON_id

		#calculate timezone
		openAstro.timezonestr = tzstr
		openAstro.geonameid = gid

		#aware datetime object
		dt_input = datetime.datetime(int(self.dateY.get_text()), int(self.dateM.get_text()), int(self.dateD.get_text()), int(self.eH.get_text()), int(self.eM.get_text()), int(self.eS.get_text()))
		dt = pytz.timezone(openAstro.timezonestr).localize(dt_input)
		dprint( dt.strftime('%Y-%m-%d %H:%M:%S %Z%z') )
		dprint( 'Daylight Saving Time: %s' %((dt.dst().seconds / 3600.0)) )

		#naive datetime object UTC
		dt_utc = dt.replace(tzinfo=None) - dt.utcoffset()

		#set globals
		openAstro.year = dt_utc.year
		openAstro.month = dt_utc.month
		openAstro.day = dt_utc.day
		openAstro.hour = openAstro.decHourJoin(dt_utc.hour, dt_utc.minute, dt_utc.second)
		openAstro.timezone = openAstro.offsetToTz(dt.utcoffset())
		openAstro.name = self.name.get_text()

		#location
		openAstro.geolat=lat
		openAstro.geolon=lon
		openAstro.location=loc
		openAstro.countrycode=cc

		#update local time
		openAstro.utcToLocal()

		#update labels
		labelDateStr = str(openAstro.year_loc)+'-%(#1)02d-%(#2)02d' % {'#1':openAstro.month_loc,'#2':openAstro.day_loc}
		self.labelDate.set_text(labelDateStr)
		labelTzStr = '%(#1)02d:%(#2)02d:%(#3)02d' % {'#1':openAstro.hour_loc,'#2':openAstro.minute_loc,'#3':openAstro.second_loc} + openAstro.decTzStr(openAstro.timezone)
		self.labelTz.set_text(labelTzStr)
		self.ename.set_text(openAstro.name)
		self.entry2.set_text(' %s: %s\n %s: %s\n %s: %s' % ( _('Latitude'),lat,_('Longitude'),lon,_('Location'),loc) )

	def updateUI(self):

		#remove old actiongroup
		try:
			self.uimanager.remove_action_group(self.actiongroup)
		except AttributeError:
			pass

		#create new actiongroup
		self.actiongroup = Gtk.ActionGroup('UIManagerExample')

		#remove old ui's
		try:
			self.uimanager.remove_ui(self.ui_mid_history)
			self.uimanager.remove_ui(self.ui_mid_quickopendatabase)
		except AttributeError:
			pass

		#new merge id's
		self.ui_mid_history = self.uimanager.new_merge_id()
		self.ui_mid_quickopendatabase = self.uimanager.new_merge_id()

		# Add actions
		self.actiongroup.add_actions(self.actions)
		self.actiongroup.get_action('Quit').set_property('short-label', _('Quit') )

		self.actiongroup.add_radio_actions([
			('z80', None, '_80%', None,'80%', 0),
			('z100', Gtk.STOCK_ZOOM_100, '_100%', None,'100%', 1),
         ('z150', None, '_150%', None,'150%', 2),
         ('z200', None, '_200%', None,'200%', 3),
         ], 1, self.zoom)

		#create history actions
		history=db.history
		history.reverse()
		for i in range(10):
			if i < len(history):
				label=history[i][1]
				visible=True
				list=history[i]
			else:
				label='empty'
				visible=False
				list=[]
			self.uimanager.add_ui(self.ui_mid_history, '/MenuBar/File/History', 'history%i'%(i), 'history%i'%(i), Gtk.UIManagerItemType.MENUITEM, False)
			action=Gtk.Action('history%i'%(i),label,None,False)
			action.connect('activate',self.updateChartList,list)
			action.set_visible(visible)
			self.actiongroup.add_action(action)

		#create quickdatabaseopen actions
		self.DB = db.getDatabase()
		for i in range(len(self.DB)):
			self.uimanager.add_ui(self.ui_mid_quickopendatabase, '/MenuBar/Event/QuickOpenDatabase', 'quickopendatabase%s'%(i), 'quickopendatabase%s'%(i), Gtk.UIManagerItemType.MENUITEM, False)
			action=Gtk.Action('quickopendatabase%s'%(i),self.DB[i]["name"],None,False)
			action.connect('activate',self.updateChartList,self.DB[i])
			action.set_visible(True)
			self.actiongroup.add_action(action)

		#update uimanager
		self.uimanager.insert_action_group(self.actiongroup, 0)
		self.uimanager.ensure_update()


	def eventDataNew(self, widget):
		#default location
		openAstro.location=openAstro.home_location
		openAstro.geolat=float(openAstro.home_geolat)
		openAstro.geolon=float(openAstro.home_geolon)
		openAstro.countrycode=openAstro.home_countrycode

		#timezone string, example Europe/Amsterdam
		now = datetime.datetime.now()
		openAstro.timezone_str = zonetab.nearest_tz(openAstro.geolat,openAstro.geolon,zonetab.timezones())[2]
		#aware datetime object
		dt_input = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)
		dt = pytz.timezone(openAstro.timezonestr).localize(dt_input)
		#naive utc datetime object
		dt_utc = dt.replace(tzinfo=None) - dt.utcoffset()

		#Default
		openAstro.name=_("New Chart")
		openAstro.charttype=openAstro.label["radix"]
		openAstro.year=dt_utc.year
		openAstro.month=dt_utc.month
		openAstro.day=dt_utc.day
		openAstro.hour=openAstro.decHourJoin(dt_utc.hour,dt_utc.minute,dt_utc.second)
		openAstro.timezone=openAstro.offsetToTz(dt.utcoffset())

		#Make locals
		openAstro.utcToLocal()

		#open editor
		self.eventData(widget, edit=False)
		return

	def eventData(self, widget, edit=False):
		self.settingsLocationMode = False

		# create a new window
		self.window2 = Gtk.Window(Gtk.WindowType.TOPLEVEL)
		self.window2.set_icon_from_file(cfg.iconWindow)
		self.window2.set_title(_("Edit Event Details"))
		self.window2.connect("delete_event", lambda w,e: self.window2.destroy())
		self.window2.move(150,150)
		self.window2.set_border_width(10)

		#check internet connection
		self.checkInternetConnection()

		#create a table
		table = Gtk.Table(5, 2, False)
		table.set_col_spacings(15)
		table.set_row_spacings(15)
		self.window2.add(table)

		#Name entry
		hbox = Gtk.HBox(False,5)
		table.attach(hbox,0,1,0,1)

		label=Gtk.Label(_("Name")+":")
		hbox.pack_start(label,False,False,0)

		self.name = Gtk.Entry()
		self.name.set_max_length(50)
		self.name.set_width_chars(25)
		self.name.set_text(openAstro.name)
		hbox.pack_start(self.name,False,False,0)

		#name entry ( non editable)
		self.ename = Gtk.Label(openAstro.name)
		table.attach(self.ename, 1, 2, 0, 1)

		#if connection use geocoders, else use geonames sql database

		#display of location (non editable)
		self.entry2 = Gtk.Label(' '+_('Latitude')+
			': %s\n '%openAstro.geolat+_('Longitude')+
			': %s\n '%openAstro.geolon+_('Location')+
			': %s' %openAstro.location)
		table.attach(self.entry2, 1, 2, 1, 2)

		#check for connection
		if self.iconn:
			hbox = Gtk.HBox(False,5)
			table.attach(hbox,0,1,1,2)
			#entry for location (editable)
			label=Gtk.Label(_("City")+": ")
			hbox.pack_start(label,False,False,0)

			self.geoLoc = Gtk.Entry()
			self.geoLoc.set_max_length(50)
			self.geoLoc.set_width_chars(20)
			self.geoLoc.set_text(openAstro.location.partition(',')[0])
			hbox.pack_start(self.geoLoc,False,False,0)

			label=Gtk.Label(" "+_("Country-code")+": ")
			hbox.pack_start(label,False,False,0)

			self.geoCC = Gtk.Entry()
			self.geoCC.set_max_length(2)
			self.geoCC.set_width_chars(2)
			self.geoCC.set_text(openAstro.countrycode)
			hbox.pack_start(self.geoCC,False,False,0)
		else:
			vbox=Gtk.VBox(False,5)
			table.attach(vbox,0,1,1,2)
			hbox=Gtk.HBox(False,5)
			#get nearest geoname
			self.GEON_nearest = db.gnearest(openAstro.geolat,openAstro.geolon)
			#continents
			self.contbox = Gtk.ComboBox()
			self.contstore = Gtk.ListStore(str,str)
			cell = Gtk.CellRendererText()
			self.contbox.pack_start(cell, True)
			self.contbox.add_attribute(cell, 'text', 0)
			hbox.pack_start(self.contbox,False,False,0)
			self.contbox.set_wrap_width(1)

			sql = 'SELECT * FROM continent ORDER BY name ASC'
			db.gquery(sql)
			continentinfo=[]
			self.searchcontinent={}
			i = 0
			activecont = 3
			for row in db.gcursor:
				self.searchcontinent[row['code']]=i
				if row['code'] == self.GEON_nearest['continent']:
					activecont=i
					self.GEON_nearest['continent']=None
				self.contstore.append([row['name'],row['code']])
				i += 1
			db.gclose()
			self.contbox.set_model(self.contstore)

			#countries
			self.countrybox = Gtk.ComboBox()
			cell = Gtk.CellRendererText()
			self.countrybox.pack_start(cell, True)
			self.countrybox.add_attribute(cell, 'text', 0)
			hbox.pack_start(self.countrybox,False,False,0)
			self.countrybox.set_wrap_width(1)
			self.countrybox.connect('changed', self.eventDataChangedCountrybox)

			#provinces
			self.provbox = Gtk.ComboBox()
			cell = Gtk.CellRendererText()
			self.provbox.pack_start(cell, True)
			self.provbox.add_attribute(cell, 'text', 0)
			hbox.pack_start(self.provbox,False,False,0)
			self.provbox.set_wrap_width(1)
			self.provbox.connect('changed', self.eventDataChangedProvbox)

			#cities
			self.citybox = Gtk.ComboBox()
			cell = Gtk.CellRendererText()
			self.citybox.pack_start(cell, True)
			self.citybox.add_attribute(cell, 'text', 0)
			hbox.pack_start(self.citybox,False,False,0)
			self.citybox.set_wrap_width(2)
			self.citybox.connect('changed', self.eventDataChangedCitybox)

			self.contbox.connect('changed', self.eventDataChangedContbox)
			self.contbox.set_active(activecont)

			#add search in database
			vbox.pack_start(hbox,False,False,0)
			hbox=Gtk.HBox(False,5)
			label=Gtk.Label(_("Search City")+":")
			hbox.pack_start(label,False,False,0)
			self.citysearch = Gtk.Entry()
			self.citysearch.set_max_length(34)
			self.citysearch.set_width_chars(24)
			hbox.pack_start(self.citysearch,False,False,0)
			self.citysearchbutton = Gtk.Button(_('Search'))
			self.citysearchbutton.connect("clicked", self.citySearch)
			self.citysearch.connect("activate", self.citySearch)
			hbox.pack_start(self.citysearchbutton,False,False,0)
			label=Gtk.Label("("+_("For example: London, GB")+")")
			hbox.pack_start(label,False,False,0)
			vbox.pack_start(hbox,False,False,0)

		#Year month day entry
		hbox = Gtk.HBox(False,5)
		table.attach(hbox, 0, 1, 2, 3)

		label=Gtk.Label(_("Year")+":")
		hbox.pack_start(label,False,False,0)

		self.dateY = Gtk.Entry()
		self.dateY.set_max_length(4)
		self.dateY.set_width_chars(4)
		self.dateY.set_text(str(openAstro.year_loc))
		hbox.pack_start(self.dateY,False,False,0)

		label=Gtk.Label(_("Month")+":")
		hbox.pack_start(label,False,False,0)

		self.dateM = Gtk.Entry()
		self.dateM.set_max_length(2)
		self.dateM.set_width_chars(2)
		self.dateM.set_text('%(#)02d' % {'#':openAstro.month_loc})
		hbox.pack_start(self.dateM,False,False,0)

		label=Gtk.Label("Day:")
		hbox.pack_start(label,False,False,0)

		self.dateD = Gtk.Entry()
		self.dateD.set_max_length(2)
		self.dateD.set_width_chars(2)
		self.dateD.set_text('%(#)02d' % {'#':openAstro.day_loc})
		hbox.pack_start(self.dateD,False,False,0)

		#dat entry (non editable)
		labelDateStr = str(openAstro.year_loc)+'-%(#1)02d-%(#2)02d' % {'#1':openAstro.month_loc,'#2':openAstro.day_loc}
		self.labelDate = Gtk.Label(labelDateStr)
		table.attach(self.labelDate, 1, 2, 2, 3)

		#time entry (editable) (Hour, Minutes, Seconds, Timezone)
		hbox = Gtk.HBox(False,5)
		table.attach(hbox, 0, 1, 3, 4)

		label=Gtk.Label(_("Hour")+":")
		hbox.pack_start(label,False,False,0)

		self.eH = Gtk.Entry()
		self.eH.set_max_length(2)
		self.eH.set_width_chars(2)
		self.eH.set_text('%(#)02d' % {'#':openAstro.hour_loc})
		hbox.pack_start(self.eH,False,False,0)

		label=Gtk.Label(_("Min")+":")
		hbox.pack_start(label,False,False,0)

		self.eM = Gtk.Entry()
		self.eM.set_max_length(2)
		self.eM.set_width_chars(2)
		self.eM.set_text('%(#)02d' % {'#':openAstro.minute_loc})
		hbox.pack_start(self.eM,False,False,0)

		label=Gtk.Label("Sec:")
		hbox.pack_start(label,False,False,0)

		self.eS = Gtk.Entry()
		self.eS.set_max_length(2)
		self.eS.set_width_chars(2)
		self.eS.set_text('%(#)02d' % {'#':openAstro.second_loc})
		hbox.pack_start(self.eS,False,False,0)

		#time entry (non editable)
		labelTzStr = '%(#1)02d:%(#2)02d:%(#3)02d' % {'#1':openAstro.hour_loc,'#2':openAstro.minute_loc,'#3':openAstro.second_loc} + openAstro.decTzStr(openAstro.timezone)
		self.labelTz = Gtk.Label(labelTzStr)
		table.attach(self.labelTz, 1, 2, 3, 4)

		#buttonbox
		buttonbox = Gtk.HBox(False, 5)
		table.attach(buttonbox, 0, 2, 4, 5)

		#save to database button
		if edit:
			self.savebutton = Gtk.Button(_('Save'),Gtk.STOCK_SAVE)
			self.savebutton.connect("clicked", self.openDatabaseEditAsk)
			buttonbox.pack_start(self.savebutton,False,False,0)
		else:
			self.savebutton = Gtk.Button(_('Add to Database'))
			self.savebutton.connect("clicked", self.eventDataSaveAsk)
			buttonbox.pack_start(self.savebutton,False,False,0)


		#Test button
		button = Gtk.Button(_('Test'),Gtk.STOCK_APPLY)
		button.connect("clicked", self.eventDataApply)
		buttonbox.pack_start(button,False,False,0)
  		#ok button
		if edit == False:
			button = Gtk.Button(stock=Gtk.STOCK_OK)
			button.connect("clicked", self.eventDataSubmit)
			#button.set_can_default(True)
			buttonbox.pack_start(button,False,False,0)
			button.set_can_default(True)
			button.grab_default()

		#cancel button
		button = Gtk.Button(stock=Gtk.STOCK_CANCEL)
		button.connect("clicked", lambda w: self.window2.destroy())
		buttonbox.pack_start(button,False,False,0)

		self.window2.show_all()
		return


	def citySearch(self, widget):

		#text entry
		city=self.citysearch.get_text()

		#look for country in search string
		isoalpha2=None
		if city.find(","):
			split = city.split(",")
			for x in range(len(split)):
				sql="SELECT * FROM countryinfo WHERE \
				(isoalpha2 LIKE ? OR name LIKE ?) LIMIT 1"
				y=split[x].strip()
				db.gquery(sql,(y,y))
				result=db.gcursor.fetchone()
				if result != None:
					isoalpha2=result["isoalpha2"]
					city=city.replace(split[x]+",","").replace(","+split[x],"").strip()
					#print "%s,%s"%(city,isoalpha2)
					break

		#normal search
		normal = city
		fuzzy = "%"+city+"%"
		if isoalpha2:
			extra = " AND country='%s'"%(isoalpha2)
		else:
			extra = ""

		sql = "SELECT * FROM geonames WHERE \
		(name LIKE ? OR asciiname LIKE ?)%s \
		LIMIT 1" %(extra)
		db.gquery(sql,(normal,normal))
		result=db.gcursor.fetchone()

		if result == None:
			sql = "SELECT * FROM geonames WHERE \
			(name LIKE ? OR asciiname LIKE ?)%s \
			LIMIT 1" %(extra)
			db.gquery(sql,(fuzzy,fuzzy))
			result=db.gcursor.fetchone()

		if result == None:
			sql = "SELECT * FROM geonames WHERE \
			(alternatenames LIKE ?)%s \
			LIMIT 1"%(extra)
			db.gquery(sql,(fuzzy,))
			result=db.gcursor.fetchone()

		if result != None:
			#set continent
			sql = "SELECT continent FROM countryinfo WHERE isoalpha2=? LIMIT 1"
			db.gquery(sql,(result["country"],))
			self.contbox.set_active(self.searchcontinent[db.gcursor.fetchone()[0]])
			#set country
			self.countrybox.set_active(self.searchcountry[result["country"]])
			#set admin1
			self.provbox.set_active(self.searchprov[result["admin1"]])
			#set city
			self.citybox.set_active(self.searchcity[result["geonameid"]])

		return


	def eventDataChangedContbox(self, combobox):
		model = combobox.get_model()
		index = combobox.get_active()

		store = Gtk.ListStore(str,str)
		store.clear()
		sql = "SELECT * FROM countryinfo WHERE continent=? ORDER BY name ASC"
		db.gquery(sql,(model[index][1],))
		list = []
		i=0
		activecountry=0
		self.searchcountry={}
		for row in db.gcursor:
			self.searchcountry[row['isoalpha2']]=i
			if self.GEON_nearest['country'] == row['isoalpha2']:
				activecountry=i
				self.GEON_nearest['country']=None
			list.append((row['name'],row['isoalpha2']))
			i+=1
		db.gclose()
		for i in range(len(list)):
			store.append(list[i])
		self.countrybox.set_model(store)
		self.countrybox.set_active(activecountry)
		return

	def eventDataChangedCountrybox(self, combobox):
		model = combobox.get_model()
		index = combobox.get_active()
		self.provlist = Gtk.ListStore(str,str,str,str)
		self.provlist.clear()
		sql = "SELECT * FROM admin1codes WHERE country=? ORDER BY admin1 ASC"
		db.gquery(sql,(model[index][1],))
		list = []
		i=0
		activeprov=0
		self.searchprov={}
		for row in db.gcursor:
			self.searchprov[row["admin1"]] = i
			if self.GEON_nearest['admin1'] == row['admin1']:
				activeprov=i
				self.GEON_nearest['admin1'] = None
			list.append((row['province'],row['country'],row['admin1'],model[index][0]))
			i+=1
		db.gclose()
		for i in range(len(list)):
			self.provlist.append(list[i])
		self.provbox.set_model(self.provlist)
		self.provbox.set_active(activeprov)
		return

	def eventDataChangedProvbox(self, combobox):
		model = combobox.get_model()
		index = combobox.get_active()

		self.citylist = Gtk.ListStore(str,str,str,str,str,str,str,str)
		self.citylist.clear()
		sql = 'SELECT * FROM geonames WHERE country=? AND admin1=? ORDER BY name ASC'
		db.gquery(sql,(model[index][1],model[index][2]))
		list = []
		i=0
		activecity=0
		self.searchcity={}
		for row in db.gcursor:
			self.searchcity[row["geonameid"]]=i
			if self.GEON_nearest['geonameid'] == row['geonameid']:
				activecity=i
				self.GEON_nearest['geonameid'] = None
			list.append((row['name'],str(row['latitude']),str(row['longitude']),model[index][3],model[index][0],row['country'],str(row['geonameid']),row['timezone']))
			i+=1
		db.gclose()
		for i in range(len(list)):
			self.citylist.append(list[i])
		self.citybox.set_model(self.citylist)
		self.citybox.set_active(activecity)
		return

	def eventDataChangedCitybox(self, combobox):
		model = combobox.get_model()
		index = combobox.get_active()
		#change label for eventdata
		self.GEON_lat = model[index][1]
		self.GEON_lon = model[index][2]
		self.GEON_loc = '%s, %s, %s' % (model[index][0],model[index][4],model[index][3])
		self.GEON_cc = model[index][5]
		self.GEON_id = model[index][6]
		self.GEON_tzstr = model[index][7]
		dprint( 'evenDataChangedCitybox: %s:%s:%s:%s:%s:%s' % (self.GEON_loc,self.GEON_lat,self.GEON_lon,self.GEON_cc,self.GEON_tzstr,self.GEON_id) )
		#settingslocationmode
		if self.settingsLocationMode:
			self.LLoc.set_text(_('Location')+': %s'%(self.GEON_loc))
			self.LLat.set_text(_('Latitude')+': %s'%(self.GEON_lat))
			self.LLon.set_text(_('Longitude')+': %s'%(self.GEON_lon))
		else:
			self.entry2.set_text(' %s: %s\n %s: %s\n %s: %s' % (
				_('Latitude'),self.GEON_lat,_('Longitude'),self.GEON_lon,_('Location'),self.GEON_loc) )


	def eventDataSaveAsk(self, widget):
		#check for duplicate name
		en = db.getDatabase()
		for i in range(len(en)):
			if en[i]["name"] == self.name.get_text():
				dialog=Gtk.Dialog(_('Duplicate'),self.window2,0,(Gtk.STOCK_OK, Gtk.ResponseType.DELETE_EVENT))
				dialog.set_icon_from_file(cfg.iconWindow)
				dialog.connect("response", lambda w,e: dialog.destroy())
				dialog.connect("close", lambda w,e: dialog.destroy())
				dialog.vbox.pack_start(Gtk.Label(_('There is allready an entry for this name, please choose another')),True,True,0)
				dialog.show_all()
				return
		#ask for confirmation
		dialog=Gtk.Dialog(_('Question'),self.window2,0,(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT, Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
		dialog.set_destroy_with_parent(True)
		dialog.set_icon_from_file(cfg.iconWindow)
		dialog.connect("close", lambda w,e: dialog.destroy())
		dialog.connect("response",self.eventDataSave)
		dialog.vbox.pack_start(Gtk.Label(_('Are you sure you want to save this entry to the database?')),True,True,0)
		dialog.show_all()
		return

	def eventDataSave(self, widget, response_id):
		if response_id == Gtk.ResponseType.ACCEPT:
			#update chart data
			self.updateChartData()
			#set query to save
			#add data from event_natal table
			sql='INSERT INTO event_natal \
				(id,name,year,month,day,hour,geolon,geolat,altitude,location,timezone,notes,image,countrycode,geonameid,timezonestr,extra)\
				 VALUES (null,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
			tuple=(openAstro.name,openAstro.year,openAstro.month,openAstro.day,openAstro.hour,
				openAstro.geolon,openAstro.geolat,openAstro.altitude,openAstro.location,
				openAstro.timezone,'','',openAstro.countrycode,openAstro.geonameid,openAstro.timezonestr,'')
			db.pquery([sql],[tuple])
			dprint('saved to database: '+openAstro.name)
			self.updateUI()
			widget.destroy()
		else:
			widget.destroy()
			dprint('rejected save to database')
		return

	def eventDataSubmit(self, widget):
		#check if no changes were made
		if self.name.get_text() == openAstro.name and \
		self.dateY.get_text() == str(openAstro.year_loc) and \
		self.dateM.get_text() == '%(#)02d' % {'#':openAstro.month_loc} and \
		self.dateD.get_text() == '%(#)02d' % {'#':openAstro.day_loc} and \
		self.eH.get_text() == '%(#)02d' % {'#':openAstro.hour_loc} and \
		self.eM.get_text() == '%(#)02d' % {'#':openAstro.minute_loc} and \
		self.eS.get_text() == '%(#)02d' % {'#':openAstro.second_loc}:
			if self.iconn and \
			self.geoCC.get_text() == openAstro.countrycode and \
			self.geoLoc.get_text() == openAstro.location.partition(',')[0]:
				#go ahead ;)
				self.window2.destroy()
				return

		#apply data
		self.eventDataApply( widget )

		if self.geoLocFound:
			self.window2.destroy()
			#update history
			db.addHistory()
			self.updateUI()
			return
		else:
			return

	def eventDataApply(self, widget):
		#update chart data
		openAstro.charttype=openAstro.label["radix"]
		openAstro.type="Radix"
		openAstro.transit=False
		self.updateChartData()

		#update chart
		self.updateChart()

	def quit_cb(self, b):
		dprint('Quitting program')
		Gtk.main_quit()
