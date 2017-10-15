import os
import json
from csv import DictWriter

def get_donor(donor_id):
	donor_filename = os.path.join('data', 'donors', donor_id, 'donor_data.json')
	return json.load(open(donor_filename))

def get_all_donors():
	donor_folder = os.path.join('data','donors')
	return os.listdir(donor_folder)

file_descriptions = {
	'volume_and_age.csv': {
		'volume': ['initial_evaluation', 'volume'],
		'ph': ['initial_evaluation', 'ph'],
		'viscosity': ['initial_evaluation', 'viscosity'],
		'age': ['questionnaire', 'age'],
	},
	'proton_scans_ph.csv': {
		'initial_ph': ['initial_evaluation', 'ph'],
		'end_pbs_ph': ['pellets', 'eighty_percent', 'proton', 'tend', 'pbs_ph'],
		'end_sample_ph': ['pellets', 'eighty_percent', 'proton', 'tend', 'sample_ph'],
	},
}

for filename, description in file_descriptions.items():
	with open(os.path.join('tables', filename), 'w') as f_out:
		writer = DictWriter(f_out, sorted(description.keys()))
		writer.writeheader()
		for donor in get_all_donors():
			donor_data = get_donor(donor)
			required_data = {}
			for header, key_list in description.items():
				element = donor_data
				for key in key_list:
					element = element[key]
				required_data[header] = element
			writer.writerow(required_data)