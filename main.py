import webbrowser, threading
from flask_wtf.csrf import CsrfProtect
from flask.ext.bootstrap import Bootstrap
from datetime import datetime
from flask import Flask, render_template, request, redirect, send_from_directory, flash
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

def flash_errors(form):
    """Flashes form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'error')

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
    return [("Questionnaire", all_set(data["questionnaire"])),
            ("Initial evaluation", all_set(data["initial_evaluation"])),
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
    donor_list.sort(key=lambda x: x.get("donor_id", 0), reverse=True)
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
    concentration = BetterDecimalField(label="Concentration (10^6/ml)", places=2, validators=[Optional(), NumberRange(0,1000)])

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
    sample_ph = BetterDecimalField("Sample pH", validators=[Optional()])
    pbs_ph = BetterDecimalField("PBS pH", validators=[Optional()])

class Duration(Form):
    start_time = DateTimeField('Start time',format='%d/%m/%Y %H:%M', validators=[Optional()])
    end_time = DateTimeField('End time',format='%d/%m/%Y %H:%M', validators=[Optional()])

class Scan(Duration):
    scan_type = SelectField('Scan type', choices=[  ('not_chosen', 'None'),
                                                    ('proton', 'Proton'),
                                                    ('cu_glucose', 'Cu Glucose'),
                                                    ('cu_fructose', 'Cu Fructose'),
                                                    ('c1_pyruvate', 'C1 Pyruvate'),
                                                    ('cu_glucose_c1_pyruvate', 'Cu Glucose & C1 Pyruvate'),
                                                    ('cu_fructose_c1_pyruvate', 'Cu Fructose & C1 Pyruvate'),
                                                    ('cu_galactose', 'Cu Galactose'),
                                                    ('c1_butyrate', 'C1 Butyrate'),
                                                    ('additional_substrate_1', 'Additional substrate 1'),
                                                    ('additional_substrate_2', 'Additional substrate 2'),
                                                    ('additional_substrate_3', 'Additional substrate 3'),
                                                 ])
    in_water_bath_time = DateTimeField('Time put in water bath',format='%d/%m/%Y %H:%M', validators=[Optional()])
    out_water_bath_time = DateTimeField('Time taken out of water bath',format='%d/%m/%Y %H:%M', validators=[Optional()])
    tend = FormField(Tend)
    zip_file = FileField('Zip File')
    scan_number = TextField('Scan number in file')
    comments = TextField('Details about the scan')

class Pellet(Form):
    carbon_t0 = FormField(T0)
    proton_t0 = FormField(T0)
    sperm_cell_count = IntegerField(label="Sperm cell count", validators=[Optional()])
    non_sperm_count = IntegerField(label="Non-sperm count", validators=[Optional()])
    suspected_sperm_heads = IntegerField(label="Suspected sperm heads", validators=[Optional()])
    suspected_epithelial_cells = IntegerField(label="Suspected epithelial cells", validators=[Optional()])
    proton = FormField(Scan, "Proton Scan")
    carbon_1 = FormField(Scan, "Carbon Scan 1")
    carbon_2 = FormField(Scan, "Carbon Scan 2")
    carbon_3 = FormField(Scan, "Carbon Scan 3")
    


class InitialEvaluation(Form):
    method = SelectField('Method of production', choices=[('home', 'Masturbation at home'),
                                                          ('clinic', 'Masturbation at clinic'),
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
    eighty_percent = FormField(Pellet, label="80% Pellet")
    interface = FormField(Pellet, label="40/80 Interface Pellet")


def create_yes_no(text):
    return SelectField(text, choices=[
                                    ('not_chosen', ''),
                                    ('yes','Yes'),
                                    ('no','No'),
                                    ]
                            ,validators=[Optional()])

class Questionnaire(Form):
    age = IntegerField('What is your age', validators=[Optional(), NumberRange(0, 100)])
    abstained = IntegerField('How long have you abstained in days', validators=[Optional(), NumberRange(0, 1000)])

    ethnicity = SelectField(label='Ethnicity', choices=[
                                    ('not_chosen', ''),
                                    ('white','White'),
                                    ('mixed','Mixed'),
                                    ('asian_asian_british','Asian or Asian British'),
                                    ('black_black_british','Black or Black British'),
                                    ('chinese_chinese_british','Chinese or Chinese British'),
                                    ('other','Other')
                                    ])
    height = BetterDecimalField('Height (m)', places=2, validators=[Optional()])
    weight = BetterDecimalField('Weight (kg)', places=2, validators=[Optional()])
    vasectomy = create_yes_no('Have you had a vasectomy?')
    conceived = create_yes_no('Have you conceived previously?')
    bloodborne_disease = create_yes_no('Have you tested positive for a blood borne disease (e.g. HIV or Hepatitis)?')
    sti = create_yes_no('Are you aware that you currently have a Sexually Transmitted Infection? (e.g.chlamydia)')
    medications = TextAreaField('Which medications have you taken in the past 3 months?')
    cancer = create_yes_no('Have you received treatment for cancer within the 2 past years?')
    supplements = TextAreaField('Are you taking any dietary supplements or multivitamins? If so which ones?')
    alcohol = create_yes_no('Do you drink alcohol?')

    units = BetterDecimalField('In a typical week how many units of alcohol do you consume?', places=2, validators=[Optional()])
    tobacco = create_yes_no('Do you smoke tobacco?')
    smokes = BetterDecimalField('In a typical day how many cigarettes/ cigars/ pipes do you smoke?', places=2, validators=[Optional()])
    smoking_type = RadioField( choices=[
                                    ('cigarettes','Cigarettes'),
                                    ('cigars','Cigars'),
                                    ('pipes','Pipes'),
                                    ], validators=[Optional()])

    use_bike = create_yes_no('Regular use of a bicycle or motorcycle')
    tight_underwear = create_yes_no('Wearing tight underwear or jeans')
    use_laptop = create_yes_no('Use of a laptop on lap')
    use_hottub = create_yes_no('Use hot-tubs or saunas')
    hot_env = create_yes_no('Work in a hot environment (e.g. kitchen)')
    use_bike = create_yes_no('Regular use of a bicycle or motorcycle')
    fever = create_yes_no('Had a fever of two weeks or more')
    warm_groin = create_yes_no('Activities that warm your groin')
    use_glues = create_yes_no('Use of glues, paints or solvents')
    exposed_lead = create_yes_no('Exposed to lead at work')
    night_shifts = create_yes_no('Any night shifts or sleep disorders')

    more_information = TextAreaField('More information')
    


class Donor(Form):

    donor_id = StringField('Donor ID', validators=[DataRequired()])
    donation_time =  DateTimeField('Donation Time',format='%d/%m/%Y %H:%M', validators=[Optional()])

    abstinence = StringField('Days of abstinence', validators=[Optional()])

    questionnaire = FormField(Questionnaire, label="Questionnaire")

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

    for pellet, pellet_name in [(form.pellets.interface, 'interface'), (form.pellets.eighty_percent, 'eighty_percent')]:
        for upload, name in [(pellet.proton.zip_file, 'proton_scan'),
                             (pellet.carbon_1.zip_file, 'carbon_1_scan'),
                             (pellet.carbon_2.zip_file, 'carbon_2_scan'),
                             (pellet.carbon_3.zip_file, 'carbon_3_scan')]:
            if len(upload.data.filename) > 0:
                upload.data.save(joinpath(path, pellet_name, "%s.zip" % name))
                copy2(joinpath(path, pellet_name, "%s.zip" % name), joinpath(path, pellet_name, 'previous', "%d_%s.zip" % (current_time, name)))
            upload.data = None
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
        for filename in ["proton_scan.zip", "carbon_1_scan.zip", "carbon_2_scan.zip", "carbon_3_scan.zip"]:
            file_path = joinpath('data', 'donors', donor_id, pellet, filename)
            if os.path.isfile(file_path):
                yield (donor_id, pellet, filename)

@app.route('/donors/<donor_id>', methods=('GET', 'POST'))
def edit_donor(donor_id):
    form = Donor()
    if request.method == 'POST':
        if form.validate_on_submit():
            write_donor(form)
            flash("Saved successfully", "info")
            return redirect('/donors/%s' % (donor_id))
        else:
            flash("Error saving, please check validation messages", "error")
            flash_errors(form)
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
    return render_template('index.html',
        donors=all_donors,
        total_donors=len(all_donors))

if __name__ == '__main__':
    threading.Timer(3, lambda: webbrowser.open('http://127.0.0.1:5000/') ).start()
    app.run(host='127.0.0.1', port=5000, debug=False)
