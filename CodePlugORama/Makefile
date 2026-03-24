DESTHOST=edwfal@iad1-shared-b8-27.dreamhost.com
DESTTOP=efalk.org/public
DESTDIR=CodePlugORama

GENERATED_HTML = index.html help.html

all:	${GENERATED_HTML}

%.html:	%.md Makefile header.html trailer.html
	markdown.py -i $< -o $@ -T "Code Plug O'rama" -H header.html -t trailer.html

upload:	all *.css *.js
	rsync -avzL --exclude-from=EXCLUDES --delete-excluded ./ ${DESTHOST}:${DESTTOP}/${DESTDIR}

clobber:
	rm ${GENERATED_HTML}

server:
	python3 -m http.server --cgi
