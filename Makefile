
# Edit this next line whenever a new ICS-217 is issued
#ICS217 = W7ACS_ICS-217A_20240131.csv
#ICS217 = W7ACS_ICS-217A_20250912.csv
#ICS217 = W7ACS_ICS-217A_20250916.csv
#ICS217 = W7ACS_ICS-217A_20250917-FINAL_REVIEW.csv
#ICS217 = W7ACS_ICS-217A_20250922_FINAL.csv
ICS217 = W7ACS_ICS-217A_WORKING.csv

CSV_FILES := ACS_VHF_UHF_RT.csv ACS_VHF_UHF_chirp.csv ACS_LOW_RT.csv ACS_LOW_chirp.csv \
	ACS_220_RT.csv ACS_220_chirp.csv ACS_DATA_RT.csv ACS_DATA_chirp.csv \
	ACS_HUB_RT.csv ACS_HUB_chirp.csv \
	ACS_UHF_NARROW_RT.csv ACS_UHF_NARROW_chirp.csv
#	ACS_VHF_UHF_ICOM.csv ACS_LOW_ICOM.csv \
#	ACS_220_ICOM.csv ACS_DATA_ICOM.csv \
#	ACS_HUB_ICOM.csv ACS_UHF_NARROW_ICOM.csv

all: ${CSV_FILES}

ACS_VHF_UHF_RT.csv: ${ICS217}
	./Tools/Acs2RtSys.py -b VU < ${ICS217} > $@

ACS_VHF_UHF_chirp.csv: ${ICS217}
	./Tools/Acs2Chirp.py -b VU < ${ICS217} > $@

ACS_UHF_NARROW_RT.csv: ${ICS217}
	./Tools/Acs2RtSys.py -R 'U..N' < ${ICS217} > $@

ACS_UHF_NARROW_chirp.csv: ${ICS217}
	./Tools/Acs2Chirp.py -R 'U..N' < ${ICS217} > $@

ACS_LOW_RT.csv: ${ICS217}
	./Tools/Acs2RtSys.py -b L < ${ICS217} > $@

ACS_LOW_chirp.csv: ${ICS217}
	./Tools/Acs2Chirp.py -b L < ${ICS217} > $@

ACS_220_RT.csv: ${ICS217}
	./Tools/Acs2RtSys.py -b T < ${ICS217} > $@

ACS_220_chirp.csv: ${ICS217}
	./Tools/Acs2Chirp.py -b T < ${ICS217} > $@

ACS_DATA_RT.csv: ${ICS217}
	./Tools/Acs2RtSys.py -b D < ${ICS217} > $@

ACS_DATA_chirp.csv: ${ICS217}
	./Tools/Acs2Chirp.py -b D < ${ICS217} > $@

ACS_HUB_RT.csv: ${ICS217}
	./Tools/Acs2RtSys.py -b H < ${ICS217} > $@

ACS_HUB_chirp.csv: ${ICS217}
	./Tools/Acs2Chirp.py -b H < ${ICS217} > $@

# ICOM
ACS_VHF_UHF_ICOM.csv: ${ICS217}
	./Tools/Acs2Icom.py -b VU < ${ICS217} > $@

ACS_UHF_NARROW_ICOM.csv: ${ICS217}
	./Tools/Acs2Icom.py -R 'U..N' < ${ICS217} > $@

ACS_LOW_ICOM.csv: ${ICS217}
	./Tools/Acs2Icom.py -b L < ${ICS217} > $@

ACS_220_ICOM.csv: ${ICS217}
	./Tools/Acs2Icom.py -b T < ${ICS217} > $@

ACS_DATA_ICOM.csv: ${ICS217}
	./Tools/Acs2Icom.py -b D < ${ICS217} > $@

ACS_HUB_ICOM.csv: ${ICS217}
	./Tools/Acs2Icom.py -b H < ${ICS217} > $@

%.html: %.md
	markdown.py < $< > $@



clean:
	rm -rf __pycache__
