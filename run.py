from parsers.parsers import SURVEY_DATE
from parsers.Quinn.quinn_parser import QuinnParser
from parsers.Fox.fox_parser import FoxParser
from pathlib import Path
from constants import POLLSTERS
import requests
import requests
import os
import calendar
import numpy as np
import pandas as pd
import csv
import datetime


def main():
	date = input("Please enter the date of the survey MM/DD/YYYY: ")
	d_split = date.split("/")
	s_date = SURVEY_DATE(d_split[0], d_split[1], d_split[2])
	url = input("Please enter the url of the survey: ")
	poll = ""
	for pollster in POLLSTERS:
		if (url.find(pollster.value) != -1):
			confirm = input("This looks like a " + pollster.name + " poll. Is that correct? y/n: ")
			if confirm == "y":
				poll = pollster.name
				break

	if (poll == ""):
		poll = input("I wasn't able to determine the pollster from the URL. What poll is this? Your options are: " + str([i.name for i in POLLSTERS]))

	if poll == POLLSTERS.FOX.name:
		total_n = input("Please enter the total n: ")
		pages_to_skip = input("Please enter the number of pages to skip: ")
		parser = FoxParser(s_date, url, total_n)

	if poll == POLLSTERS.QUINN.name:
		total_n = input("Please enter the total n: ")
		pages_to_skip = input("Please enter the number of pages to skip: ")
		parser = QuinnParser(s_date, url, total_n)
	

	filename = Path(parser.saveAs + ".pdf")
	response = requests.get(url)
	filename.write_bytes(response.content)
	response = input("Please make sure you have a PDF saved in this directory called: " + parser.saveAs + ".pdf Once confirmed, press enter ")

	print("Running parser!")
	parser.run(int(pages_to_skip))
	print("Done! Your output is saved to this directory in a CSV file called: " + parser.saveAs + ".csv")

if __name__ == "__main__":
    main()