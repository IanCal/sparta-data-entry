import os
import json
from tabulate import tabulate

primary_version = "sparta"
secondary_version = "sparta_dup"

def get_donor(donor_id, root):
	donor_filename = os.path.join(root, 'data', 'donors', donor_id, 'donor_data.json')
	return json.load(open(donor_filename))

def get_all_donors(root):
	donor_folder = os.path.join(root,'data','donors')
	return os.listdir(donor_folder)

def diff(primary, secondary, loc=''):
	for key, primary_value in sorted(primary.items()):
		if key == 'updated':
			continue
		secondary_value = secondary[key]
		item_loc = loc+'.'+key
		if type(primary_value) == type({}):
			yield from diff(primary_value, secondary_value, item_loc)
		else:
			if primary_value != secondary_value:
				yield (item_loc, primary_value, secondary_value)


with open("differences.txt", 'w') as f_out: 
	# First, let's see if there are any missing things

	all_primary_donors = set(get_all_donors(primary_version))
	all_secondary_donors = set(get_all_donors(secondary_version))

	for donor in all_primary_donors - all_secondary_donors:
		print("Donor %s is in %s but not %s" % (donor, primary_version, secondary_version), file=f_out)

	for donor in all_secondary_donors - all_primary_donors:
		print("Donor %s is in %s but not %s" % (donor, secondary_version, primary_version), file=f_out)

	# Now compare all the donors that exist in both
	for donor in all_primary_donors.intersection(all_secondary_donors):
		primary_donor = get_donor(donor, primary_version)
		secondary_donor = get_donor(donor, secondary_version)
		diffs = list(diff(primary_donor, secondary_donor))
		if len(diffs) > 0:
			print("Differences found for donor %s" % donor, file=f_out)
			print(tabulate(diffs, headers=['key', primary_version, secondary_version]), file=f_out)