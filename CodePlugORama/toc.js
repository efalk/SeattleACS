// Auto-generate table of contents
//
// To use:
//	<script type="text/javascript" src="toc.js"></script>
//	...
//	<div id="toc"></div>
//	...
//	<script language="JavaScript">
//	<!--
//	genToc(1);
//	// -->
//	</script>
//
// @param minlevel  minimum header level to index, default 1
// @param maxlevel  maximum header level to index, default 1
// @param divId     div id to write the table of contents, default "toc"
//
// Default minlevel, maxlevel is 1
// If there is only one h1 element, then it is considered to be the
// title and the table of contents starts at h2 instead.
//
// If minlevel is greater than 1, then any header less than that ends
// the toc. This lets you define tables of contents for subsections.
//
// You may want to define css for classes "tocHdr", "tocList", and "tocItem"
// as well as for your toc div.

function genToc(minlevel, maxlevel, divId)
{
  var i, start, level, toc_n = 0, value;
  var obuf = [];
  var curlevel;
  divId = typeof(divId) != 'undefined' ? divId : 'toc';
  var toc = document.getElementById(divId);
  if (toc == null) {
    console.log("Div " + divId + " not found");
    return;
  }
  //console.log("-- genToc(" + minlevel + ", " + maxlevel + ", " + divId + "), toc=" + toc);

//  dumpstructure();
//  return;

  if( toc == null ) {
    document.write('<div id="' + divId + '"></div>');
    var toc = document.getElementById(divId);
  }
  items = document.getElementsByTagName("h1");
  var dfltLevel = items.length <= 1 ? 2 : 1;
  minlevel = typeof(minlevel) != 'undefined' ? minlevel : dfltLevel;
  maxlevel = typeof(maxlevel) != 'undefined' ? maxlevel : dfltLevel;
  //console.log("--- genToc(" + minlevel + ", " + maxlevel + ", " + divId + "), toc=" + toc);
  maxlevel = Math.max(minlevel, maxlevel)
  curlevel = minlevel - 1;
  const iterator = document.createNodeIterator(
    document.body,
    NodeFilter.SHOW_ELEMENT,
    (node) =>
      node.tagName[0].toUpperCase() === "H" || node.tagName.toUpperCase() == 'DIV'
	? NodeFilter.FILTER_ACCEPT
	: NodeFilter.FILTER_REJECT,
  );
  var active = false;
  for (item = iterator.nextNode(); item != null; item = iterator.nextNode()) {
    if (item.id == divId) {
      active = true;
      //console.log(" now active");
    }
    if (!active) {
      continue;
    }
    if( item instanceof HTMLHeadingElement ) {
      level = parseInt(item.tagName[1]);
      if (active && level < minlevel) {
	//console.log(" no longer active");
	break;
      }
      if( level >= minlevel && level <= maxlevel ) {
	//console.log("    " + item.tagName + ", " + item.id);
	// May require more indentation
	for(; curlevel < level; ++curlevel) obuf.push('<ul class=tocList>');
	for(; curlevel > level; --curlevel) obuf.push('</ul>');
	value = item.innerHTML;
	obuf.push('<li class=tocItem><a href="#' + item.id + '">' +
	    value + '</a></li>');
      }
    }
  }
  obuf = obuf.join('');
  //console.log(obuf);
  toc.innerHTML = obuf;
}

function HTMLescape(s) {
  s = '' + s;
  return s.replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function dumpstructure() {
  d = document;
  debug('structure:');
  debug('d: ' + document);
  debug('children: ' + document.childNodes.length);
  var i;
  for( i = 0; i < document.childNodes.length; ++i)
    dumpnode(document.childNodes[i], i+'', 4);
  debug('');
}

function dumpnode(node, pfx, limit) {
  if( node instanceof Text )
    debug(pfx + ' Text: ' + node.nodeValue);
  else
    debug(pfx + ' node ' + node + ', children: ' + node.childNodes.length);
  if( limit <= 0 ) return;
  if( node.id == "debug" ) return;
  var i;
  for( i = 0; i < node.childNodes.length; ++i)
    dumpnode(node.childNodes[i], pfx+'.'+i, limit-1);
}
