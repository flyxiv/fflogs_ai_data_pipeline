import os
import yaml

from pathlib import Path

""" Loads fflogs username and key from config.yml

Needs to have: fflogs_rotation_data_pipeline/config.yml with following categories:
   * username
   * key
"""
_YAML_FILE_DIR = os.path.join(Path(__file__).resolve().parent.parent, 'config.yml')

with open(_YAML_FILE_DIR, 'r') as config_yaml_file:
    config = yaml.load(config_yaml_file, yaml.FullLoader) 
    USERNAME = config['username']
    KEY = config['key']