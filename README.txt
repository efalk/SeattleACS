Note: git files can be found at https://github.com/efalk/SeattleACS/

Files for programming radios for Seattle Emergency Hub and ACS.

csv files are either for Chirp, or RT Systems software (Yaesu FT-60)

The RT Systems files might work on any RT Systems software. They has been
successfully tested with Explorer QRZ-1 and other radios. If you find a radio this
doesn't work with, feel free to contact me off line; I'll see what needs
to be changed.

W7ACS_ICS-217A_20230505.csv	Seattle ACS ics-217 frequency list
W7ACS_ICS-217A_20240131.csv	Seattle ACS ics-217 frequency list

ACS_VHF_UHF_RT.csv		ACS frequencies from W7ACS_ICS-217A_20240131.xlsx
ACS_VHF_UHF_chirp.csv		ACS frequencies from W7ACS_ICS-217A_20240131.xlsx
ACS_LOW_RT.csv			ACS frequencies from W7ACS_ICS-217A_20240131.xlsx
ACS_LOW_chirp.csv		ACS frequencies from W7ACS_ICS-217A_20240131.xlsx
ACS_220_RT.csv			ACS frequencies from W7ACS_ICS-217A_20240131.xlsx
ACS_220_chirp.csv		ACS frequencies from W7ACS_ICS-217A_20240131.xlsx
ACS_DATA_RT.csv			ACS frequencies from W7ACS_ICS-217A_20240131.xlsx
ACS_DATA_chirp.csv		ACS frequencies from W7ACS_ICS-217A_20240131.xlsx
Hub_RT.csv			GMRS frequencies and repeaters for emergency hubs
Hub_chirp.csv			GMRS frequencies and repeaters for emergency hubs
NOAA_RT.csv			NOAA weather frequencies
NOAA_chirp.csv			NOAA weather frequencies


Utility programs:

Acs2RtSys.py			Convert ACS 217 spreadsheet csv to RT systems
Acs2Chirp.py			Convert ACS 217 spreadsheet csv to Chirp
Chirp2RtSys.py			Convert Chirp csv to RT systems

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

My own preferred workflow is as follows:

• Download current radio settings into a tab within the software.
• Load the csv(s) into a second tab within the software.
• Copy-paste rows from the second tab into the tab for my radio.
• Upload back to the radio.

This process lets you store csv entries into whatever memories you like in the
radio, and lets you update the radio without losing other data. The "-s" option
is not needed if you do it this way.


If you would like to contribute, send changes to me at KK7NNS au gmail.com or
file a pull request on github.
