from flask_wtf.csrf import CsrfProtect
from flask.ext.bootstrap import Bootstrap
from datetime import datetime
from flask import Flask, render_template, request, redirect, send_from_directory
from random import getrandbits
from decimal import Decimal
from shutil import copy2
from time import time
import decimal
import os
from os.path import join as joinpath
import json
from time import time
from wtforms_components import read_only
from flask_wtf import Form
from wtforms import StringField, IntegerField, SubmitField, TextField, FormField, DecimalField, SelectField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, Optional
from wtforms_components import DateTimeField
from werkzeug import secure_filename

from flask_wtf.file import FileField

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

def all_set(d):
    for k, v in d.items():
        if k.endswith("_spectra"):
            continue
        if v is None:
            return False
        if isinstance(v, dict):
            if not all_set(v):
                return False
    return True

def check_status(data):
    return [("Initial evaluation", all_set(data["initial_evaluation"])),
            ("Interface pellet", all_set(data["pellets"]["interface"])),
            ("80% pellet", all_set(data["pellets"]["eighty_percent"])),
            ]

def get_all_donors():
    donor_list = []
    path = joinpath("data", "donors")
    if not os.path.exists(path):
        os.makedirs(path)
    for entry in os.scandir(joinpath("data", "donors")):
        if entry.is_dir():
            data = json.load(open(joinpath(entry.path, "donor_data.json")))
            data["status"] = check_status(data)
            donor_list.append(data)
    donor_list.sort(key=lambda x: x.get("updated", 0), reverse=True)
    return donor_list


@app.route('/donors/')
def donor_list():
    return render_template('donors.html', donors = get_all_donors())

# Donations

class Motility(Form):
    a = BetterDecimalField(label="FP (a) %", places=2, validators=[Optional(), NumberRange(0,100)])
    b = BetterDecimalField(label="SP (b) %", places=2, validators=[Optional(), NumberRange(0,100)])
    c = BetterDecimalField(label="NP (c) %", places=2, validators=[Optional(), NumberRange(0,100)])
    d = BetterDecimalField(label="IM (d) %", places=2, validators=[Optional(), NumberRange(0,100)])
    concentration = BetterDecimalField(label="Concentration (10^6/ml)", places=2, validators=[Optional(), NumberRange(0,100)])

class T0(Form):
    pbs = FormField(Motility)
    wash = FormField(Motility)

class T3(T0):
    ph_10 =  BetterDecimalField("pH 10", places=2, validators=[Optional()])
    ph_7 =  BetterDecimalField("pH 7", places=2, validators=[Optional()])
    ph_4 =  BetterDecimalField("pH 4", places=2, validators=[Optional()])


class Duration(Form):
    start_time = DateTimeField('Start time',format='%d/%m/%Y %H:%M', validators=[Optional()])
    end_time = DateTimeField('End time',format='%d/%m/%Y %H:%M', validators=[Optional()])

class Scan(Duration):
    scan_type = SelectField('Scan type', choices=[
                                                    ('proton', 'Proton'),
                                                    ('glucose_13cu', 'Glucose 13Cu'),
                                                    ('fructose_13cu', 'Fructose 13Cu'),
                                                    ('pyruvate_13c1', 'Pyruvate 13C1'),
                                                    ('pyruvate_13c2', 'Pyruvate 13C2'),
                                                    ('glucose_13cu_pyruvate_13c1', 'Glucose 13Cu & Pyruvate 13C1'),
                                                    ('glucose_13C1_6_pyruvate_13c2', 'Glucose 13C1,6 & Pyruvate 13C2'),
                                                    ('hydroxybutyrate', 'Hydroxybutyrate'),
                                                 ])

class Pellet(Form):
    t0 = FormField(T0)
    leukocyte_ratio_to_sperm = BetterDecimalField(places=2, validators=[Optional()])
    t3 = FormField(T3)
    scan_time = FormField(Scan, "Scan")
    raw_spectra = FileField('Raw spectra')
    matlab_spectra = FileField('ML spectra')


class InitialEvaluation(Form):

    sample_prep_duration = FormField(Duration, label="Sample Prep")
    analysis_duration = FormField(Duration, label="Analysis")
    volume = BetterDecimalField(label="Volume", places=2, validators=[Optional()])
    ph = BetterDecimalField(label="pH", places=1, validators=[Optional()])
    viscosity = SelectField(choices=[('normal', 'Normal'),
                                         ('high', 'High'),
                                         ])
    agglutination = SelectField(choices=[('none', 'None'),
                                         ('isolated', 'Isolated'),
                                         ('moderate', 'Moderate'),
                                         ('widespread', 'Widespread'),
                                         ('gross', 'Gross'),
                                         ])
    agglutination_type = SelectField(choices=[('none', 'None'),
                                         ('head', 'Head - Head'),
                                         ('tail', 'Tail - Tail'),
                                         ('mixed', 'Mixed'),
                                         ('tangle', 'Tangle'),
                                         ('tail_tip', 'Tail tip - Tail tip'),
                                         ])
    comments = TextAreaField()
    andrology_motility = FormField(Motility, label="Andrology Motility")
    casa_motility = FormField(Motility, label="CASA Motility")

