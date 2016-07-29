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
from wtforms import StringField, widgets, IntegerField, RadioField, SelectMultipleField, SubmitField, TextField, FormField, DecimalField, SelectField, TextAreaField, FieldList
from wtforms.validators import DataRequired, NumberRange, Optional
from wtforms_components import DateTimeField
from werkzeug import secure_filename

from flask_wtf.file import FileField

import wtforms_json


from wtforms import DecimalField

class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


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

def is_asthenozoospermic(data):
    initial_evaluation = data["initial_evaluation"]
    motility = initial_evaluation["andrology_motility"]
    if motility["a"] is None or motility["a"] is None:
        return False
    a = float(motility["a"])
    b = float(motility["b"])
    return a + b < 26


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
            data["asthenozoospermic"] = is_asthenozoospermic(data)
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

class VitalitySection(Form):
    red = IntegerField(label="Red", validators=[Optional(), NumberRange(0,100000)])
    green = IntegerField(label="Green", validators=[Optional(), NumberRange(0,100000)])

class Vitality(Form):
    count_1 = FormField(VitalitySection, label="Count 1")
    count_2 = FormField(VitalitySection, label="Count 2")

class T0(Form):
    pbs = FormField(Motility)
    wash = FormField(Motility)
    vitality = FormField(Vitality)

class Tend(Form):
    wash = FormField(Motility)
    vitality = FormField(Vitality)

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
    tend = FormField(Tend)
    scan_time = FormField(Scan, "Scan")
    ph =  BetterDecimalField("pH", places=2, validators=[Optional()])
    zip_file = FileField('Zip File')


class InitialEvaluation(Form):
    method = SelectField('Method of production', choices=[('home', 'Masturbation at home'),
                                                          ('office', 'Masturbation at office'),
                                                          ('intercourse', 'Intercourse')])
    analysis_duration = FormField(Duration, label="Analysis")
    sample_prep_duration = FormField(Duration, label="Sample Prep")
    volume = BetterDecimalField(label="Volume", places=2, validators=[Optional()])
    ph = BetterDecimalField(label="pH", places=1, validators=[Optional()])

    morphology = BetterDecimalField(label="Morphology (% normal forms)", places=2, validators=[Optional()])
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

    pbs_ph =  BetterDecimalField("PBS pH", places=2, validators=[Optional()])
    eighty_percent = FormField(Pellet, label="80% Pellet")
    interface = FormField(Pellet, label="40/80 Interface Pellet")
 


class Questionnaire(Form):
    age = IntegerField('What is your age', validators=[Optional(), NumberRange(0, 100)])
    abstained = IntegerField('How long have you abstained in days', validators=[Optional(), NumberRange(0, 1000)])

    ethnicity = SelectField(label='Ethnicity', choices=[
                                    ('white','White'),
                                    ('mixed','Mixed'),
                                    ('asian_asian_british','Asian or Asian British'),
                                    ('black_black_british','Black or Black British'),
                                    ('chinese_chinese_british','Chinese or Chinese British'),
                                    ('other','Other')
                                    ])
    height = BetterDecimalField('Height (m)', places=2, validators=[Optional()])
    weight = BetterDecimalField('Weight (kg)', places=2, validators=[Optional()])
    vasectomy = SelectField('Have you had a vasectomy?', default=None, choices=[
                                    ('yes','Yes'),
                                    ('no','No'),
                                    ])
    conceived = SelectField('Have you conceived previously?', choices=[
                                    ('yes','Yes'),
                                    ('no','No'),
                                    ])
    bloodborne_disease = SelectField('Have you tested positive for a blood borne disease (e.g. HIV or Hepatitis)?', choices=[
                                    ('yes','Yes'),
                                    ('no','No'),
                                    ])
    sti = SelectField('Are you aware that you currently have a Sexually Transmitted Infection? (e.g.chlamydia)', choices=[
                                    ('yes','Yes'),
                                    ('no','No'),
                                    ])
    medications = TextAreaField('Which medications have you taken in the past 3 months?')
    cancer = SelectField('Have you received treatment for cancer within the 2 past years?', choices=[
                                    ('yes','Yes'),
                                    ('no','No'),
                                    ])
    supplements = TextAreaField('Are you taking any dietary supplements or multivitamins? If so which ones?')
    alcohol = SelectField('Do you drink alcohol?', choices=[
                                    ('yes','Yes'),
                                    ('no','No'),
                                    ])

    units = BetterDecimalField('In a typical week how many units of alcohol do you consume?', places=2, validators=[Optional()])
    tobacco = SelectField('Do you smoke tobacco?', choices=[
                                    ('yes','Yes'),
                                    ('no','No'),
                                    ])
    smokes = BetterDecimalField('In a typical day how many cigarettes/ cigars/ pipes do you smoke?', places=2, validators=[Optional()])
    smoking_type = RadioField( choices=[
                                    ('cigarettes','Cigarettes'),
                                    ('cigars','Cigars'),
                                    ('pipes','Pipes'),
                                    ], validators=[Optional()])
    more_information = TextAreaField('More information')
    


class Donor(Form):

    donor_id = StringField('Donor ID', validators=[DataRequired()])
    donation_time =  DateTimeField('Donation Time',format='%d/%m/%Y %H:%M', validators=[Optional()])

    abstinence = IntegerField('Days of abstinence', validators=[Optional(), NumberRange(0, 100000)])

    questionnaire = FormField(Questionnaire, label="Questionnaire")

    initial_evaluation = FormField(InitialEvaluation, label="Initial evaluation")
    pellets = FormField(Pellets)

    submit_button = SubmitField('Submit Form')

def write_donor(form):
    print("Write donor")
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

    for upload, pellet, name in [(form.pellets.interface.zip_file.data, 'interface', 'zip_file'),
                                 (form.pellets.eighty_percent.zip_file.data, 'eighty_percent', 'zip_file')]:
        if len(upload.filename) > 0:
            upload.save(joinpath(path, pellet, "%s.zip" % name))
            copy2(joinpath(path, pellet, "%s.zip" % name), joinpath(path, pellet, 'previous', "%d_%s.zip" % (current_time, name)))
    form.pellets.interface.zip_file.data = None
    form.pellets.eighty_percent.zip_file.data = None
    print("Saving the file")
    filename = joinpath(path, "donor_data.json")
    for filename in [joinpath(path, "donor_data.json"),
                     joinpath(previous_path, "%d.json" % current_time)]:
        with open(filename, "w+") as f_out:
            data= form.data
            data["updated"] = current_time
            json.dump(data, f_out, default=wtforms_json_handler, indent=4)
    print("Saved?")

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
    print("EDIT DONOR")
    form = Donor()
    print(form.validate_on_submit())
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
    print("RUNNIN")
    app.run(host='0.0.0.0', port=5000, debug=True)
