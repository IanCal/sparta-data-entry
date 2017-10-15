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
	'carbon_methods.csv': {
		'donor_id': ['donor_id'],
		'donation_time': ['donation_time'],
		'days_abstinence': ['abstinence'],
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