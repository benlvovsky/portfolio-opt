import os
import yaml

config = None

if config is None:
	fileName = os.path.join(os.path.dirname(__file__), 'settings.yaml')
	f = open(fileName)
	config = yaml.safe_load(f)
	f.close()
