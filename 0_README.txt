Files for programming radios for Seattle Emergency Hub and ACS.

csv files are either for Chirp, or RT Systems software (Yaesu FT-60)

The RT Systems files might work on any RT Systems software; not tested

W7ACS_ICS-217A_20230505.csv	Seattle ACS ics-217 frequency list
W7ACS_ICS-217A_20240131.csv	Seattle ACS ics-217 frequency list

ACS_LOW_RT.csv			ACS frequencies from W7ACS_ICS-217A_20240131.xlsx
ACS_LOW_chirp.csv		ACS frequencies from W7ACS_ICS-217A_20240131.xlsx
ACS_VHF_UHF_RT.csv		ACS frequencies from W7ACS_ICS-217A_20240131.xlsx
ACS_VHF_UHF_chirp.csv		ACS frequencies from W7ACS_ICS-217A_20240131.xlsx
Hub_RT.csv			GMRS frequencies and repeaters for emergency hubs
Hub_chirp.csv			GMRS frequencies and repeaters for emergency hubs

BTECH_GMRS-V2_20230831.img	Memory dump from BTECH GMRS-V2 (chirp)
Baofeng_UV-9R Pro_20230903.img	Memory dump from Baofeng UV-9R
Explorer_QRZ-1_20230831.img	Memory dump from Explorer QRZ-1
GMRS V2 Program.csv
US Calling Frequencies.csv	List of 9 common frequencies, schema unknown
rtsystems.csv			sample file from RT systems
rtsystems_schema		notes on RT systems csv format
chirp_schema.txt		notes on CHIRP csv format

Utility programs:

Acs2RtSys.py			Convert ACS 217 spreadsheet csv to RT systems
Acs2Chirp.py			Convert ACS 217 spreadsheet csv to Chirp
Chirp2RtSys.py			Convert Chirp csv to RT systems
