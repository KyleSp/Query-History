#Kyle Spurlock

import webbrowser
import time
import os

#constants
FILE_OUT_NAME = "q-history.txt"
GOOGLE_URL = "https://www.google.com/search?q="
YOUTUBE_URL = "https://www.youtube.com/results?search_query="
STACK_OVERFLOW_SITE = "stackoverflow.com"
REDDIT_SITE = "reddit.com"
POSSIBLE_ARGUMENTS = ["q", "s", "t", "d", "y", "r", "h", "v", "g"]

#TODO: add amazon (a) and ebay (e) and craigslist (c) and bing (b)
#TODO: handle special characters (such as +)
#TODO: make argument definitions be read in from a file for easy customization (must include one for "quit")
#TODO: be able to search with multiple search engines at the same time

class Query:
	def __init__(self, search):
		self.search = search
		self.noArgsSearch = ""
		self.formatSearch = ""
		self.url = ""
		
		self.args = []
		
		self.skip = False
		self.quit = False
		self.addToHistory = True
		self.deleteHistory = False
		self.viewHistory = False
	
	#get arguments and separate them from query
	def getArguments(self):
		words = self.search.split()
		for word in words:
			if len(word) == 2 and word[0] == '-':
				self.args.append(word[1])
			else:
				if self.noArgsSearch != "":
					self.noArgsSearch += " "
				self.noArgsSearch += word
		self.noArgsSearch = " " + self.noArgsSearch
	
	#either perform specific command, or create url for query
	def processArguments(self):
		for arg in self.args:
			if not arg in POSSIBLE_ARGUMENTS:
				print("ERROR:", "\"" + arg + "\"", "not found in arguments list")
				self.skip = True
		
		#misc. arguments
		if "q" in self.args:
			self.quit = True
			return
		
		if "t" in self.args:
			self.addToHistory = False
		
		if "d" in self.args:
			self.addToHistory = False
			self.deleteHistory = True
		
		if "h" in self.args:
			self.skip = True
			print("list of arguments:", POSSIBLE_ARGUMENTS)
		
		if "v" in self.args:
			self.skip = True
			self.viewHistory = True
		
		#browser selection and format search
		if "y" in self.args:
			self.url += YOUTUBE_URL
			self.formatSearch = self.convertToURL("y")
		else:
			#do this by default (g)
			self.url += GOOGLE_URL
			self.formatSearch = self.convertToURL("g")
			
			#site selection
			if "s" in self.args:
				self.url += "site:" + STACK_OVERFLOW_SITE
			elif "r" in self.args:
				self.url += "site:" + REDDIT_SITE
		
		self.url += self.formatSearch
	
	#convert query into a usable url based on the browser selection
	def convertToURL(self, arg):
		if arg == "g" or arg == "y":
			return self.noArgsSearch.replace(" ", "+")


fileOut = open(FILE_OUT_NAME, "a+")

while True:
	q = Query(input("Query: "))
	
	q.getArguments()
	q.processArguments()
	
	#display history (v)
	if q.viewHistory:
		fileOut.close()
		fileOut = open(FILE_OUT_NAME, "r")
		for line in fileOut:
			print(line)
		fileOut.close()
		fileOut = open(FILE_OUT_NAME, "a+")
	
	if q.quit:
		#quit program
		break
	elif q.skip:
		#skip to next prompt
		continue
	
	#open new browser/tab with query's url
	webbrowser.open_new(q.url)
	
	#delete history (d)
	if q.deleteHistory:
		fileOut.close()
		os.remove(FILE_OUT_NAME)
		fileOut = open(FILE_OUT_NAME, "a+")
	
	#add to history (disabled with t or d)
	if q.addToHistory:
		timestamp = time.strftime("%d/%m/%Y, %H:%M:%S")
		
		outputStr = timestamp + " -"
		if len(q.args) == 0:
			outputStr += " "
		outputStr += q.noArgsSearch
		outputStr += "" + "\n"
		fileOut.write(outputStr)
		

fileOut.close()
