prefix = /usr
all:
	
clean:

distclean: clean

install:
	mkdir -p $(DESTDIR)$(prefix)/bin
	cp bin/* $(DESTDIR)$(prefix)/bin/
	mkdir -p $(DESTDIR)$(prefix)/share/aptC
	cp -r src/* $(DESTDIR)$(prefix)/share/aptC/
	mkdir -p $(DESTDIR)$(prefix)/etc/
	cp -r etc/* $(DESTDIR)$(prefix)/etc/

uninstall:
	-rm -f $(DESTDIR)$(prefix)/bin/aptc
	-rm -f $(DESTDIR)$(prefix)/bin/apt-getc

.PHONY: all install clean distclean uninstall
