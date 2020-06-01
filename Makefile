
version = 0.8.6

default:
	clear
	rm -rf /tmp/python-cyrus-$(version)
	mkdir /tmp/python-cyrus-$(version)
	cp AUTHORS Changelog cyruslib.py sievelib.py LICENSE README /tmp/python-cyrus-$(version)/
	rm -rf ../release/python-cyrus-$(version).tar.gz
	tar -C /tmp -czvf ../release/python-cyrus-$(version).tar.gz python-cyrus-$(version)
