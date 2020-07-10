class Parser(object):
    def __init__(self, name, date, url):
        self.name = name
        self.date = date
        self.url = url
        self.saveAs = name + str(date)
        # default values
        self.geography = "National"
        self.universe = "Registered Voters"
        self.mode = "Phone"

    def run():
        print("Parser not implemented!")

class SURVEY_DATE:
    def __init__(self, month, day, year): 
        self.year = year 
        self.month = month 
        self.day = day 
    def __str__(self):
    	return self.year + self.month + self.day