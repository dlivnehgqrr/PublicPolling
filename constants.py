from enum import Enum

class CSV_COLUMNS(Enum):
    DATE_ADDED = "date_added"
    POLLSTER = "pollster"
    DATE = "date"
    GEOGRAPHY = "geography"
    UNIVERSE = "universe"
    MODE = "mode" 
    DEPVAR = "depvar"
    GROUPNAME = "groupname"
    ESTIMATE = "estimate"
    N = "n"
    URL = "url"


class GROUPS(Enum):
	ALL = 'all sample'
	MEN = 'Men'
	WOMEN = 'Women'
	HISP = 'Hispanic'
	BLACK = 'Black'
	WHITE = 'White'
	IND = 'Ind_Id'
	REP = 'Rep_Id'
	DEM = 'Dem_Id'


class POLLSTERS(Enum):
	FOX = "foxnews"
	QUINN = "poll.qu.edu"
