
# Edit this next line whenever a new ICS-217 is issues
ICS217 = W7ACS_ICS-217A_20240131.csv

CSV_FILES := ACS_VHF_UHF_RT.csv ACS_VHF_UHF_chirp.csv ACS_LOW_RT.csv ACS_LOW_chirp.csv \
	ACS_220_RT.csv ACS_220_chirp.csv ACS_DATA_RT.csv ACS_DATA_chirp.csv

all: ${CSV_FILES}

ACS_VHF_UHF_RT.csv: ${ICS217}
	./Acs2RtSys.py -b VU < ${ICS217} > $@

ACS_VHF_UHF_chirp.csv: ${ICS217}
	./Acs2Chirp.py -b VU < ${ICS217} > $@

ACS_LOW_RT.csv: ${ICS217}
	./Acs2RtSys.py -b L < ${ICS217} > $@

ACS_LOW_chirp.csv: ${ICS217}
	./Acs2Chirp.py -b L < ${ICS217} > $@

ACS_220_RT.csv: ${ICS217}
	./Acs2RtSys.py -b T < ${ICS217} > $@

ACS_220_chirp.csv: ${ICS217}
	./Acs2Chirp.py -b T < ${ICS217} > $@

ACS_DATA_RT.csv: ${ICS217}
	./Acs2RtSys.py -b D < ${ICS217} > $@

ACS_DATA_chirp.csv: ${ICS217}
	./Acs2Chirp.py -b D < ${ICS217} > $@

clean:
	rm -rf __pycache__
