###############################################################################
#
#   Raspberry Pi Weather Display
#
################################################################################
import os
import pygame
import time
import random
from pygame.locals import *
import calendar
import serial

import pywapi
import string

from icon_defs import *

mouseX, mouseY = 0, 0

# Small LCD Display.
class SmDisplay:
	screen = None;
	
	####################################################################
	def __init__(self):
		"Ininitializes a new pygame screen using the framebuffer"
		# Based on "Python GUI in Linux frame buffer"
		# http://www.karoltomala.com/blog/?p=679
		disp_no = os.getenv("DISPLAY")
		if disp_no:
			print "X Display = {0}".format(disp_no)
		
		# Check which frame buffer drivers are available
		# Start with fbcon since directfb hangs with composite output
		drivers = ['fbcon', 'directfb', 'svgalib']
		found = False
		for driver in drivers:
			# Make sure that SDL_VIDEODRIVER is set
			if not os.getenv('SDL_VIDEODRIVER'):
				os.putenv('SDL_VIDEODRIVER', driver)
			try:
				pygame.display.init()
			except pygame.error:
				print 'Driver: {0} failed.'.format(driver)
				continue
			found = True
			break

		if not found:
			raise Exception('No suitable video driver found!')
		
		size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
		print "Framebuffer Size: %d x %d" % (size[0], size[1])
		self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
		# Clear the screen to start
		self.screen.fill((0, 0, 0))        
		# Initialise font support
		pygame.font.init()
		# Render the screen
		pygame.mouse.set_visible(0)
		pygame.display.update()
		#for fontname in pygame.font.get_fonts():
		#        print fontname
		self.temp = 0
		self.feels_like = 0
		self.wind_speed = 0
		self.baro = 0.0
		self.wind_dir = 'S'
		self.humid = 0
		self.wLastUpdate = ''
		self.day = [ '', '', '', '' ]
		self.icon = [ 0, 0, 0, 0 ]
		self.rain = [ '', '', '', '' ]
		self.temps = [ ['',''], ['',''], ['',''], ['',''] ]


	####################################################################
	def __del__(self):
		"Destructor to make sure pygame shuts down, etc."

	####################################################################
	def UpdateWeather( self ):
		# Use Weather.com for source data.
		cc = 'current_conditions'
		f = 'forecasts'
		w = pywapi.get_weather_from_weather_com( '48085', units='imperial' )
		try:
			if ( w[cc]['last_updated'] != self.wLastUpdate ):
				self.wLastUpdate = w[cc]['last_updated']
				print "New Weather Update: " + self.wLastUpdate
				self.temp = string.lower( w[cc]['temperature'] )
				self.feels_like = string.lower( w[cc]['feels_like'] )
				self.wind_speed = string.lower( w[cc]['wind']['speed'] )
				self.baro = string.lower( w[cc]['barometer']['reading'] )
				self.wind_dir = string.upper( w[cc]['wind']['text'] )
				self.humid = string.upper( w[cc]['humidity'] )
				self.day[0] = w[f][0]['day_of_week']
				self.day[1] = w[f][1]['day_of_week']
				self.day[2] = w[f][2]['day_of_week']
				self.day[3] = w[f][3]['day_of_week']
				self.icon[0] = int(w[f][0]['day']['icon'])
				self.icon[1] = int(w[f][1]['day']['icon'])
				self.icon[2] = int(w[f][2]['day']['icon'])
				self.icon[3] = int(w[f][3]['day']['icon'])
				print 'Icon Index: ', self.icon[0], self.icon[1], self.icon[2], self.icon[3]
				#print 'File: ', sd+icons[self.icon[0]]
				self.rain[0] = w[f][0]['day']['chance_precip']
				self.rain[1] = w[f][1]['day']['chance_precip']
				self.rain[2] = w[f][2]['day']['chance_precip']
				self.rain[3] = w[f][3]['day']['chance_precip']
				if ( w[f][0]['high'] == 'N/A' ):
					self.temps[0][0] = '--'
				else:	
					self.temps[0][0] = w[f][0]['high'] + unichr(0x2109)
				self.temps[0][1] = w[f][0]['low'] + unichr(0x2109)
				self.temps[1][0] = w[f][1]['high'] + unichr(0x2109)
				self.temps[1][1] = w[f][1]['low'] + unichr(0x2109)
				self.temps[2][0] = w[f][2]['high'] + unichr(0x2109)
				self.temps[2][1] = w[f][2]['low'] + unichr(0x2109)
				self.temps[3][0] = w[f][3]['high'] + unichr(0x2109)
				self.temps[3][1] = w[f][3]['low'] + unichr(0x2109)
		except KeyError:
			print "Weather Error"


	####################################################################
	def disp_weather(self):
		# Fill the screen with black
		self.screen.fill( (0,0,0) )
		xmax = 656 - 35
		ymax = 416 - 5
		lines = 5
		lc = (255,255,255) 
		fn = "freesans"

		# Draw Screen Border
		pygame.draw.line( self.screen, lc, (0,0),(xmax,0), lines )
		pygame.draw.line( self.screen, lc, (0,0),(0,ymax), lines )
		pygame.draw.line( self.screen, lc, (0,ymax),(xmax,ymax), lines )	# Bottom
		pygame.draw.line( self.screen, lc, (xmax,0),(xmax,ymax+2), lines )
		pygame.draw.line( self.screen, lc, (0,ymax*0.15),(xmax,ymax*0.15), lines )
		pygame.draw.line( self.screen, lc, (0,ymax*0.5),(xmax,ymax*0.5), lines )
		pygame.draw.line( self.screen, lc, (xmax*0.25,ymax*0.5),(xmax*0.25,ymax), lines )
		pygame.draw.line( self.screen, lc, (xmax*0.5,ymax*0.15),(xmax*0.5,ymax), lines )
		pygame.draw.line( self.screen, lc, (xmax*0.75,ymax*0.5),(xmax*0.75,ymax), lines )

		# Time & Date
		font = pygame.font.SysFont( fn, int(ymax*0.125), bold=1 )	# Regular Font
		sfont = pygame.font.SysFont( fn, int(ymax*0.075), bold=1 )	# Small Font for Seconds

		tm1 = time.strftime( "%a, %b %d   %I:%M", time.localtime() )	# 1st part
		tm2 = time.strftime( "%S", time.localtime() )					# 2nd
		tm3 = time.strftime( " %P", time.localtime() )					# 

		rtm1 = font.render( tm1, True, lc )
		(tx1,ty1) = rtm1.get_size()
		rtm2 = sfont.render( tm2, True, lc )
		(tx2,ty2) = rtm2.get_size()
		rtm3 = font.render( tm3, True, lc )
		(tx3,ty3) = rtm3.get_size()

		tp = xmax / 2 - (tx1 + tx2 + tx3) / 2
		self.screen.blit( rtm1, (tp,1) )
		self.screen.blit( rtm2, (tp+tx1+3,8) )
		self.screen.blit( rtm3, (tp+tx1+tx2,1) )

		# Outside Temp
		font = pygame.font.SysFont( fn, int(ymax*(0.5-0.15)*0.9), bold=1 )
		txt = font.render( self.temp, True, lc )
		(tx,ty) = txt.get_size()
		# Show degree F symbol using magic unicode char in a smaller font size.
		dfont = pygame.font.SysFont( fn, int(ymax*(0.5-0.15)*0.5), bold=1 )
		dtxt = dfont.render( unichr(0x2109), True, lc )
		(tx2,ty2) = dtxt.get_size()
		x = xmax*0.27 - (tx*1.02 + tx2) / 2
		self.screen.blit( txt, (x,ymax*0.15) )
		#self.screen.blit( txt, (xmax*0.02,ymax*0.15) )
		x = x + (tx*1.02)
		self.screen.blit( dtxt, (x,ymax*0.2) )
		#self.screen.blit( dtxt, (xmax*0.02+tx*1.02,ymax*0.2) )

		# Conditions
		st = 0.16    # Yaxis Start Pos
		gp = 0.065   # Line Spacing Gap
		th = 0.06    # Text Height
		dh = 0.05    # Degree Symbol Height
		so = 0.01    # Degree Symbol Yaxis Offset
		xp = 0.52    # Xaxis Start Pos
		x2 = 0.78    # Second Column Xaxis Start Pos

		font = pygame.font.SysFont( fn, int(ymax*th), bold=1 )
		txt = font.render( 'Windchill:', True, lc )
		self.screen.blit( txt, (xmax*xp,ymax*st) )
		txt = font.render( self.feels_like, True, lc )
		self.screen.blit( txt, (xmax*x2,ymax*st) )
		(tx,ty) = txt.get_size()
		# Show degree F symbol using magic unicode char.
		dfont = pygame.font.SysFont( fn, int(ymax*dh), bold=1 )
		dtxt = dfont.render( unichr(0x2109), True, lc )
		self.screen.blit( dtxt, (xmax*x2+tx*1.01,ymax*(st+so)) )

		txt = font.render( 'Windspeed:', True, lc )
		self.screen.blit( txt, (xmax*xp,ymax*(st+gp*1)) )
		txt = font.render( self.wind_speed+' mph', True, lc )
		self.screen.blit( txt, (xmax*x2,ymax*(st+gp*1)) )

		txt = font.render( 'Direction:', True, lc )
		self.screen.blit( txt, (xmax*xp,ymax*(st+gp*2)) )
		txt = font.render( string.upper(self.wind_dir), True, lc )
		self.screen.blit( txt, (xmax*x2,ymax*(st+gp*2)) )

		txt = font.render( 'Barometer:', True, lc )
		self.screen.blit( txt, (xmax*xp,ymax*(st+gp*3)) )
		txt = font.render( self.baro + '"Hg', True, lc )
		self.screen.blit( txt, (xmax*x2,ymax*(st+gp*3)) )

		txt = font.render( 'Humidity:', True, lc )
		self.screen.blit( txt, (xmax*xp,ymax*(st+gp*4)) )
		txt = font.render( self.humid+'%', True, lc )
		self.screen.blit( txt, (xmax*x2,ymax*(st+gp*4)) )

		wx = 	0.125			# Sub Window Centers
		wy = 	0.510			# Sub Windows Yaxis Start
		th = 	0.060			# Text Height
		rpth = 	0.100			# Rain Present Text Height
		gp = 	0.065			# Line Spacing Gap
		ro = 	0.010 * xmax   	# "Rain:" Text Window Offset winthin window. 
		rpl =	5.95			# Rain percent line offset.

		font = pygame.font.SysFont( fn, int(ymax*th), bold=1 )
		rpfont = pygame.font.SysFont( fn, int(ymax*rpth), bold=1 )

		# Sub Window 1
		txt = font.render( 'Today:', True, lc )
		(tx,ty) = txt.get_size()
		self.screen.blit( txt, (xmax*wx-tx/2,ymax*(wy+gp*0)) )
		txt = font.render( self.temps[0][0] + ' / ' + self.temps[0][1], True, lc )
		(tx,ty) = txt.get_size()
		self.screen.blit( txt, (xmax*wx-tx/2,ymax*(wy+gp*5)) )
		#rtxt = font.render( 'Rain:', True, lc )
		#self.screen.blit( rtxt, (ro,ymax*(wy+gp*5)) )
		rptxt = rpfont.render( self.rain[0]+'%', True, lc )
		(tx,ty) = rptxt.get_size()
		self.screen.blit( rptxt, (xmax*wx-tx/2,ymax*(wy+gp*rpl)) )
		icon = pygame.image.load(sd + icons[self.icon[0]]).convert_alpha()
		(ix,iy) = icon.get_size()
		#icon2 = pygame.transform.scale( icon, (int(ix*1.5),int(iy*1.5)) )
		if ( iy < 90 ):
			yo = (90 - iy) / 2 
		else: 
			yo = 0
		self.screen.blit( icon, (xmax*wx-ix/2,ymax*(wy+gp*1.2)+yo) )

		# Sub Window 2
		txt = font.render( self.day[1]+':', True, lc )
		(tx,ty) = txt.get_size()
		self.screen.blit( txt, (xmax*(wx*3)-tx/2,ymax*(wy+gp*0)) )
		txt = font.render( self.temps[1][0] + ' / ' + self.temps[1][1], True, lc )
		(tx,ty) = txt.get_size()
		self.screen.blit( txt, (xmax*wx*3-tx/2,ymax*(wy+gp*5)) )
		#self.screen.blit( rtxt, (xmax*wx*2+ro,ymax*(wy+gp*5)) )
		rptxt = rpfont.render( self.rain[1]+'%', True, lc )
		(tx,ty) = rptxt.get_size()
		self.screen.blit( rptxt, (xmax*wx*3-tx/2,ymax*(wy+gp*rpl)) )
		icon = pygame.image.load(sd + icons[self.icon[1]]).convert_alpha()
		(ix,iy) = icon.get_size()
		#icon2 = pygame.transform.scale( icon, (int(ix*1.5),int(iy*1.5)) )
		if ( iy < 90 ):
			yo = (90 - iy) / 2 
		else: 
			yo = 0
		self.screen.blit( icon, (xmax*wx*3-ix/2,ymax*(wy+gp*1.2)+yo) )

		# Sub Window 3
		txt = font.render( self.day[2]+':', True, lc )
		(tx,ty) = txt.get_size()
		self.screen.blit( txt, (xmax*(wx*5)-tx/2,ymax*(wy+gp*0)) )
		txt = font.render( self.temps[2][0] + ' / ' + self.temps[2][1], True, lc )
		(tx,ty) = txt.get_size()
		self.screen.blit( txt, (xmax*wx*5-tx/2,ymax*(wy+gp*5)) )
		#self.screen.blit( rtxt, (xmax*wx*4+ro,ymax*(wy+gp*5)) )
		rptxt = rpfont.render( self.rain[2]+'%', True, lc )
		(tx,ty) = rptxt.get_size()
		self.screen.blit( rptxt, (xmax*wx*5-tx/2,ymax*(wy+gp*rpl)) )
		icon = pygame.image.load(sd + icons[self.icon[2]]).convert_alpha()
		(ix,iy) = icon.get_size()
		#icon2 = pygame.transform.scale( icon, (int(ix*1.5),int(iy*1.5)) )
		if ( iy < 90 ):
			yo = (90 - iy) / 2 
		else: 
			yo = 0
		self.screen.blit( icon, (xmax*wx*5-ix/2,ymax*(wy+gp*1.2)+yo) )

		# Sub Window 4
		txt = font.render( self.day[3]+':', True, lc )
		(tx,ty) = txt.get_size()
		self.screen.blit( txt, (xmax*(wx*7)-tx/2,ymax*(wy+gp*0)) )
		txt = font.render( self.temps[3][0] + ' / ' + self.temps[3][1], True, lc )
		(tx,ty) = txt.get_size()
		self.screen.blit( txt, (xmax*wx*7-tx/2,ymax*(wy+gp*5)) )
		#self.screen.blit( rtxt, (xmax*wx*6+ro,ymax*(wy+gp*5)) )
		rptxt = rpfont.render( self.rain[3]+'%', True, lc )
		(tx,ty) = rptxt.get_size()
		self.screen.blit( rptxt, (xmax*wx*7-tx/2,ymax*(wy+gp*rpl)) )
		icon = pygame.image.load(sd + icons[self.icon[3]]).convert_alpha()
		(ix,iy) = icon.get_size()
		#icon2 = pygame.transform.scale( icon, (int(ix*1.5),int(iy*1.5)) )
		if ( iy < 90 ):
			yo = (90 - iy) / 2 
		else: 
			yo = 0
		self.screen.blit( icon, (xmax*wx*7-ix/2,ymax*(wy+gp*1.2)+yo) )

		# Update the display
		pygame.display.update()

	####################################################################
	def disp_calendar(self):
		# Fill the screen with black
		self.screen.fill( (0,0,0) )
		xmax = 656 - 35
		ymax = 416 - 5
		lines = 5
		lc = (255,255,255) 
		sfn = "freemono"
		fn = "freesans"

		# Draw Screen Border
		pygame.draw.line( self.screen, lc, (0,0),(xmax,0), lines )
		pygame.draw.line( self.screen, lc, (0,0),(0,ymax), lines )
		pygame.draw.line( self.screen, lc, (0,ymax),(xmax,ymax), lines )
		pygame.draw.line( self.screen, lc, (xmax,0),(xmax,ymax), lines )
		pygame.draw.line( self.screen, lc, (0,ymax*0.15),(xmax,ymax*0.15), lines )

		# Time & Date
		font = pygame.font.SysFont( fn, int(ymax*0.125), bold=1 )		# Regular Font
		sfont = pygame.font.SysFont( sfn, int(ymax*0.075), bold=1 )		# Small Font for Seconds

		tm1 = time.strftime( "%a, %b %d   %I:%M", time.localtime() )	# 1st part
		tm2 = time.strftime( "%S", time.localtime() )					# 2nd
		tm3 = time.strftime( " %P", time.localtime() )					# 

		rtm1 = font.render( tm1, True, lc )
		(tx1,ty1) = rtm1.get_size()
		rtm2 = sfont.render( tm2, True, lc )
		(tx2,ty2) = rtm2.get_size()
		rtm3 = font.render( tm3, True, lc )
		(tx3,ty3) = rtm3.get_size()

		tp = xmax / 2 - (tx1 + tx2 + tx3) / 2
		self.screen.blit( rtm1, (tp,1) )
		self.screen.blit( rtm2, (tp+tx1+3,8) )
		self.screen.blit( rtm3, (tp+tx1+tx2,1) )

		# Conditions
		ys = 0.20		# Yaxis Start Pos
		xs = 0.20		# Xaxis Start Pos
		gp = 0.075	# Line Spacing Gap
		th = 0.06		# Text Height

		#cal = calendar.TextCalendar()
		cal = calendar.month( 2013, 8 ).splitlines()
		i = 0
		for cal_line in cal:
			txt = sfont.render( cal_line, True, lc )
			self.screen.blit( txt, (xmax*xs,ymax*(ys+gp*i)) )
			i = i + 1

		# Update the display
		pygame.display.update()

	def screen_cap( self ):
		pygame.image.save( self.screen, "screenshot.jpeg" )
		print "Screen capture complete."

