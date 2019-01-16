'''

Copyright (c) 2019 Vanessa Sochat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from random import choice
from threading import Thread
from selenium import webdriver
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
import webbrowser
import json
import shutil
import re
import sys
import os


class BrowserServer(SimpleHTTPRequestHandler):
    '''here we subclass SimpleHTTPServer to capture error messages
    '''
    def log_message(self, format, *args):
        '''log to standard error with a date time string,
            and then call any subclass specific logging functions
        '''
        sys.stderr.write("%s - - [%s] %s\n" %
                     (self.address_string(),
                      self.log_date_time_string(),
                      format%args))

        # Workaround for error trying to GET html
        if not re.search("div",format%args) and not re.search("function",format%args):
            if re.search("404",format%args):
                raise IOError(format%args)

    def log_error(self, format, *args):
        '''log_error
        catch errors in the log_messages instead
        '''
        pass



class BrowserRobot(object):
    ''' bring up a server with a custom robot
        
        Defaults
        ==========

        pause_time: time to wait between browser commands
        port: a random choice between 8000 and 9999
    '''
  
    def __init__(self, **kwargs):
        self.Handler = BrowserServer
        if "port" in kwargs:
            self.port = kwargs['port']
        else:       
            self.port = choice(range(8000,9999))
        print('Selected port is %s' %self.port)
        self.httpd = TCPServer(("", self.port), self.Handler)
        self.server = Thread(target=self.httpd.serve_forever)
        self.server.setDaemon(True)
        self.server.start()
        self.started = True
        self.pause_time = 100
        self.browser = None
        self.headless = False
        self.display = None
        self.driver = "Chrome"
        if "browser" in kwargs:
            self.driver = kwargs['browser']


    def validate(self, folder):
        '''validate is the first entrypoint function for running an experiment
           or survey robot. It ensures that the content is valid,
           and then calls _validate (should be defined in subclass)'''
            
        validator = ExperimentValidator()
        valid = validator.validate(folder)

        if valid is True:

            # IF missing favicon, add
            self._check_favicon(folder)

            valid = self._validate(folder)
            print("[done] stopping web server...")
            self.httpd.server_close()
        else:
            print('%s is not valid, skipping robot testing.' %folder)


    def check_errors(self):
   
        if self.browser is not None:
            # Look at log from last call
            log = self.browser.get_log("browser")
            for log_entry in log:
                assert_equal(log_entry["level"] in ["WARNING","INFO"],True)


    def get_and_wait(self, url, sleep_seconds=0):
        '''a helper function to get a browser and wait a randomly
           selected number of seconds between 0 and 2'''
        self.get_browser()
        wait_time = choice([0, 0.25, 0.5, 0.75, 1, 1.5, 2])
        self.browser.implicitly_wait(wait_time) # if error, will wait 3 seconds and retry
        self.browser.set_page_load_timeout(10)
        self.get_page(url)
        sleep(sleep_seconds)


    def get_browser(self, name=None):
        '''get_browser 
           return a browser if it hasn't been initialized yet
        '''
        if name is None:
            name=self.driver

        log_path = "%s-driver.log" % name.lower()

        if self.browser is None:
            options = self.get_options()
            if name.lower() == "Firefox":
                self.browser = webdriver.Firefox(service_log_path=log_path)
            else:
                self.browser = webdriver.Chrome(service_log_path=log_path,
                                                options=options)
        return self.browser


    def get_options(self, width=1200, height=800):
        '''return options for headless, no-sandbox, and custom width/height
        '''
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        options.add_argument("no-sandbox")
        options.add_argument("window-size=%sx%s" %(width, height))
        return options


    def get_page(self, url, name='Chrome'):
        '''get_page
            open a particular url, checking for Timeout
        '''
        if self.browser is None:
            self.browser = self.get_browser(name)

        try:
            return self.browser.get(url)
        except TimeoutException:
            print('Browser request timeout. Are you connected to the internet?')
            self.browser.close()
            sys.exit(1)


    def stop(self):
        '''close any running browser or server, and shut down the robot
        '''
        if self.browser is not None:
            self.browser.close()
        self.httpd.server_close() 

        if self.display is not None:
            self.display.close()


    def run_javascript(browser,code):
        if self.browser is not None:
            return browser.execute_script(code)
