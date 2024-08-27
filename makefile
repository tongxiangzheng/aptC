all:
	
clean:

distclean: clean

install:
	mkdir -p $(DESTDIR)/usr/sbin
	cp bin/* $(DESTDIR)/usr/sbin/
	mkdir -p $(DESTDIR)/usr/share/aptC
	cp -r src/* $(DESTDIR)/usr/share/aptC/
	mkdir -p $(DESTDIR)/etc/
	cp -r etc/* $(DESTDIR)/etc/

uninstall:
	-rm -f $(DESTDIR)/usr/sbin/aptc
	-rm -f $(DESTDIR)/usr/sbin/apt-getc
	-rm -rf $(DESTDIR)/usr/share/aptC
	-rm -rf $(DESTDIR)/etc/aptC

.PHONY: all install clean distclean uninstall
