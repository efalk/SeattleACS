
# Generate code plugs for your radio

This page allows you to select from one of several sources or to
upload your own. It can generate CSV files for Chirp, RT Systems
(tested with Yaesu FT-60 and several other radios), or Icom.

You can filter the input based on various criteria and slightly
customize the output.

<html><p>Click <a href="help.html" target="CodePlugHelp">here for detailed instructions</a></p></html>

<html>
<form action="/cgi-bin/generate.cgi" method=POST enctype="multipart/form-data" name="mainForm">
<h2>Select source:</h2>
<p>Source: <select name=source onchange="inputSelection()">
<option>ACS ICS 217</option>
<option>ACS Winlink list</option>
<option>Repeater Roundabout</option>
<option>Seattle emergency hubs</option>
<option>WWARA</option>
<option>GMRS</option>
<option>MURS</option>
<option>Upload …</option>
</select>
</p>

<div id="drop-area" class="drop-area" hidden=true>
  <p>Drag & drop file here or click to select</p>
  <input type="file" id="fileInput" name="fileInput">
</div>

<p class="filters">Filter by band: <input type=checkbox name=bandFilter onclick="bandFilterVisibility()">&nbsp;
<span id="bandFilterChecks" style="visibility: hidden">
HF<input type=checkbox name=hf>&nbsp;
2m<input type=checkbox name=vhf>&nbsp;
1.25m<input type=checkbox name=vhf2>&nbsp;
70cm<input type=checkbox name=uhf>&nbsp;
GMRS<input type=checkbox name=gmrs>&nbsp;
Digital<input type=checkbox name=digital>
</span>
</p>

<p class="filters">Filter by mode: <input type=checkbox name=modeFilter onclick="modeFilterVisibility()">&nbsp;
<span id="modeFilterChecks" style="visibility: hidden">
FM<input type=checkbox name=FM>&nbsp;
AM<input type=checkbox name=AM>&nbsp;
LSB<input type=checkbox name=LSB>&nbsp;
USB<input type=checkbox name=USB>&nbsp;
CW<input type=checkbox name=CW>&nbsp;
PKT<input type=checkbox name=PKT>&nbsp;
P25<input type=checkbox name=P25>&nbsp;
DMR<input type=checkbox name=DMR>&nbsp;
DSTAR<input type=checkbox name=DSTAR>&nbsp;
NXDN<input type=checkbox name=NXDN>&nbsp;
ATV<input type=checkbox name=ATV>&nbsp;
DATV<input type=checkbox name=DATV>&nbsp;
Other digital<input type=checkbox name=DIG>&nbsp;
</span>
</p>

<h2>Output options:</h2>
<p>Format: <select name=outputFormat>
<option>Chirp</option>
<option>RT Systems</option>
<option>Icom</option>
</select>
</p>
<p>Start: <input type=text value="1" size=5 name="start"></p>

Long names: <input type=checkbox name=longNames>
<span class=qmark onclick="toggleVis('nameHelp')">?
<span id=nameHelp class="popupBox hidden">
<p>By default, the name field in the output
is the same as the name field in the input, which is usually short enough to
fit the display of most radios.</p>
<p>Some radios can display longer names, and so this flag adds some extra
information to the name where appropriate. Typically this means adding the
station call sign if not already part of the name. For e.g. ACS ICS 217 forms,
the channel number is added if not already present.</p>
</span></span>
<br><br>

Sparse: <input type=checkbox name=sparse>
<span class=qmark onclick="toggleVis('scaleHelp')">?<span id="scaleHelp" class="popupBox hidden">
<p>By default, output records are written and numbered in the order
they're read from the input. The record numbers start at the Start
value given above and are strictly incrementing, ignoring the record
numbers in the input file.</p>
<p>Gaps in the input record numbers do not result in gaps in the
output. The output might look something like this:</p>
<table>
<tr><th>Location</th><th>Name</th><th>Frequency</th></tr>
<tr><td>1</td><td>Chan 1</td><td>146.96</td></tr>
<tr><td>2</td><td>Chan 2</td><td>146.96</td></tr>
<tr><td>3</td><td>Chan 3</td><td>146.40</td></tr>
<tr><td>4</td><td>Chan 6</td><td>146.50</td></tr>
<tr><td>5</td><td>Chan 7</td><td>146.60</td></tr>
</table>
<p>When <b>Sparse</b> is selected, the input record numbers are taken into account,
and if there are gaps in the input, there will be gaps in the output.</p>
<table>
<tr><th>Location</th><th>Name</th><th>Frequency</th></tr>
<tr><td>1</td><td>Chan 1</td><td>146.96</td></tr>
<tr><td>2</td><td>Chan 2</td><td>146.96</td></tr>
<tr><td>3</td><td>Chan 3</td><td>146.40</td></tr>
<tr><td><b>6</b></td><td>Chan 6</td><td>146.50</td></tr>
<tr><td><b>7</b></td><td>Chan 7</td><td>146.60</td></tr>
</table>
</span></span><br>
</p>
<input type=submit name=submit>
<br>
</form>
<div id="debug"></div>
</html>

<html>
<script language="JavaScript">
<!--
setupDnD();
-->
</script>