class Pellets(Form):
    eighty_percent = FormField(Pellet, label="80% Pellet")
    interface = FormField(Pellet, label="80/40 Interface Pellet")
 


class Questionnaire(Form):
    ethnicity = SelectField(choices=[
                                    ('uno','uno')
                                    ])   

class Donor(Form):

    donor_id = StringField('Donor ID', validators=[DataRequired()])
    donation_time =  DateTimeField('Donation Time',format='%d/%m/%Y %H:%M', validators=[Optional()])

    abstinence = IntegerField('Days of abstinence', validators=[Optional(), NumberRange(0, 100000)])
    method = SelectField('Method of production', choices=[('home', 'Masturbation at home'), ('office', 'Masturbation at office')])
    bbquestionnaire = FormField(Questionnaire, label="Questionnaire")

    initial_evaluation = FormField(InitialEvaluation, label="Initial evaluation")
    pellets = FormField(Pellets)

    submit_button = SubmitField('Submit Form')

def write_donor(form):
    donor_id = form.donor_id.data
    current_time = int(time())
    previous_path = joinpath("data", "donors", donor_id, "previous")
    if not os.path.exists(previous_path):
        os.makedirs(previous_path)
    path = joinpath("data", "donors", donor_id)
    for pellet_type in ['interface', 'eighty_percent']:
        pellet_path = joinpath(path, pellet_type, 'previous')
        if not os.path.exists(pellet_path):
            os.makedirs(pellet_path)

    for upload, pellet, name in [(form.pellets.interface.raw_spectra.data, 'interface', 'raw_spectra'),
                                 (form.pellets.interface.matlab_spectra.data, 'interface', 'matlab_spectra'),
                                 (form.pellets.eighty_percent.raw_spectra.data, 'eighty_percent', 'raw_spectra'),
                                 (form.pellets.eighty_percent.matlab_spectra.data, 'eighty_percent', 'matlab_spectra')]:
        if len(upload.filename) > 0:
            upload.save(joinpath(path, pellet, "%s.raw" % name))
            copy2(joinpath(path, pellet, "%s.raw" % name), joinpath(path, pellet, 'previous', "%d_%s.raw" % (current_time, name)))
    form.pellets.interface.raw_spectra.data = None
    form.pellets.interface.matlab_spectra.data = None
    form.pellets.eighty_percent.raw_spectra.data = None
    form.pellets.eighty_percent.matlab_spectra.data = None

    filename = joinpath(path, "donor_data.json")
    for filename in [joinpath(path, "donor_data.json"),
                     joinpath(previous_path, "%d.json" % current_time)]:
        with open(filename, "w+") as f_out:
            data= form.data
            data["updated"] = current_time
            json.dump(data, f_out, default=wtforms_json_handler, indent=4)

@app.route('/donors/new', methods=('GET', 'POST'))
def new_donor():
    form = Donor()
    if request.method == 'POST' and form.validate_on_submit():
        write_donor(form)
        return redirect('/donors/%s' % form.donor_id.data)
    return render_template('new_donor.html', form=form)

def find_files(donor_id):
    for pellet in ["eighty_percent", "interface"]:
        for filename in ["matlab_spectra.raw", "raw_spectra.raw"]:
            file_path = joinpath('data', 'donors', donor_id, pellet, filename)
            if os.path.isfile(file_path):
                yield (donor_id, pellet, filename)

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
    return render_template('new_donor.html', form=form, files=find_files(donor_id))

@app.route('/download/<donor_id>/<pellet>/<filename>')
def custom_static(donor_id, pellet, filename):
    path = joinpath('data', 
                                        secure_filename(donor_id),
                                        secure_filename(pellet))
    print(path)
    return send_from_directory(joinpath('data', 
                                        'donors',
                                        secure_filename(donor_id),
                                        secure_filename(pellet)),
                                        secure_filename(filename))

def add_duration(durations, elem):
    start = elem["start_time"]
    end = elem["end_time"]
    if start is not None and end is not None:
        start = datetime.strptime(start, DATE_FORMAT)
        end = datetime.strptime(end, DATE_FORMAT)
        durations.append((end - start).total_seconds() / 60)


@app.route('/')
def root():
    all_donors = get_all_donors()
    sample_prep_durations = []
    analysis_durations = []
    scan_durations = []
    for donor in all_donors:
        add_duration(sample_prep_durations, donor["initial_evaluation"]["sample_prep_duration"])
        add_duration(analysis_durations, donor["initial_evaluation"]["analysis_duration"])
        for pellet in ["eighty_percent", "interface"]:
            add_duration(scan_durations, donor["pellets"][pellet]["scan_time"])
    return render_template('index.html',
        donors=all_donors,
        total_donors=len(all_donors),
        timing_histograms=
        [
            ('Sample prep', json.dumps(sample_prep_durations), 'sample_prep'),
            ('Initial analysis', json.dumps(analysis_durations), 'analysis'),
            ('Scans', json.dumps(scan_durations), 'scans'),
        ])

if __name__ == '__main__':
    app.run(debug=True)