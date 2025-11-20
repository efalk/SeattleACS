Note: these files can be found at https://github.com/efalk/SeattleACS/

Instructions for CHIRP: https://github.com/efalk/SeattleACS/blob/main/Chirp/README.md
Instructions for RT: https://github.com/efalk/SeattleACS/blob/main/RT/README.md

Short instructional videos:
  Chirp:      https://www.youtube.com/watch?v=ehvOrtVYogs
  RT Systems: https://www.youtube.com/watch?v=n52Fra0JfIA


Files for programming radios for Seattle Emergency Hub and ACS.

csv files are either for Chirp, RT Systems software, or Icom (tested with IC-705)

The RT Systems files might work on any RT Systems software. They
has been successfully tested with Yaesu FT-60, FTM-7250, Explorer
QRZ-1 and other radios. If you find a radio this doesn't work with,
feel free to contact me off line; I'll see what needs to be changed.

W7ACS_ICS-217A_20230505.csv     Seattle ACS ics-217 frequency list
W7ACS_ICS-217A_20240131.csv     Seattle ACS ics-217 frequency list

Chirp/		Programming files for Chirp
RT/			Programming files for RT Systems
Icom/		Programming files for Icom

Each subdirectory contains some or all of the following:

2m.csv          ACS frequencies, 2m band
220.csv         ACS frequencies, 1.25m band
70cm.csv        ACS frequencies, 70cm band
6m.csv          ACS frequencies, 6m band
data.csv        ACS frequencies, data
narrow.csv      upcoming narrow band frequencies
noaa.csv        NOAA weather frequencies
hub.csv         Seattle emergency hub GMRS frequencies
Hub_GMRS.csv    Same, for GMRS radios.

Utilities:

Tools/		Various programs to convert ICS217 spreadsheet to code plugs


My own preferred workflow is as follows:

• Download current radio settings into a tab within the software.
• Load the csv(s) into a second tab within the software.
• Copy-paste rows from the second tab into the tab for my radio.
• Upload back to the radio.

This process lets you store csv entries into whatever memories you like in the
radio, and lets you update the radio without losing other data. The "-s" option
is not needed if you do it this way.

See the README files in the Chirp/ and RT/ subdirectories for more detailed instructions.


If you would like to contribute, send changes to me at KK7NNS au gmail.com or
file a pull request on github.
