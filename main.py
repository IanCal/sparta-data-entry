from flask import Flask, render_template, request, redirect
from flask_wtf.csrf import CsrfProtect
from flask.ext.bootstrap import Bootstrap
from time import time

from flask_wtf import Form
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange

import os
import json

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3khs4$%$]LWX/,?RT'

CsrfProtect(app)
Bootstrap(app)

class Donor(Form):
    donor_id = StringField('donor_id', validators=[DataRequired()])
    age = IntegerField('age', validators=[DataRequired(), NumberRange(1,100)])
    ethnicity = StringField('ethnicity', validators=[DataRequired()])
    submit_button = SubmitField('Submit Form')


def get_all_donors():
	donor_list = []
	for filename in os.listdir("data/donors/"):
		donor_list.append(json.load(open("data/donors/" + filename)))
	return donor_list

@app.route('/donors/new', methods=('GET', 'POST'))
def new_donor():
	form = Donor()
	if request.method == 'POST' and form.validate_on_submit():
		donor_id = form.donor_id.data
		with open("data/donors/%s" % donor_id, "w+") as f_out:
			json.dump({
				"donor_id": donor_id,
				"age": form.age.data,
				"ethnicity": form.ethnicity.data,
				"updated": time()
				}, f_out)
		return redirect('/donors/%s' % donor_id)
	return render_template('new_donor.html', form=form)

@app.route('/donors/<donor_id>')
def show_donor(donor_id):
	donor = json.load(open('data/donors/%s' % donor_id))
	return render_template('donor.html', donor = donor)

@app.route('/donors')
def donor_list():
    return render_template('donors.html', donors = get_all_donors())


if __name__ == '__main__':
    app.run(debug=True)