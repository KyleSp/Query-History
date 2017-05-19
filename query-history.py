#Kyle Spurlock

import webbrowser
import time
import os

#constants
DIRECTORY = "C:\\Users\\kspurloc\\AppData\Local\\Programs\\Python\\Python36-32\\Python Programs\\"
FILE_OUT_NAME = DIRECTORY + "q-history.txt"
FILE_ARG_NAME = DIRECTORY + "q-history-args.txt"

GOOGLE_URL = "https://www.google.com/search?q="
YOUTUBE_URL = "https://www.youtube.com/results?search_query="
BING_URL = "https://www.bing.com/search?q="
AMAZON_URL = "https://www.amazon.com/s/field-keywords="
WOLFRAM_URL = "https://www.wolframalpha.com/input/?i="
SEARCH_ENGINE_DEFS = {
	"[search_youtube]": YOUTUBE_URL,
	"[search_bing]": BING_URL,
	"[search_amazon]": AMAZON_URL,
	"[search_google]": GOOGLE_URL,
	"[search_wolfram]": WOLFRAM_URL
	}

STACK_OVERFLOW_SITE = "stackoverflow.com"
REDDIT_SITE = "reddit.com"

#TODO: handle special characters (other ones besides + or ')
#TODO: do something with the history (keep track of frequency of something)
#TODO: make error checking tests
#TODO: deal with conflicting commands (either one has more precidence or it is an error)

def parseArgumentFile(fileName):
	inFile = open(fileName, "r")
	argDefs = {}
	
	for line in inFile:
		words = line.split()
		if len(words) == 3:
			argDefs[words[0]] = words[2]
	
	inFile.close()
	return argDefs

def saveArgumentFile(argDefs, fileName):
	if fileName == "query-history.py" or fileName == FILE_OUT_NAME or fileName == FILE_ARG_NAME:
		return
	
	inFile = open(fileName, "w")
	
	for arg in argDefs:
		inFile.write(arg + " = " + argDefs[arg] + "\n")
	
	inFile.close()

