all:
	
clean:

distclean: clean

install:
	mkdir -p $(DESTDIR)/usr/bin
	cp bin/* $(DESTDIR)/usr/bin/
	mkdir -p $(DESTDIR)/usr/share/aptC
	cp -r src/* $(DESTDIR)/usr/share/aptC/
	mkdir -p $(DESTDIR)/etc/
	cp -r etc/* $(DESTDIR)/etc/

uninstall:
	-rm -f $(DESTDIR)/usr/bin/aptc
	-rm -f $(DESTDIR)/usr/bin/apt-getc

.PHONY: all install clean distclean uninstall
