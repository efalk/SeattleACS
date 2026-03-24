<html><script type="text/javascript" src="toc.js"></script>

<div id="toc"></div>
</html>

# Code Plug O'Rama explained

This web page converts CSV files in one of several different formats into a format that
your radio can understand. More specifically, into files that CHIRP,
RT Systems, or Icom can understand.

There are several built-in databases you can use, or you can upload
your own in one of several [accepted formats](#accepted-formats).

This utility was written with the members of the
[Seattle Auxiliary Communications Service](https://www.seattleacs.org/) in
mind. If you're not a member of the ACS, most of the stuff here won't be of
any interest to you.

That said, let's get started.

## Using this tool

This tool has several built-in databases. You select one as a
a source, or optionally upload your own CSV file.

Optionally set a couple of filter options to select a subset
of the input, choose your output format and a few output options,
and hit 'Submit'. The tool generates a CSV file suitable for
the radio programming software of your choice, and Björn's your
uncle.

# The Form

## Select source

### Source

The drop-down list allows you to select one of the following
databases.

* ACS ICS 217 — The ICS 217 form used by ACS. This is a large
database with hundreds of entries in different bands and different
operating modes. If you're not in the ACS, you probably don't want
this one.
* ACS Winlink list — That subset of the ICS 217 specific to Winlink nodes.
* Repeater Roundabout — List of repeaters for the Repeater Roundabout event.
Updated every year.
* Seattle emergency hubs — Channel list used to program the GMRS radios
used by the Seattle Emergency Hub system.
* WWARA — Repeater list issued by the Western Washington Amateur Radio Association. Updated frequently.
* GMRS — List of GMRS frequencies.
* MURS — List of MURS (Multi-Use Radio Service) frequencies.
* Upload… — Allows you to upload your own CSV file and have it
translated to a form appropriate to your radio. See
[Accepted formats](#accepted-formats), below.

### Filter by band

For a large database, the ACS 217 in particular, there are channels
in several bands. Chances are, you're not interested in them all, so
this option allows you to limit the inputs.

* HF — Any channel in the HF band.
* 2m — VHF 2 meter band
* 1.25m — VHF 1.25 meter band
* 70cm — UHF
* GMRS — GMRS frequencies
* Digital — Channels marked as digital (ACS 217 only)

### Filter by mode

For a large database, the ACS 217 in particular, there are channels
using several different operating modes.
Chances are, you're not interested in them all, so
this option allows you to limit the inputs.

The names,
"FM", "AM", "LSB", "USB", "CW", "PKT", "P25", "DMR", "DSTAR", "NXDN",
"ATV", "DATV", and "Other digital",
should be self-explanatory.

## Output Options

### Format

One of:

* Chirp — Standard format used by CHIRP software.
* RT System — Format accepted by RT Systems software. Tested with
Yaesu FT-60 and several other radios, but not guaranteed to work
for all radios.
* Icom — Format accepted by Icom radio programming software.

### Start

The starting record number for the output. Normally you just
leave this as 1, but if you want to generate an output file that
starts at a specific record, you can change this.

### Long names

By default, the name field in the output
is the same as the name field in the input, which is usually short enough to
fit the display of most radios.

Some radios can display longer names, and so this flag adds some extra
information to the name where appropriate. Typically this means adding the
station call sign if not already part of the name. For e.g. ACS ICS 217 forms,
the channel number is added if not already present.

For example, When "Long names" is selected, then the tool would change
"`V01PSR`" to "`V01PSR WW7PSR`". The exact conversion depends on the
source database involved and the data found in the record.

### Sparse

By default, output records are written and numbered in the order
they're read from the input. The record numbers start at the Start
value given above and are strictly incrementing, ignoring the record
numbers in the input file.

Gaps in the input record numbers do not result in gaps in the
output. Suppose the input looks like this:

|Location|Name|Frequency|Duplex|Offset|Comment|
|1|H01WSEA|462.5500|+|5.000000|West Seattle|
|2|H02BHIL|462.5750|+|5.000000|Beacon Hill|
|3|H03CAPH|462.6000|+|5.000000|Capitol Hill|
|4|H04MAG|462.6250|+|5.000000|Magnolia|
|:||||||
|21|H21MAPL|462.6750|+|5.000000|Maple Leaf|
|22|H22ETIG|462.6250|+|5.000000|East Tiger|
|23|H23OLYM|462.6500|+|5.000000|Olympia|
|24|H24LKFP|462.7250|+|5.000000|Lake Forest Park|
|25|H25SNOH|462.7250|+|5.000000|Snohomish|

The output might look something like this:

|n|Receive Frequency|Transmit Frequency|Name|Comment|
|1|462.5500|467.5500|H01WSEA|West Seattle|
|2|462.5750|467.5750|H02BHIL|Beacon Hill|
|3|462.6000|467.6000|H03CAPH|Capitol Hill|
|4|462.6250|467.6250|H04MAG|Magnolia|
|5|462.6750|467.6750|H21MAPL|Maple Leaf|
|6|462.6250|467.6250|H22ETIG|East Tiger|
|7|462.6500|467.6500|H23OLYM|Olympia|
|8|462.7250|467.7250|H24LKFP|Lake Forest Park|
|9|462.7250|467.7250|H25SNOH|Snohomish|

With **Sparse** set, the output would be

|n|Receive Frequency|Transmit Frequency|Name|Comment|
|1|462.5500|467.5500|H01WSEA|West Seattle|
|2|462.5750|467.5750|H02BHIL|Beacon Hill|
|3|462.6000|467.6000|H03CAPH|Capitol Hill|
|4|462.6250|467.6250|H04MAG|Magnolia|
|21|462.6750|467.6750|H21MAPL|Maple Leaf|
|22|462.6250|467.6250|H22ETIG|East Tiger|
|23|462.6500|467.6500|H23OLYM|Olympia|
|24|462.7250|467.7250|H24LKFP|Lake Forest Park|
|25|462.7250|467.7250|H25SNOH|Snohomish|

----

# Accepted Formats

This tool recognizes several input formats, as identified by the CSV
header line. These are as follows:

Note that since this tool accepts and writes out Chirp and Rt Systems
formats, it can be used to translate back and forth.

## Chirp

CSV files exported from Chirp contain the following fields:

|Field name|Explanation|
|Location|Memory location, starting at 1|
|Name|	e.g. "PSRG"|
|Frequency|e.g. 146.960000|
|Duplex|	off, +, -, or <blank>|
|Offset|	e.g. 0.60000|
|Tone|	one of:|
||	  <blank>	no tone|
||	  **Tone** — Tone on TX using rToneFreq|
||	  **TSQL** — Tone on TX & RX using rToneFreq|
||	  **DTCS** — DTCS on TX & RX using DtcsCode|
||	  **TSQL-R** — Tone on RX using rToneFreq|
||	  **DTCS-R** — DTCS on RX using DtcsCode|
||	  **Cross** — see CrossMode|
||	  note: see https://chirp.danplanet.com/projects/chirp/wiki/DevelopersToneModes for cases where cToneFreq is used instead.|
|rToneFreq|e.g. 103.5, required, even if not used|
|cToneFreq|required, even if not used|
|DtcsCode|e.g. 023, required, even if not used|
|DtcsPolarity|e.g. NN|
|RxDtcsCode|e.g. 023, required, even if not used|
|CrossMode|covers more complex cases than **Tone** can describe. one of:|
||	  **Tone->Tone** — TX rToneFreq; RX cToneFreq|
||	  **Tone->DTCS** — TX rToneFreq; RX DtcsCode|
||	  **DTCS->Tone** — TX DtcsCode; RX rToneFreq|
||	  **DTCS->** — TX DtcsCode|
||	  **->DTCS** — RX DtcsCode|
||	  **->Tone** — RX rToneFreq|
||	  **DTCS->DTCS**|
|Mode|	WFM, FM, NFM, AM, NAM, DV, LSB, USB, CW, RTTY, DIG, PKT, NCW,NCWR, CWR, P25, Auto, RTTYR, FSK, FSKR, DMR, DN|
|TStep|	e.g. 5.00|
|Skip|	<blank>, S|
|Power|	e.g. 5.0W|
|Comment|	any text|
|URCALL|	?|
|RPT1CALL|?|
|RPT2CALL|?|
|DVCODE|	?|

The columns must be in this exact order and the header labels must match exactly.

## RT Systems

RT Systems provides different software for different radios, and so their
CSV files may vary somewhat. The scheme shown here was exported by the
software for the Yaesun FT-60 but has been successfully read by other
RT software and has a good chance of working on your radio.

|Field name|Explanation|
||memory: 1-1000; column header is blank|
|Receive Frequency|e.g. 146.96000|
|Transmit Frequency|e.g. 146.36000|
|Offset Frequency|600 kHz \| 5.00000 MHz \| (blank)|
|Offset Direction|Minus \| Plus \| Simplex|
|Operating Mode|FM \| AM|
|Name|e.g. PSRG|
|Show Name|Y|
|Tone Mode|None|
||Tone: Tone on TX|
||T Sql: Tone on RX (as well as TX?)|
||Rev CTCSS: RX squelch if tone *is* received|
||DCS: DCS code on TX|
||D Code|
||T DCS: CTCSS on TX, DCS on RX|
||D Tone: DCX on TX, CTCSS on RX|
|CTCSS|e.g. 103.5|
|DCS|e.g. 023|
|Skip|<blank> \| Scan|
|Step|e.g. "5 kHz"|
|Clock Shift|N|
|Tx Power|High \| Low|
|Tx Narrow|<blank> \| N|
|Pager Enable|N|
|Bank 1|e.g. N; *Bank columns are optional*|
|Bank 2|Y|
|Bank 3|N|
|Bank 4|N|
|Bank 5|N|
|Bank 6|N|
|Bank 7|N|
|Bank 8|N|
|Bank 9|N|
|Bank 10|N|
|Comment|any string|

The columns must be in this exact order and the header labels must match exactly.
The **Bank** columns are optional, but must either all be present or all be omitted.

## ARRL

This is the format used by ARRL to publish repeater lists. The built-in "WWARA"
database is in this format. See https://www.wwara.org/coordinations/coordination-data-files/
for more information.

In a nutshell, the format accepted by this tool is:

|Field name|Explanation|
|FC_RECORD_ID|ignored|
|SOURCE|ignored|
|OUTPUT_FREQ|e.g. 29.6800|
|INPUT_FREQ|e.g. 29.5800|
|STATE|e.g. WA|
|CITY|e.g. Lookout Mtn|
|LOCALE|e.g. WASHINGTON- NORTHWEST|
|CALL|call sign, e.g. W7RNB|
|SPONSOR|e.g. 5CountyEmCommGrp|
|CTCSS_IN|e.g. 110.9 (or blank)|
|CTCSS_OUT|e.g. 110.9 (or blank)|
|DCS_CDCSS|e.g. 023 (or blank)|
|DTMF|ignored|
|LINK|link access, e.g. E+echolink#|
|FM_WIDE|Y: repeater can handle wide|
|FM_NARROW|Y: repeater can handle narrow; (some repeaters can do both)|
|DSTAR_DV|Y: dstar capable|
|DSTAR_DD|Y: dstar capable|
|DMR|Y: dmr capable|
|DMR_COLOR_CODE|used with DMR|
|FUSION|N|
|FUSION_DSQ|used with fusion|
|P25_PHASE_1|N P25 capable|
|P25_PHASE_2|N P25 capable|
|P25_NAC|NAC code for P25|
|NXDN_DIGITAL|Y: digital only|
|NXDN_MIXED|Y: mixed mode|
|NXDN_RAN|radio access number|
|ATV|Y: amateur television (analog)|
|DATV|Y: amateur television (digital)|
|RACES|N|
|ARES|N|
|WX|N|
|URL|Internet URL for this station|
|LATITUDE|e.g. 48.6875|
|LONGITUDE|e.g. -122.3625|
|EXPIRATION_DATE|e.g. 2026-02-28|
|COMMENT|any text|

The columns must be in this exact order and the header labels must match exactly.

Some repeaters are capable of more than one operating mode. For example, K7TGU in
Washington handles both narrow FM and P25 protocols. In cases like this, one input
record can result in multiple output records.

Additional information such as the dmr color code or nxdn radio access number will
be put into the comment field of the output.

## Generic

If you want to write your own code plug and have it translated to other
formats, and you're looking for something very simple, then this format is
also accepted.

|Field name|Explanation|
|group|Radio group number if used;  usually blank|
|CH#|Channel (memory) number|
|txfreq|Transmit frequency or blank for simplex|
|rxfreq|Receive frequency|
|offset|Offset in MHz. E.g. -0.600|
|name|Display name|
|comment|Any text|
|txtone|CTCSS tone for transmit, "D<i>nnn</i>" for DCS, or blank|
|rxtone|CTCSS tone for receive, "D<i>nnn</i>" for DCS, or blank|
|mode|FM, AM, DV, LSB, USB, CW, RTTY, DIG, PKT, NCW,NCWR, CWR, P25, Auto, RTTYR, FSK, FSKR, DMR, DN, DIG, etc.|
|wide|Y \| N (for FM and AM)|
|power|e.g. 5.0W. "high" and "low" also accepted.|

The columns must be in this exact order and the header labels must match exactly.

For simplex, only the "rxfreq" column need be specified; "txfreq" and "offset"
may be left blank. For a repeater, any two of "rxfreq", "txfreq", and "offset"
will suffice; choose whatever is more convenient for you. "offset" is the value
added to "rxfreq" to determine "txfreq".

While this tool accepts any value for the mode, there is no guarantee that the
programming software will accept it. In a few cases this tool will translate an
unsupported mode.  E.g. for Chirp output, "DSTAR" and changed to "DIG".

If you encounter problems, you'll need to change the mode in your input file to
something the software will accept. Contact KK7NNS au gmail.com if you think of
a change that's worth making here.

## ACS

Format is specific to the Seattle ACS. Contact KK7NNS au gmail.com if you need more
information.

<html><script language="Javascript">
<!--
genToc(1);
// -->
</script></html>

