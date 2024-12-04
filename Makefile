# parser manufacture
run: 
	@echo "Running the parser"
	python main.py ${ARGS}

run-all:
	@echo "Running the parser"
	python main.py -m asus
	python main.py -m asrock
	python main.py -m gigabyte
	python main.py -m msi
	python main.py -m biostar
	python main.py -m evga
	python main.py -m colorful
	python main.py -m galax