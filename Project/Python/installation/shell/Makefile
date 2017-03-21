ifeq ($(origin JAVA_HOME), undefined)
  JAVA_HOME=/usr
endif

ifeq ($(origin NETLOGO), undefined)
  NETLOGO=../..
endif

ifeq ($(origin SCALA_JAR), undefined)
  SCALA_JAR=$(NETLOGO)/lib/scala-library.jar
endif

SRCS=$(wildcard src/*.java)

shell.jar: $(SRCS) manifest.txt
	mkdir -p classes
	$(JAVA_HOME)/bin/javac -g -encoding us-ascii -source 1.5 -target 1.5 -classpath $(NETLOGO)/NetLogo.jar:$(SCALA_JAR) -d classes $(SRCS)
	jar cmf manifest.txt shell.jar -C classes .

shell.zip: shell.jar
	rm -rf shell
	mkdir shell
	cp -rp shell.jar README.md Makefile src manifest.txt shell
	zip -rv shell.zip shell
	rm -rf shell
