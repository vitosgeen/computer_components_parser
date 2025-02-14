# activate virtual environment
activate-venv:
	@echo "Activating virtual environment"
	source venv/bin/activate

# parser manufacture
run: 
	@echo "Running the parser"
	python main.py -m ${ARGS}

# parser manufacture for all
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

# clear code cache with file pyclean.sh
clear-pycache:
	@echo "Clearing pycache"
	./pyclean.sh

# clear cache and downloads
clear-cache-all:
	@echo "Clearing cache and downloads"
	rm -rf cache/*
	rm -rf downloads/*
# clear cache and downloads for old files only, for example files that are older than 1 day
clear-cache-old-files:
	@echo "Clearing cache and downloads"
	find cache/ -type f -mtime +1 -exec rm -f {} \;
	find downloads/ -type f -mtime +1 -exec rm -f {} \;