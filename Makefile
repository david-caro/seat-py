SHELL=/bin/sh
PYTHON?=python

all:
	${PYTHON} setup.py build
install: 
	${PYTHON} setup.py install
	@make clean
clean:
	@rm -rvf build
test_seat:
	@echo 'Testing seat.Seat (REST Wrapper)'
	${PYTHON} test/test_seat.py -v
test_object:
	@echo 'Testing seat.Object (ORM)'
	${PYTHON} test/test_object.py -v
test: test_seat test_object