from enum import Enum
from parsers.parsers import Parser
from constants import GROUPS
from constants import CSV_COLUMNS
from pdf_utils import pdf_to_text
import requests
import os
import calendar
import numpy as np
import pandas as pd
import csv
import datetime

class FoxParser(Parser):
	def __init__(self, date, url, total_n):
		Parser.__init__(self, "Fox", date, url)
		self.geography = "National"
		self.universe = "Registered Voters"
		self.mode = "Phone"
		self.total_n = total_n
		class Question(Enum):
			TRUMPJOB = "Do you approve or disapprove of the job Donald Trump is doing as president? [IF APPROVE"
			BIDEN_FAV = "Joe Biden: Please tell"
			TRUMP_FAV = "Donald Trump: Please tell"
			VOTE_2020 = "how would you vote if the candidates were: "
		self.PUNCHES_TO_QUESTION_MAPPING = [( ['Trump_StrApp', "Trump_App", "Trump_Disapproval", "Trump_StrDisapp", 'DK-NO_RECORD'], Question.TRUMPJOB ),
                               ( ['DK-NO_RECORD', 'DK-NO_RECORD', 'DK-NO_RECORD', 'DK-NO_RECORD', "BIDEN_THERM_Neut", 'DK-NO_RECORD', 'BIDEN_THERM_Warm', "BIDEN_THERM_Cool"], Question.BIDEN_FAV ),
                             ( ['DK-NO_RECORD', 'DK-NO_RECORD', 'DK-NO_RECORD', 'DK-NO_RECORD', "TRUMP_THERM_Neut", 'DK-NO_RECORD', 'TRUMP_THERM_Warm', "TRUMP_THERM_Cool"], Question.TRUMP_FAV ),
                              ( ['Pres20BT_Biden', "Pres20BT_Trump", "DKNA_Pres20BT", 'DK-NO_RECORD', 'DK-NO_RECORD'], Question.VOTE_2020 )] 

		self.GROUP_TO_SPLIT_DICT = {
		    GROUPS.ALL : 'Total',
		    GROUPS.MEN :  'Men',
		    GROUPS.WOMEN : 'Women',
		   	GROUPS.HISP : 'anic',
		    GROUPS.BLACK : 'Black',
		    GROUPS.WHITE : 'White',
		    GROUPS.IND : 'Ind',
		    GROUPS.REP : 'GOP',
		    GROUPS.DEM : 'Dem'
		}
		self.question_break = "Non"

	def get_numbers(self, split_section):
	    nums = [i.strip() for i in split_section.split(" ")]
	    good = []
	    for min_list in nums:
	        # crosstabs so when its x by x its denoted with - we will keep it so all
	        # number lists are the same length and we can index uniformally
	        if (len(min_list) >= 1):
	            if ((min_list[-1] == "%") or (min_list == '-')):
	                good.append(min_list.replace("%", ""))
	    return good

	def find_next_section(self, text, seperator, n):
		start = text.find(seperator)
		while start >= 0 and n > 1:
			start = text.find(seperator, start+len(seperator))
			n -= 1
		return start

	def run(self, number_of_pages_to_skip):
		# get PDF text
		path = os.getcwd() + "/" + self.saveAs + ".pdf"
		original_text = pdf_to_text(path, number_of_pages_to_skip)
		decoded_text = original_text.decode("utf-8")

		# OPEN CSV AND WRITE HEADER DEFINE CONSTANTS
		csv_file = self.saveAs + ".csv"

		f = open(csv_file, "w")
		writer = csv.DictWriter(f,fieldnames=[i.value for i in list(CSV_COLUMNS)])
		writer.writeheader()

		today = datetime.date.today()
		DATE_ADDED = today.strftime("%m/%d/%y")
		POLLSTER = self.name
		s_date = self.date
		S_DATE = datetime.datetime(int(s_date.year), int(s_date.month), int(s_date.day)).strftime("%m/%d/%y")
		GEOGRAPHY = self.geography
		UNIVERSE = self.universe
		MODE = self.mode
		URL = self.url
		for questions in self.PUNCHES_TO_QUESTION_MAPPING:
			question_to_look_for = questions[1].value
			first_index = decoded_text.find(str(question_to_look_for))
			second_index = self.find_next_section(decoded_text[first_index:], self.question_break, 4)
			passage = decoded_text[first_index:first_index+second_index]
			if not passage:
				if question_to_look_for == "Joe Biden: Please tell":
					question_to_look_for == "Joe Biden - Please tell me"
				if question_to_look_for == "Donald Trump: Please tell":
					question_to_look_for == "Donald Trump - Please tell me"
				first_index = decoded_text.find(str(question_to_look_for))
				second_index = self.find_next_section(decoded_text[first_index:], self.question_break, 4)
				passage = decoded_text[first_index:first_index+second_index]
			split = passage.split("\n")
			percentages = []
			for s in split:
				percentages.append(self.get_numbers(s))
		    # get rid of blanks or one offs
			percentages = [i for i in percentages if len(i) > 1]
			# only keep %
			percentages = [j for j in percentages if len(j[0]) <= 3]
			columns = []
			# Consistent across all questions as it is based off the number of groups 
			sections = 2
			# eg right track, wrong track, ns
			num_columns = len(questions[0])
			# creates list of lists [[righttrack%s], [wrongtrack%s], [ns]]
			for j in range(0, len(questions[0])):
				col = []
				for i in range(0, sections):
					col = col + (percentages[j + (i * len(questions[0]))])
				columns.append(col)

			dems = " ".join([i.strip() for i in passage.split("\n") if (i.strip().startswith("Total"))]).split(" ")
			dems = [j for j in dems if len(j) > 0 and j != "Age"]

			# loop through columns aka RightTrack
			for i in range(len(questions[0])):
				# loops dictionary of groups which will tell you which index to use to get the correct %
				for group in self.GROUP_TO_SPLIT_DICT:
					fox_dem = self.GROUP_TO_SPLIT_DICT[group]
					index = dems.index(fox_dem)

					num = columns[i][index]
					if not num.isdigit():
					    num = 0

					n = self.total_n  if group.value == 'all sample' else 0
					# columsn are organized str app, app, diss, str diss
					# app is str + app so column + column - 1
					# dissapp is str + diss so column + column + 1
					if ( questions[0][i].endswith("_App") ):
						add = columns[i - 1][index]
						if not add.isdigit():
							add = 0
						num = int(num) + int(add)
					if ( questions[0][i].endswith("_Disapproval") or questions[0][i].endswith("_Neut") ):
						add = columns[i + 1][index]
						if not add.isdigit():
							add = 0
						num = int(num) + int(add)

					if ( questions[0][i].startswith("DKNA_") ):
						for k in range(1,3):
							add = columns[i + k][index]
							if not add.isdigit():
								add = 0
							num = int(num) + int(add)

					        

					estimate = "." + f'{int(num):02}'
		            
		            
					# We don't actaully record dks for trump approval 
					if ( questions[0][i] == "DK-NO_RECORD" ): 
						continue
					else:
						writer.writerow({
							'date_added' : DATE_ADDED,
							'pollster' : POLLSTER,
							"date": S_DATE,
							'geography': GEOGRAPHY,
							"universe": UNIVERSE,
							"mode":MODE,
							"depvar": questions[0][i],
							"groupname":group.value,
							"estimate": estimate,
							"n":n,
							"url":URL
						})
		f.close()
