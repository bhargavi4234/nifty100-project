load:
	python src/etl/loader.py

test:
	pytest

clean:
	rm -f output/*.csv

report:
	@echo "Report generated."

ratios:
	@echo "Financial ratios not implemented in Sprint 1."

dashboard:
	@echo "Dashboard not implemented in Sprint 1."

api:
	@echo "API not implemented in Sprint 1."