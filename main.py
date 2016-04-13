from flask_wtf.csrf import CsrfProtect
from flask.ext.bootstrap import Bootstrap
from datetime import datetime
from flask import Flask, render_template, request, redirect
from random import getrandbits
from decimal import Decimal
import decimal
import os
from os.path import join as joinpath
import json
from time import time
from wtforms_components import read_only
from flask_wtf import Form
from wtforms import StringField, IntegerField, SubmitField, TextField, FormField, DecimalField
from wtforms.validators import DataRequired, NumberRange
from wtforms_components import DateTimeField

import wtforms_json


from wtforms import DecimalField


class BetterDecimalField(DecimalField):
    """
    Very similar to WTForms DecimalField, except with the option of rounding
    the data always.
    """
    def __init__(self, label=None, validators=None, places=2, rounding=None,
                 round_always=True, **kwargs):
        super(BetterDecimalField, self).__init__(
            label=label, validators=validators, places=places, rounding=
            rounding, **kwargs)
        self.round_always = round_always

    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = decimal.Decimal(valuelist[0])
                if self.round_always and hasattr(self.data, 'quantize'):
                    exp = decimal.Decimal('.1') ** self.places
                    if self.rounding is None:
                        quantized = self.data.quantize(exp)
                    else:
                        quantized = self.data.quantize(
                            exp, rounding=self.rounding)
                    self.data = quantized
            except (decimal.InvalidOperation, ValueError):
                self.data = None
                raise ValueError(self.gettext('Not a valid decimal value'))



wtforms_json.init()


DATE_FORMAT = '%d/%m/%Y %H:%M'

app = Flask(__name__)
app.config["BOOTSTRAP_SERVE_LOCAL"] = True
app.secret_key = 'A0Zr98j/3khs4$%$]LWX/,?RT'

CsrfProtect(app)
Bootstrap(app)

def date_handler(obj):
    if hasattr(obj, 'strftime'):
        return obj.strftime(DATE_FORMAT)
    if type(obj) == type(Decimal()):
    	return str(obj)
    return obj


# Donors

def get_all_donors():
	donor_list = []
	path = joinpath("data", "donors")
	if not os.path.exists(path):
		os.makedirs(path)
	for entry in os.scandir(joinpath("data", "donors")):
		if entry.is_dir():
			print(entry)
			donor_list.append(json.load(open(joinpath(entry.path, "donor_data.json"))))
	return donor_list


class Donor(Form):
    donor_id = StringField('donor_id', validators=[DataRequired()])
    test_field = DateTimeField(
        'Date',
         format=DATE_FORMAT
    )
    age = IntegerField('age', validators=[DataRequired(), NumberRange(1,100)])
    ethnicity = StringField('ethnicity', validators=[DataRequired()])
    medications = TextField('medications')
    submit_button = SubmitField('Submit Form')



@app.route('/donors/new', methods=('GET', 'POST'))
def new_donor():
	form = Donor()
	if request.method == 'POST' and form.validate_on_submit():
		donor_id = form.donor_id.data
		path = joinpath("data", "donors", donor_id)
		if not os.path.exists(path):
			os.makedirs(path)
		with open(joinpath("data", "donors", donor_id, "donor_data.json"), "w+") as f_out:
			data = form.data
			json.dump(data, f_out, default=date_handler)
		return redirect('/donors/%s' % donor_id)

	print(form.data)
	return render_template('new_donor.html', form=form)

@app.route('/donors/<donor_id>')
def show_donor(donor_id):
	donor = json.load(open(joinpath("data", "donors", donor_id, "donor_data.json")))
	return render_template('donor.html', donor = donor)

@app.route('/donors/')
def donor_list():
    return render_template('donors.html', donors = get_all_donors())

# Donations

class Motility(Form):
	a = BetterDecimalField('a', places=2, validators=[DataRequired(), NumberRange(0,100)])
	b = IntegerField('b', validators=[DataRequired(), NumberRange(0,100)])
	c = IntegerField('c', validators=[DataRequired(), NumberRange(0,100)])
	d = IntegerField('d', validators=[DataRequired(), NumberRange(0,100)])

class Donation(Form):
    donor_id = StringField('donor_id', validators=[DataRequired()])
    donation_id = StringField('donation_id', validators=[DataRequired()])
    motility_pbs = FormField(Motility)
    counts = IntegerField('counts', validators=[DataRequired(), NumberRange(1,100)])
    volume = IntegerField('volume', validators=[DataRequired(), NumberRange(1,100)])
    start_time = DateTimeField('Start',format='%d/%m/%Y %H:%M')
    end_time = DateTimeField('End',format='%d/%m/%Y %H:%M')
    submit_button = SubmitField('Submit Form')

    def __init__(self, *args, **kwargs):
        super(Donation, self).__init__(*args, **kwargs)
        read_only(self.donation_id)
        read_only(self.donor_id)


def write_donation(form, donor_id, donation_id):
	path = joinpath("data", "donors", donor_id, "donations", donation_id)
	if not os.path.exists(path):
		os.makedirs(path)
	filename = joinpath(path, "donation_data.json")
	with open(filename, "w+") as f_out:
		data = form.data
		json.dump(data, f_out, default=date_handler)

@app.route('/donors/<donor_id>/donations/new', methods=('GET', 'POST'))
def new_donation(donor_id):
	form = Donation()
	form.donor_id.data = donor_id
	if form.donation_id.data is None:
		form.donation_id.data = str(getrandbits(32))
	if request.method == 'POST' and form.validate_on_submit():
		
		write_donation(form, donor_id, form.donation_id.data)
		return redirect('/donors/%s/donations/%s' % (donor_id, form.donation_id.data))
	return render_template('new_donation.html', form=form)

@app.route('/donors/<donor_id>/donations/<donation_id>/edit', methods=('GET', 'POST'))
def edit_donation(donor_id, donation_id):
	form = Donation()
	if request.method == 'POST' and form.validate_on_submit():
		write_donation(form, donor_id, donation_id)
		return redirect('/donors/%s/donations/%s' % (donor_id, donation_id))
	if form.donor_id.data is None:
		path = joinpath("data", "donors", donor_id, "donations", donation_id)
		filename = joinpath(path, "donation_data.json")
		donation = json.load(open(filename))
		form = Donation.from_json(donation)
		form.donor_id.data = donor_id
	return render_template('new_donation.html', form=form)

@app.route('/donors/<donor_id>/donations/<donation_id>')
def show_donation(donor_id, donation_id):
	path = joinpath("data", "donors", donor_id, "donations", donation_id)
	filename = joinpath(path, "donation_data.json")
	donation = json.load(open(filename))
	return render_template('donation.html', donation = donation)



if __name__ == '__main__':
    app.run(debug=True)