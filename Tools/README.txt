
Acs2RtSys.py			Convert ACS 217 spreadsheet csv to RT systems
Acs2Chirp.py			Convert ACS 217 spreadsheet csv to Chirp
Chirp2RtSys.py			Convert Chirp csv to RT systems
ics217.py			Class that reads ACS 217 spreadsheet csv
common.py			Common code for converters


The Acs2*.py programs read a W7ACS_ICS-217 csv file and write out a csv file
compatible with RT Systems or Chirp, respectively. By default, only the "V" and "U"
entries are used, but this can be changed with the -b option.

Options are:

	-b _bands_	Any combination of letters from VULTD, default is VU
			Run "Acs2Chirp --help" for the full list.

	-s _n_		Start output line numbering at _n_, default is 1


By default, the included Makefile will generate csv files for Vhf+Uhf, 220 MHz, Low,
and Data. All csv files start numbering lines from 1. If you want the line numbering
to start elsewhere, run the programs manually with the "-s _n_" value of your choice.

