ifeq ($(origin JAVA_HOME), undefined)
  JAVA_HOME=/usr
endif

ifeq ($(origin NETLOGO), undefined)
  NETLOGO=../..
endif

JAVAC=$(JAVA_HOME)/bin/javac
SRCS=$(wildcard src/*.java)

url.jar: $(SRCS) manifest.txt Makefile
	mkdir -p classes
	$(JAVAC) -g -deprecation -Xlint:all -Xlint:-serial -Xlint:-path -encoding us-ascii -source 1.5 -target 1.5 -classpath web.jar:$(NETLOGO)/NetLogoLite.jar -d classes $(SRCS)
	jar cmf manifest.txt url.jar -C classes .

url.zip: url.jar
	rm -rf url
	mkdir url
	cp -rp url.jar README.md Makefile src web.jar manifest.txt myjavatools_license.txt WebPostExample.nlogo url
	zip -rv url.zip url
	rm -rf url