class Query:
	def __init__(self, search, argDefs):
		self.search = search
		self.noArgsSearch = ""
		self.urls = []
		
		self.argDefs = argDefs
		self.args = []
		
		self.skip = False
		self.quit = False
		self.addToHistory = True
		self.deleteHistory = False
		self.viewHistory = False
		self.loadArgs = False
	
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
	
	#either perform specific command, or create urls for query
	def processArguments(self):
		#check for invalid arguments
		for arg in self.args:
			if not arg in self.argDefs.values():
				print("ERROR:", "\"" + arg + "\"", "not found in arguments list")
				self.skip = True
		
		#misc. arguments
		#quit
		if self.argDefs["[quit]"] in self.args:
			self.quit = True
			return
		
		#save argument definitions to file
		if self.argDefs["[save_args]"] in self.args:
			self.skip = True
			words = self.noArgsSearch.split()
			if len(words) == 1:
				saveArgumentFile(self.argDefs, DIRECTORY + words[0])
		
		#load argument definitions from file
		if self.argDefs["[load_args]"] in self.args:
			self.skip = True
			self.loadArgs = True
			words = self.noArgsSearch.split()
			if len(words) == 1:
				self.argDefs = parseArgumentFile(DIRECTORY + words[0])
				print("site_reddit is:", self.argDefs["[site_reddit]"])
		
		#replace argument definition with new value
		if self.argDefs["[replace_arg]"] in self.args:
			self.skip = True
			words = self.noArgsSearch.split()
			if len(words) == 2:
				words[0] = "[" + words[0] + "]"
				print("changed", words[0], "to", words[1])
				self.argDefs[words[0]] = words[1]
		
		#don't add to history
		if self.argDefs["[no_add_to_history]"] in self.args:
			self.addToHistory = False
		
		#delete history
		if self.argDefs["[delete_history]"] in self.args:
			self.addToHistory = False
			self.deleteHistory = True
			self.skip = True
		
		#get help
		if self.argDefs["[help]"] in self.args:
			self.skip = True
			print("List of Arguments:")
			for arg in self.argDefs:
				print(arg + ": " + self.argDefs[arg])
		
		#view history
		if self.argDefs["[view_history]"] in self.args:
			self.skip = True
			self.viewHistory = True
		
		#search engine selection and format search
		match = False
		defaultEngine = ""
		for searchEngine in SEARCH_ENGINE_DEFS:
			if self.argDefs[searchEngine] == self.argDefs["[default_search]"]:
				defaultEngine = searchEngine
			
			if self.argDefs[searchEngine] in self.args:
				match = True
				url = SEARCH_ENGINE_DEFS[searchEngine]
				
				if searchEngine == "[search_google]":
					#site selection
					if self.argDefs["[site_stack_overflow]"] in self.args:
						#select stack overflow for site
						url += "site: " + STACK_OVERFLOW_SITE + "+"
					elif self.argDefs["[site_reddit]"] in self.args:
						#select reddit for site
						url += "site: " + REDDIT_SITE + "+"
				
				url += self.convertToURL(self.argDefs[searchEngine])
				self.urls.append(url)
		
		#use default search engine if none specified
		if not match:
			if defaultEngine == "[search_google]":
				#site selection
				url = SEARCH_ENGINE_DEFS[defaultEngine]
				if self.argDefs["[site_stack_overflow]"] in self.args:
					#select stack overflow for site
					url += "site:" + STACK_OVERFLOW_SITE + "+"
					url += self.convertToURL(self.argDefs[defaultEngine])
					self.urls.append(url)
					return
				if self.argDefs["[site_reddit]"] in self.args:
					#select reddit for site
					url = SEARCH_ENGINE_DEFS[defaultEngine]
					url += "site:" + REDDIT_SITE + "+"
					url += self.convertToURL(self.argDefs[defaultEngine])
					self.urls.append(url)
					return
				url = SEARCH_ENGINE_DEFS[defaultEngine]
				url += self.convertToURL(self.argDefs[defaultEngine])
				self.urls.append(url)
	
	#convert query into a usable url based on the browser selection
	def convertToURL(self, arg):
		if (arg == self.argDefs["[search_google]"] or arg == self.argDefs["[search_youtube]"]
		or arg == self.argDefs["[search_bing]"] or arg == self.argDefs["[search_amazon]"] or arg == self.argDefs["[search_wolfram]"]):
			s = self.noArgsSearch.replace("+", "%2B")
			s = s.replace("'", "%27")
			s = s.replace(" ", "+")
			return s
	
	def openTabs(self):
		for url in self.urls:
			webbrowser.open_new(url)
	
	def getArgDefs(self):
		return self.argDefs


argDefs = parseArgumentFile(FILE_ARG_NAME)
fileOut = open(FILE_OUT_NAME, "a+")

while True:
	#prompt user for input
	q = Query(input("Query: "), argDefs)
	
	q.getArguments()
	q.processArguments()
	
	#load arguments from file (o)
	if q.loadArgs:
		argDefs = q.getArgDefs()
	
	#display history (v)
	if q.viewHistory:
		fileOut.close()
		fileOut = open(FILE_OUT_NAME, "r")
		for line in fileOut:
			print(line)
		fileOut.close()
		fileOut = open(FILE_OUT_NAME, "a+")
	
	#delete history (d)
	if q.deleteHistory:
		fileOut.close()
		os.remove(FILE_OUT_NAME)
		fileOut = open(FILE_OUT_NAME, "a+")
	
	if q.quit:
		#quit program
		break
	elif q.skip:
		#skip to next prompt
		continue
	
	#open new browser/tab with query's url
	q.openTabs()
	
	#add to history (disabled with t or d)
	if q.addToHistory:
		timestamp = time.strftime("%m/%d/%Y, %H:%M:%S")
		
		outputStr = timestamp + " - "
		outputStr += q.noArgsSearch
		outputStr += "" + "\n"
		fileOut.write(outputStr)
	
	#update argDefs
	argDefs = q.getArgDefs()

fileOut.close()
