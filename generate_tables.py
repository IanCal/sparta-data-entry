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
		'andrology_fp': ['initial_evaluation', 'andrology_motility', 'a'],
		'andrology_sp': ['initial_evaluation', 'andrology_motility', 'b'],
		'andrology_np': ['initial_evaluation', 'andrology_motility', 'c'],
		'andrology_im': ['initial_evaluation', 'andrology_motility', 'd'],
		'andrology_concentration': ['initial_evaluation', 'andrology_motility', 'concentration'],
		'casa_fp': ['initial_evaluation', 'casa_motility', 'a'],
		'casa_sp': ['initial_evaluation', 'casa_motility', 'b'],
		'casa_np': ['initial_evaluation', 'casa_motility', 'c'],
		'casa_im': ['initial_evaluation', 'casa_motility', 'd'],
		'casa_concentration': ['initial_evaluation', 'casa_motility', 'concentration'],
		'good_pbs_fp': ['pellets', 'eighty_percent', 'carbon_t0', 'pbs', 'a'],
		'good_pbs_sp': ['pellets', 'eighty_percent', 'carbon_t0', 'pbs', 'b'],
		'good_pbs_np': ['pellets', 'eighty_percent', 'carbon_t0', 'pbs', 'c'],
		'good_pbs_im': ['pellets', 'eighty_percent', 'carbon_t0', 'pbs', 'd'],
		'good_pbs_concentration': ['pellets', 'eighty_percent', 'carbon_t0', 'pbs', 'concentration'],
		'good_wash_fp': ['pellets', 'eighty_percent', 'carbon_t0', 'wash', 'a'],
		'good_wash_sp': ['pellets', 'eighty_percent', 'carbon_t0', 'wash', 'b'],
		'good_wash_np': ['pellets', 'eighty_percent', 'carbon_t0', 'wash', 'c'],
		'good_wash_im': ['pellets', 'eighty_percent', 'carbon_t0', 'wash', 'd'],
		'good_wash_concentration': ['pellets', 'eighty_percent', 'carbon_t0', 'wash', 'concentration'],
		'good_vitality_1_green': ['pellets', 'eighty_percent', 'carbon_t0', 'vitality', 'count_1', 'green'],
		'good_vitality_1_red': ['pellets', 'eighty_percent', 'carbon_t0', 'vitality', 'count_1', 'red'],
		'good_vitality_2_green': ['pellets', 'eighty_percent', 'carbon_t0', 'vitality', 'count_2', 'green'],
		'good_vitality_2_red': ['pellets', 'eighty_percent', 'carbon_t0', 'vitality', 'count_2', 'red'],
		'poor_pbs_fp': ['pellets', 'interface', 'carbon_t0', 'pbs', 'a'],
		'poor_pbs_sp': ['pellets', 'interface', 'carbon_t0', 'pbs', 'b'],
		'poor_pbs_np': ['pellets', 'interface', 'carbon_t0', 'pbs', 'c'],
		'poor_pbs_im': ['pellets', 'interface', 'carbon_t0', 'pbs', 'd'],
		'poor_pbs_concentration': ['pellets', 'interface', 'carbon_t0', 'pbs', 'concentration'],
		'poor_wash_fp': ['pellets', 'interface', 'carbon_t0', 'wash', 'a'],
		'poor_wash_sp': ['pellets', 'interface', 'carbon_t0', 'wash', 'b'],
		'poor_wash_np': ['pellets', 'interface', 'carbon_t0', 'wash', 'c'],
		'poor_wash_im': ['pellets', 'interface', 'carbon_t0', 'wash', 'd'],
		'poor_wash_concentration': ['pellets', 'interface', 'carbon_t0', 'wash', 'concentration'],
		'poor_vitality_1_green': ['pellets', 'interface', 'carbon_t0', 'vitality', 'count_1', 'green'],
		'poor_vitality_1_red': ['pellets', 'interface', 'carbon_t0', 'vitality', 'count_1', 'red'],
		'poor_vitality_2_green': ['pellets', 'interface', 'carbon_t0', 'vitality', 'count_2', 'green'],
		'poor_vitality_2_red': ['pellets', 'interface', 'carbon_t0', 'vitality', 'count_2', 'red'],
		'good_scan_1_type': ['pellets', 'eighty_percent', 'carbon_1', 'scan_type'],
		'good_scan_1_fp': ['pellets', 'eighty_percent', 'carbon_1', 'tend', 'wash', 'a'],
		'good_scan_1_sp': ['pellets', 'eighty_percent', 'carbon_1', 'tend', 'wash', 'b'],
		'good_scan_1_np': ['pellets', 'eighty_percent', 'carbon_1', 'tend', 'wash', 'c'],
		'good_scan_1_im': ['pellets', 'eighty_percent', 'carbon_1', 'tend', 'wash', 'd'],
		'good_scan_1_vitality_1_green': ['pellets', 'eighty_percent', 'carbon_1', 'tend', 'vitality', 'count_1', 'green'],
		'good_scan_1_vitality_1_red': ['pellets', 'eighty_percent', 'carbon_1', 'tend', 'vitality', 'count_1', 'red'],
		'good_scan_1_vitality_2_green': ['pellets', 'eighty_percent', 'carbon_1', 'tend', 'vitality', 'count_2', 'green'],
		'good_scan_1_vitality_2_red': ['pellets', 'eighty_percent', 'carbon_1', 'tend', 'vitality', 'count_2', 'red'],
		'good_scan_1_sample_ph': ['pellets', 'eighty_percent', 'carbon_1', 'tend', 'sample_ph'],
		'good_scan_1_pbs_ph': ['pellets', 'eighty_percent', 'carbon_1', 'tend', 'pbs_ph'],
		'good_scan_2_type': ['pellets', 'eighty_percent', 'carbon_2', 'scan_type'],
		'good_scan_2_fp': ['pellets', 'eighty_percent', 'carbon_2', 'tend', 'wash', 'a'],
		'good_scan_2_sp': ['pellets', 'eighty_percent', 'carbon_2', 'tend', 'wash', 'b'],
		'good_scan_2_np': ['pellets', 'eighty_percent', 'carbon_2', 'tend', 'wash', 'c'],
		'good_scan_2_im': ['pellets', 'eighty_percent', 'carbon_2', 'tend', 'wash', 'd'],
		'good_scan_2_vitality_1_green': ['pellets', 'eighty_percent', 'carbon_2', 'tend', 'vitality', 'count_1', 'green'],
		'good_scan_2_vitality_1_red': ['pellets', 'eighty_percent', 'carbon_2', 'tend', 'vitality', 'count_1', 'red'],
		'good_scan_2_vitality_2_green': ['pellets', 'eighty_percent', 'carbon_2', 'tend', 'vitality', 'count_2', 'green'],
		'good_scan_2_vitality_2_red': ['pellets', 'eighty_percent', 'carbon_2', 'tend', 'vitality', 'count_2', 'red'],
		'good_scan_2_sample_ph': ['pellets', 'eighty_percent', 'carbon_2', 'tend', 'sample_ph'],
		'good_scan_2_pbs_ph': ['pellets', 'eighty_percent', 'carbon_2', 'tend', 'pbs_ph'],
		'good_scan_3_type': ['pellets', 'eighty_percent', 'carbon_3', 'scan_type'],
		'good_scan_3_fp': ['pellets', 'eighty_percent', 'carbon_3', 'tend', 'wash', 'a'],
		'good_scan_3_sp': ['pellets', 'eighty_percent', 'carbon_3', 'tend', 'wash', 'b'],
		'good_scan_3_np': ['pellets', 'eighty_percent', 'carbon_3', 'tend', 'wash', 'c'],
		'good_scan_3_im': ['pellets', 'eighty_percent', 'carbon_3', 'tend', 'wash', 'd'],
		'good_scan_3_vitality_1_green': ['pellets', 'eighty_percent', 'carbon_3', 'tend', 'vitality', 'count_1', 'green'],
		'good_scan_3_vitality_1_red': ['pellets', 'eighty_percent', 'carbon_3', 'tend', 'vitality', 'count_1', 'red'],
		'good_scan_3_vitality_2_green': ['pellets', 'eighty_percent', 'carbon_3', 'tend', 'vitality', 'count_2', 'green'],
		'good_scan_3_vitality_2_red': ['pellets', 'eighty_percent', 'carbon_3', 'tend', 'vitality', 'count_2', 'red'],
		'good_scan_3_sample_ph': ['pellets', 'eighty_percent', 'carbon_3', 'tend', 'sample_ph'],
		'good_scan_3_pbs_ph': ['pellets', 'eighty_percent', 'carbon_3', 'tend', 'pbs_ph'],
		'poor_scan_1_type': ['pellets', 'interface', 'carbon_1', 'scan_type'],
		'poor_scan_1_fp': ['pellets', 'interface', 'carbon_1', 'tend', 'wash', 'a'],
		'poor_scan_1_sp': ['pellets', 'interface', 'carbon_1', 'tend', 'wash', 'b'],
		'poor_scan_1_np': ['pellets', 'interface', 'carbon_1', 'tend', 'wash', 'c'],
		'poor_scan_1_im': ['pellets', 'interface', 'carbon_1', 'tend', 'wash', 'd'],
		'poor_scan_1_vitality_1_green': ['pellets', 'interface', 'carbon_1', 'tend', 'vitality', 'count_1', 'green'],
		'poor_scan_1_vitality_1_red': ['pellets', 'interface', 'carbon_1', 'tend', 'vitality', 'count_1', 'red'],
		'poor_scan_1_vitality_2_green': ['pellets', 'interface', 'carbon_1', 'tend', 'vitality', 'count_2', 'green'],
		'poor_scan_1_vitality_2_red': ['pellets', 'interface', 'carbon_1', 'tend', 'vitality', 'count_2', 'red'],
		'poor_scan_1_sample_ph': ['pellets', 'interface', 'carbon_1', 'tend', 'sample_ph'],
		'poor_scan_1_pbs_ph': ['pellets', 'interface', 'carbon_1', 'tend', 'pbs_ph'],
		'poor_scan_2_type': ['pellets', 'interface', 'carbon_2', 'scan_type'],
		'poor_scan_2_fp': ['pellets', 'interface', 'carbon_2', 'tend', 'wash', 'a'],
		'poor_scan_2_sp': ['pellets', 'interface', 'carbon_2', 'tend', 'wash', 'b'],
		'poor_scan_2_np': ['pellets', 'interface', 'carbon_2', 'tend', 'wash', 'c'],
		'poor_scan_2_im': ['pellets', 'interface', 'carbon_2', 'tend', 'wash', 'd'],
		'poor_scan_2_vitality_1_green': ['pellets', 'interface', 'carbon_2', 'tend', 'vitality', 'count_1', 'green'],
		'poor_scan_2_vitality_1_red': ['pellets', 'interface', 'carbon_2', 'tend', 'vitality', 'count_1', 'red'],
		'poor_scan_2_vitality_2_green': ['pellets', 'interface', 'carbon_2', 'tend', 'vitality', 'count_2', 'green'],
		'poor_scan_2_vitality_2_red': ['pellets', 'interface', 'carbon_2', 'tend', 'vitality', 'count_2', 'red'],
		'poor_scan_2_sample_ph': ['pellets', 'interface', 'carbon_2', 'tend', 'sample_ph'],
		'poor_scan_2_pbs_ph': ['pellets', 'interface', 'carbon_2', 'tend', 'pbs_ph'],
		'poor_scan_3_type': ['pellets', 'interface', 'carbon_3', 'scan_type'],
		'poor_scan_3_fp': ['pellets', 'interface', 'carbon_3', 'tend', 'wash', 'a'],
		'poor_scan_3_sp': ['pellets', 'interface', 'carbon_3', 'tend', 'wash', 'b'],
		'poor_scan_3_np': ['pellets', 'interface', 'carbon_3', 'tend', 'wash', 'c'],
		'poor_scan_3_im': ['pellets', 'interface', 'carbon_3', 'tend', 'wash', 'd'],
		'poor_scan_3_vitality_1_green': ['pellets', 'interface', 'carbon_3', 'tend', 'vitality', 'count_1', 'green'],
		'poor_scan_3_vitality_1_red': ['pellets', 'interface', 'carbon_3', 'tend', 'vitality', 'count_1', 'red'],
		'poor_scan_3_vitality_2_green': ['pellets', 'interface', 'carbon_3', 'tend', 'vitality', 'count_2', 'green'],
		'poor_scan_3_vitality_2_red': ['pellets', 'interface', 'carbon_3', 'tend', 'vitality', 'count_2', 'red'],
		'poor_scan_3_sample_ph': ['pellets', 'interface', 'carbon_3', 'tend', 'sample_ph'],
		'poor_scan_3_pbs_ph': ['pellets', 'interface', 'carbon_3', 'tend', 'pbs_ph'],
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
