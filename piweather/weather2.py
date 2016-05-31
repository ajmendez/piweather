import os, syslog
import pygame
import time
import pywapi
import string
from datetime import datetime
from setproctitle import setproctitle
setproctitle('pyscreen')
import subprocess


from daemon import *

# Weather Icons used with the following permissions:
#
# VClouds Weather Icons
# Created and copyrighted by VClouds - http://vclouds.deviantart.com/
#
# The icons are free to use for Non-Commercial use, but If you use want to use it with your art please credit me and put a link leading back to the icons DA page - http://vclouds.deviantart.com/gallery/#/d2ynulp
#
# *** Not to be used for commercial use without permission! 
# if you want to buy the icons for commercial use please send me a note - http://vclouds.deviantart.com/ ***

installPath = "/home/pi/tmp/screen/"

# location for Lincoln, UK on weather.com
weatherDotComLocationCode = 'USMD0018:1:US' # baltimore
weatherDotComLocationCode = '28669:4:US'

weatherDotComLocationCode = 'USCA1018:1:US'

# convert mph = kpd / kphToMph
kphToMph = 1.60934400061

# font colours
colourWhite = (255, 255, 255)
colourBlack = (0, 0, 0)

# update interval
updateRate = 60 # seconds

class pitft :
    screen = None;
    colourBlack = (0, 0, 0)
    
    def __init__(self):
        "Ininitializes a new pygame screen using the framebuffer"
        # Based on "Python GUI in Linux frame buffer"
        # http://www.karoltomala.com/blog/?p=679
        disp_no = os.getenv("DISPLAY")
        if disp_no:
            print "I'm running under X display = {0}".format(disp_no)

        os.putenv('SDL_FBDEV', '/dev/fb1')
        
        # Select frame buffer driver
        # Make sure that SDL_VIDEODRIVER is set
        driver = 'fbcon'
        if not os.getenv('SDL_VIDEODRIVER'):
            os.putenv('SDL_VIDEODRIVER', driver)
        try:
            pygame.display.init()
        except pygame.error:
            print 'Driver: {0} failed.'.format(driver)
            exit(0)
        
        size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        # Clear the screen to start
        self.screen.fill((0, 0, 0))        
        # Initialise font support
        pygame.font.init()
        # Render the screen
        pygame.display.update()

    def __del__(self):
        "Destructor to make sure pygame shuts down, etc."

# Create an instance of the PyScope class
mytft = pitft()

pygame.mouse.set_visible(False)

# set up the fonts
# choose the font
fontpath = pygame.font.match_font('dejavusansmono')
# set up 2 sizes
font = pygame.font.Font(fontpath, 20)
fontSm = pygame.font.Font(fontpath, 18)

# print 'done'
# mytft.screen.fill(colourBlack)
# icon = "26.png"
# logo = pygame.image.load(icon).convert()
# mytft.screen.blit(logo, (0, 0))
# pygame.display.update()
#
#
# time.sleep(1)
# print 'white'
# mytft.screen.fill(colourWhite)
# time.sleep(10)
# pygame.display.update()

def _temp(t):
    return u'{}\N{DEGREE SIGN}'.format(t)

def _show(x,y,text):
    text_surface = font.render(text, True, colourWhite)
    mytft.screen.blit(text_surface, (x, y))

def saferun(command):
    try:
        value = int(subprocess.check_output(command, shell=True).strip())
        if value > 1000:
            return '{:0,.1f}'.format(value/1000.0)
        else:
            return '{:,d}'.format(value)
    except Exception as e:
        return -1


while True:
    # retrieve data from weather.com
    weather = pywapi.get_weather_from_weather_com(weatherDotComLocationCode, units='imperial')
    
    # extract current data for today
    tmp = weather['forecasts'][0]
    today = '{dow}, {month} {day}'.format(
                dow=tmp['day_of_week'][0:3],
                month=tmp['date'][:3],
                day=tmp['date'][4:])
    now = datetime.now().strftime('%H:%M:%S')
    temperature = _temp(weather['current_conditions']['temperature'])
    
    forcasts = []
    # print(len(weather['forecasts']))
    for i,result in enumerate(weather['forecasts']):
        forcasts.append(
            dict(
                day = result['day_of_week'][0:3],
                low = _temp(result['low']),
                high = _temp(result['high']),
                precip = '{}%'.format(result['day']['chance_precip']),
            )
        )
        if i == 0:
            forcasts[-1]['day'] = 'Today'
        
    
    # blank the screen
    mytft.screen.fill(colourBlack)
    
    # Render the weather logo at 0,0
    # icon = installPath+ (weather_com_result['current_conditions']['icon']) + ".png"
    icon = '{:s}{:02d}.png'.format(installPath, int(weather['current_conditions']['icon']))
    logo = pygame.image.load(icon).convert()
    mytft.screen.blit(logo, (0, 0))
    
    # set the anchor for the current weather data text
    x = 140
    y = 5
    yo = 20
    
    # add current weather data text artifacts to the screen
    _show(x, y, today)
    y += yo

    _show(x, y, now)
    y += yo
    
    _show(x, y, temperature)
    y += yo
    

    # set X axis text anchor for the forecast text
    x = 5
    xo = 65
    
    for forcast in forcasts:
        y = 125
        
        _show(x,y, forcast['day'])
        y += yo
        
        _show(x,y, forcast['high'])
        y += yo
        
        _show(x,y, forcast['low'])
        y += yo
        
        _show(x,y, forcast['precip'])
        y += yo
        
        x += xo

    
    # set X axis text anchor for the forecast text
    x = 0
    y = 212
    print(saferun("tail -n 1  /tmp/piaware.out | cut -d ';' -f 2|cut -d ' ' -f 2"))
    info = 't:{tweets} u:{users} f:{flights}'.format(
        tweets = saferun("wc -l /home/pi/data/waze/stream_waze.json|cut -d ' ' -f 1 "),
        users = saferun("sqlite3 /home/pi/data/waze/data.db 'select count(*) from users'"),
        flights = saferun("tail -n 1  /tmp/piaware.out | cut -d ';' -f 2|cut -d ' ' -f 2"),
    )
    _show(x,y, info)
    
    # refresh the screen with all the changes
    pygame.display.update()
    
    # Wait
    time.sleep(updateRate)

# if __name__ == "__main__":
#     daemon = MyDaemon('/tmp/PiTFTWeather.pid', stdout='/tmp/PiTFTWeather.log', stderr='/tmp/PiTFTWeatherErr.log')
#     if len(sys.argv) == 2:
#         if 'start' == sys.argv[1]:
#             syslog.syslog(syslog.LOG_INFO, "Starting")
#             daemon.start()
#         elif 'stop' == sys.argv[1]:
#             syslog.syslog(syslog.LOG_INFO, "Stopping")
#             daemon.stop()
#         elif 'restart' == sys.argv[1]:
#             syslog.syslog(syslog.LOG_INFO, "Restarting")
#             daemon.restart()
#         else:
#             print "Unknown command"
#             sys.exit(2)
#         sys.exit(0)
#     else:
#         print "usage: %s start|stop|restart" % sys.argv[0]
#         sys.exit(2)
