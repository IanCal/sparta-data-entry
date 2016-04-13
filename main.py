from flask_wtf.csrf import CsrfProtect
from flask.ext.bootstrap import Bootstrap
from datetime import datetime
from flask import Flask, render_template, request, redirect
from random import getrandbits
from decimal import Decimal
from time import time
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

def wtforms_json_handler(obj):
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


@app.route('/donors/')
def donor_list():
    return render_template('donors.html', donors = get_all_donors())

# Donations

class Motility(Form):
    a = BetterDecimalField('a', places=2, validators=[DataRequired(), NumberRange(0,100)])
    b = IntegerField('b', validators=[DataRequired(), NumberRange(0,100)])
    c = IntegerField('c', validators=[DataRequired(), NumberRange(0,100)])
    d = IntegerField('d', validators=[DataRequired(), NumberRange(0,100)])

class Donor(Form):
    donor_id = StringField('donor_id', validators=[DataRequired()])
    counts = IntegerField('counts', validators=[DataRequired(), NumberRange(1,100)])
    volume = IntegerField('volume', validators=[DataRequired(), NumberRange(1,100)])
    motility_pbs = FormField(Motility)
    start_time = DateTimeField('Start',format='%d/%m/%Y %H:%M')
    end_time = DateTimeField('End',format='%d/%m/%Y %H:%M')
    submit_button = SubmitField('Submit Form')


def write_donor(form):
    donor_id = form.donor_id.data
    previous_path = joinpath("data", "donors", donor_id, "previous")
    if not os.path.exists(previous_path):
        os.makedirs(previous_path)
    path = joinpath("data", "donors", donor_id)
    filename = joinpath(path, "donor_data.json")
    for filename in [joinpath(path, "donor_data.json"),
                     joinpath(previous_path, "%d.json" % int(time()))]:
        with open(filename, "w+") as f_out:
            json.dump(form.data, f_out, default=wtforms_json_handler)

@app.route('/donors/new', methods=('GET', 'POST'))
def new_donor():
    form = Donor()
    if request.method == 'POST' and form.validate_on_submit():
        write_donor(form)
        return redirect('/donors/%s' % form.donor_id.data)
    return render_template('new_donor.html', form=form)

@app.route('/donors/<donor_id>', methods=('GET', 'POST'))
def edit_donor(donor_id):
    form = Donor()
    if request.method == 'POST' and form.validate_on_submit():
        write_donor(form)
        return redirect('/donors/%s' % (donor_id))
    if form.donor_id.data is None:
        path = joinpath("data", "donors", donor_id)
        filename = joinpath(path, "donor_data.json")
        donation = json.load(open(filename))
        form = Donor.from_json(donation)
    return render_template('new_donor.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)