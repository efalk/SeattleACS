Note: git files can be found at https://github.com/efalk/SeattleACS/

Instructions for CHIRP: https://github.com/efalk/SeattleACS/blob/main/chirp.md
Instructions for RT: https://github.com/efalk/SeattleACS/blob/main/rt.md


Files for programming radios for Seattle Emergency Hub and ACS.

csv files are either for Chirp, or RT Systems software (Yaesu FT-60)

The RT Systems files might work on any RT Systems software. They has been
successfully tested with Explorer QRZ-1 and other radios. If you find a radio this
doesn't work with, feel free to contact me off line; I'll see what needs
to be changed.

W7ACS_ICS-217A_20230505.csv     Seattle ACS ics-217 frequency list
W7ACS_ICS-217A_20240131.csv     Seattle ACS ics-217 frequency list

ACS_VHF_UHF_RT.csv              ACS frequencies from W7ACS_ICS-217A_20250922_FINAL.xlsx
ACS_VHF_UHF_chirp.csv           ACS frequencies from W7ACS_ICS-217A_20250922_FINAL.xlsx
ACS_LOW_RT.csv                  ACS frequencies from W7ACS_ICS-217A_20250922_FINAL.xlsx
ACS_LOW_chirp.csv               ACS frequencies from W7ACS_ICS-217A_20250922_FINAL.xlsx
ACS_220_RT.csv                  ACS frequencies from W7ACS_ICS-217A_20250922_FINAL.xlsx
ACS_220_chirp.csv               ACS frequencies from W7ACS_ICS-217A_20250922_FINAL.xlsx
ACS_DATA_RT.csv                 ACS frequencies from W7ACS_ICS-217A_20250922_FINAL.xlsx
ACS_DATA_chirp.csv              ACS frequencies from W7ACS_ICS-217A_20250922_FINAL.xlsx
ACS_UHF_NARROW_RT.csv           New ACS frequencies for UHF narrow band
ACS_UHF_NARROW_chirp.csv        New ACS frequencies for UHF narrow band
ACS_HUB_RT.csv                  Seattle emergency hub frequencies
ACS_HUB_chirp.csv               Seattle emergency hub frequencies
Hub_RT.csv                      GMRS frequencies and repeaters for emergency hubs
Hub_chirp.csv                   GMRS frequencies and repeaters for emergency hubs
Hub_GMRS_chirp.csv              Same, for GMRS radios.
NOAA_RT.csv                     NOAA weather frequencies
NOAA_chirp.csv                  NOAA weather frequencies

Tools				Various programs to convert ICS217 spreadsheet to code plugs


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