#==============================================================

ser = serial.Serial( "/dev/ttyO0", 115200 )
ser.write( "x" )

# Display all the available fonts.
#print "Fonts: ", pygame.font.get_fonts()

mode = 'w'
# Create an instance of the lcd display class.
myDisp = SmDisplay()

running = True
s = ""
myDisp.UpdateWeather()
while running:
	# Process keyboard events.
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			if ( (event.key == K_KP_ENTER) or (event.key == K_q) ):
				running = False
			elif ( event.key == K_c ):
				mode = 'c'
			elif ( event.key == K_w ):
				mode = 'w'
			elif ( event.key == K_s ):
				myDisp.screen_cap()

	if ( mode == 'c' ):
		# Update / Refresh the display after each second.
		if ( s != time.strftime("%S") ):
			s = time.strftime("%S")
			myDisp.disp_calendar()
		
	if ( mode == 'w' ):
		# Update / Refresh the display after each second.
		if ( s != time.strftime("%S") ):
			s = time.strftime("%S")
			myDisp.disp_weather()	
			# ser.write( "Weather\r\n" )
		# Once the screen is updated, we have a full second to get the weather.
		# Once per minute, update the weather from the net.
		if ( int(s) == 0 ):
			myDisp.UpdateWeather()

	pygame.time.wait( 100 )


pygame.quit()

