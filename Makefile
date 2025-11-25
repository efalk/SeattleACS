
# Edit this next line whenever a new ICS-217 is issued
#ICS217 = W7ACS_ICS-217A_20240131.csv
#ICS217 = W7ACS_ICS-217A_20250912.csv
#ICS217 = W7ACS_ICS-217A_20250916.csv
#ICS217 = W7ACS_ICS-217A_20250917-FINAL_REVIEW.csv
#ICS217 = W7ACS_ICS-217A_20250922_FINAL.csv
ICS217 = W7ACS_ICS-217A_WORKING.csv

DIRS := Chirp RT Icom

CHIRP_FILES := Chirp/2m.csv Chirp/70cm.csv Chirp/220.csv Chirp/6m.csv \
	Chirp/data.csv Chirp/narrow.csv Chirp/hub.csv
RT_FILES := RT/2m.csv RT/70cm.csv RT/220.csv RT/6m.csv RT/data.csv \
	RT/narrow.csv RT/hub.csv
ICOM_FILES := Icom/2m.csv Icom/70cm.csv Icom/6m.csv Icom/data.csv \
	Icom/hub.csv

CSV_FILES := ${CHIRP_FILES} ${RT_FILES} ${ICOM_FILES}

all: ${CSV_FILES}

# Chirp

Chirp/2m.csv: ${ICS217} | Chirp
	./Tools/Acs2Csv.py --Chirp -b V < ${ICS217} > $@

Chirp/70cm.csv: ${ICS217} | Chirp
	./Tools/Acs2Csv.py --Chirp -b U < ${ICS217} > $@

Chirp/220.csv: ${ICS217} | Chirp
	./Tools/Acs2Csv.py --Chirp -b T < ${ICS217} > $@

Chirp/narrow.csv: ${ICS217} | Chirp
	./Tools/Acs2Csv.py --Chirp -R 'U..N' < ${ICS217} > $@

Chirp/6m.csv: ${ICS217} | Chirp
	./Tools/Acs2Csv.py --Chirp -b L < ${ICS217} > $@

Chirp/data.csv: ${ICS217} | Chirp
	./Tools/Acs2Csv.py --Chirp -b D < ${ICS217} > $@

Chirp/hub.csv: ${ICS217} | Chirp
	./Tools/Acs2Csv.py --Chirp -b H < ${ICS217} > $@


# RT Systems

RT/2m.csv: ${ICS217} | RT
	./Tools/Acs2Csv.py --RtSys -b V < ${ICS217} > $@

RT/70cm.csv: ${ICS217} | RT
	./Tools/Acs2Csv.py --RtSys -b U < ${ICS217} > $@

RT/220.csv: ${ICS217} | RT
	./Tools/Acs2Csv.py --RtSys -b T < ${ICS217} > $@

RT/narrow.csv: ${ICS217} | RT
	./Tools/Acs2Csv.py --RtSys -R 'U..N' < ${ICS217} > $@

RT/6m.csv: ${ICS217} | RT
	./Tools/Acs2Csv.py --RtSys -b L < ${ICS217} > $@

RT/data.csv: ${ICS217} | RT
	./Tools/Acs2Csv.py --RtSys -b D < ${ICS217} > $@

RT/hub.csv: ${ICS217} | RT
	./Tools/Acs2Csv.py --RtSys -b H < ${ICS217} > $@


# ICOM

Icom/2m.csv: ${ICS217} | Icom
	./Tools/Acs2Csv.py --Icom -b V < ${ICS217} > $@

Icom/70cm.csv: ${ICS217} | Icom
	./Tools/Acs2Csv.py --Icom -b U < ${ICS217} > $@

Icom/6m.csv: ${ICS217} | Icom
	./Tools/Acs2Csv.py --Icom -b L < ${ICS217} > $@

Icom/data.csv: ${ICS217} | Icom
	./Tools/Acs2Csv.py --Icom -b D < ${ICS217} > $@

Icom/hub.csv: ${ICS217} | Icom
	./Tools/Acs2Csv.py --Icom -b H < ${ICS217} > $@


%.html: %.md
	markdown.py < $< > $@

${DIRS}:
	mkdir $@


clean:
	rm -rf __pycache__
