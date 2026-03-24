/** Parse form arguments from url (GET) */
function getArgs() {
    l = window.location;
    a = l.toString().split("?") ;
    b = a[1].toString().split("&") ;
    args = new Object() ;
    for( i=0; i<b.length; ++i) {
	av = b[i].split("=") ;
	args[av[0]] = unescape(av[1]) ;
    }
    return args;
}

/**
 * Copy src to clipboard and then make the "copied" text
 * visible.
 */
function copyFunc(src, copiedItem) {
  navigator.clipboard.writeText(src)
    .then(() => {
	// Optional: Provide feedback to the user
	if (copiedItem && (item = document.getElementById(copiedItem))) {
	    item.style.visibility='visible';
	}
    })
    .catch(err => {
	// Optional: Handle errors
	console.log('Failed to copy: ', err);
    });
}

/**
 * Fetch the given url with the given args
 * @return the returned text or none on failure.
 */
async function fetchData(url, args) {
    url = url + "?" + args;
    try {
	response = await fetch(url);
	if (response.ok) {
	    return await response.text();
	} else {
	    return "error " + response.ok;;
	}
    } catch(err) {
	return "fetch failed: " + err;
    }
}

/**
 * Fetch the given url with the given args, then
 * display it.
 * @return the returned text.
 */
async function fetchAndDisplay(url, args, win) {
    txt = await fetchData(url, args);
    if (txt) {
	if (win && (win = document.getElementById(win))) {
	    win.innerHTML = '<xmp>' + txt + '</xmp>';
	}
    }
    return txt;
}

function enableButton(button) {
    if (button && (button = document.getElementById(button))) {
	button.style.visibility='visible';
    } else {
	console.log("button not found");
    }
}

function disableButton(button) {
    if (button && (button = document.getElementById(button))) {
	button.style.visibility='hidden';
    } else {
	console.log("button not found");
    }
}

function setVis(element, vis) {
    element.style.visibility = vis ? 'visible' : 'hidden';
}

function toggleVis(name) {
    if (name && (element = document.getElementById(name))) {
	element.classList.toggle('hidden');
    } else {
	console.log('toggleVis("'+name+'"): element not found');
    }
}

// specific to Code Plug O'Rama

/** User clicked on bandFilter checkbox */
function bandFilterVisibility() {
    const form = document.forms["mainForm"];
    const source = form.elements["source"];
    const bandFilter = form.elements["bandFilter"];
    const bandFilterChecks = document.getElementById("bandFilterChecks");
    const checked = bandFilter.checked;
    setVis(bandFilterChecks, checked);
}

/** User clicked on modeFilter checkbox */
function modeFilterVisibility() {
    const form = document.forms["mainForm"];
    const modeFilter = form.elements["modeFilter"];
    const modeFilterChecks = document.getElementById("modeFilterChecks");
    const checked = modeFilter.checked;
    setVis(modeFilterChecks, checked);
}

/** User clicked on input selector */
function inputSelection() {
    const form = document.forms["mainForm"];
    const source = form.elements["source"];
    const fileInput = form.elements["fileInput"];
    const dropArea = document.getElementById("drop-area");
    // TODO: index of "Upload" changes if the options in "source" change.
    // fileInput.hidden = source.selectedIndex != 7;
    dropArea.hidden = source.selectedIndex != 7;
}

function setupDnD() {
    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('fileInput');

    // Prevent defaults for all drag events
    ['dragenter', 'dragover'].forEach(eventName => {
      dropArea.addEventListener(eventName, e => {
	e.preventDefault();
	e.stopPropagation();
	dropArea.classList.add('drag-over');
      }, false);
    });

    // Prevent defaults for all drag events
    ['dragleave', 'drop'].forEach(eventName => {
      dropArea.addEventListener(eventName, e => {
	e.preventDefault();
	e.stopPropagation();
	dropArea.classList.remove('drag-over');
      }, false);
    });

    // Handle dropped files
    dropArea.addEventListener('drop', handleFiles);

    // Handle clicks; launch the file chooser
    console.log("Registering event listener")
    dropArea.addEventListener('click', (e) => {
	//console.log("droparea event: " + e + ", type=" + e.type + ", which=" + e.which + ", detail=" + e.detail);
	e.stopPropagation();
	if (e.target == fileInput) return;	// let fileInput handle it when it arrives
	fileInput.showPicker();
    });

    //console.log("drag and drop ready to go");
}

/**
 * Handle drag-n-drop. Dropped files are transferred to the
 * fileInput element as if the user had selected them through
 * the picker.
 */
function handleFiles(evt) {
    const files = evt.dataTransfer.files;
    const formData = new FormData();
    const fileInput = document.getElementById('fileInput');

    // Jam these files into the fileInput object
    const dataTransfer = new DataTransfer();
    [...files].forEach(file => {
	dataTransfer.items.add(file);
	//console.log('File moved:', file.name);
    });
    fileInput.files = dataTransfer.files;
    //console.log('Files moved to fileInput')
}
