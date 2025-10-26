from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, MultipleFileField
from wtforms import StringField, TextAreaField, PasswordField, SelectField, BooleanField, FloatField, IntegerField, SubmitField, RadioField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional, Regexp

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(), 
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    password2 = PasswordField('Repeat Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match')
    ])
    role = SelectField('I am a', choices=[
        ('customer', 'Customer (need trade services)'),
        ('trade', 'Trade Professional (provide services)')
    ], validators=[DataRequired()])
    name = StringField('Full Name / Company Name', validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    
    # Trade-specific fields
    companies_house_number = StringField('Companies House Registration Number', validators=[Optional(), Length(max=20)], 
                                        render_kw={'placeholder': 'e.g., 12345678'})
    vat_number = StringField('VAT Number', validators=[Optional(), Length(max=20)], 
                            render_kw={'placeholder': 'e.g., GB123456789'})
    skills = SelectField('Primary Trade Skills', choices=[
        ('plumbing', 'Plumbing & Drainage'),
        ('heating', 'Heating & Boilers'),
        ('electrical', 'Electrical Services'),
        ('locksmith', 'Locksmith Services'),
        ('roofing', 'Roofing & Guttering'),
        ('security', 'Security Systems'),
        ('glazing', 'Emergency Glazier'),
        ('gas', 'Gas Safety'),
        ('other', 'Other Emergency Services')
    ], validators=[Optional()])
    coverage_areas = StringField('Coverage Areas (UK Postcode Areas)', validators=[Optional()],
                                render_kw={'placeholder': 'e.g., M, SK, WA, OL'})
    
    # Required documents for trade professionals
    insurance_document = FileField('Public Liability Insurance Certificate (Required)', 
                                  validators=[Optional(), FileAllowed(['pdf', 'doc', 'docx', 'jpg', 'png'], 
                                            'Only PDF, DOC, DOCX, JPG, PNG files allowed')])
    qualification_documents = MultipleFileField('Trade Qualifications & Certifications', 
                                               validators=[Optional(), FileAllowed(['pdf', 'doc', 'docx', 'jpg', 'png'], 
                                                         'Only PDF, DOC, DOCX, JPG, PNG files allowed')])
    gas_safe_certificate = FileField('Gas Safe Certificate (if applicable)', 
                                    validators=[Optional(), FileAllowed(['pdf', 'doc', 'docx', 'jpg', 'png'])])
    
    submit = SubmitField('Register')

    def validate(self, **kwargs):
        # First run the default validators
        rv = super().validate(**kwargs)
        # If base validators already failed, continue to add conditional errors
        is_trade = (self.role.data == 'trade')
        if is_trade:
            # For trade professionals, enforce additional required fields
            # VAT number
            if not (self.vat_number.data and str(self.vat_number.data).strip()):
                self.vat_number.errors.append('VAT number is required')
                rv = False
            # Companies House number
            if not (self.companies_house_number.data and str(self.companies_house_number.data).strip()):
                self.companies_house_number.errors.append('Companies House registration number is required for trade professionals.')
                rv = False
            # Skills
            if not (self.skills.data and str(self.skills.data).strip()):
                self.skills.errors.append('Please select at least one primary trade skill.')
                rv = False
            # Insurance document (FileField) - ensure a file was uploaded
            ins = self.insurance_document.data
            has_insurance = False
            if ins:
                # FileField returns a FileStorage; check filename
                try:
                    filename = getattr(ins, 'filename', None)
                    if filename:
                        has_insurance = True
                except Exception:
                    has_insurance = False
            if not has_insurance:
                self.insurance_document.errors.append('Public liability insurance certificate is required for trade professionals.')
                rv = False
            # Qualification documents (MultipleFileField) - ensure at least one file
            quals = self.qualification_documents.data
            has_quals = False
            if quals:
                try:
                    # MultipleFileField provides a list of FileStorage objects
                    if isinstance(quals, (list, tuple)) and len([f for f in quals if getattr(f, 'filename', None)]) > 0:
                        has_quals = True
                except Exception:
                    has_quals = False
            if not has_quals:
                self.qualification_documents.errors.append('Please upload at least one qualification or certification document')
                rv = False

        return rv

class CustomerProfileForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    postcode = StringField('Postcode', validators=[
        Optional(), 
        Regexp(r'^[A-Z]{1,2}[0-9][A-Z0-9]?\s?[0-9][A-Z]{2}$', message='Invalid UK postcode format')
    ])
    submit = SubmitField('Update Profile')

class TradeProfileForm(FlaskForm):
    company = StringField('Company Name', validators=[DataRequired(), Length(min=2, max=100)])
    companies_house_number = StringField('Companies House Registration Number', validators=[DataRequired(), Length(max=20)], 
                                        render_kw={'placeholder': 'e.g., 12345678'})
    vat_number = StringField('VAT Number', validators=[Optional(), Length(max=20)])
    utr_number = StringField('UTR Number', validators=[Optional(), Length(max=20)])
    skills = StringField('Skills (comma-separated)', validators=[Optional()], 
                        render_kw={'placeholder': 'e.g., plumbing, heating, roofing, glazing, security systems'})
    coverage_areas = StringField('Coverage Areas (comma-separated)', validators=[Optional()],
                                render_kw={'placeholder': 'e.g., M, SK, WA'})
    coverage_districts = StringField('Coverage Districts (comma-separated)', validators=[Optional()],
                                   render_kw={'placeholder': 'e.g., M1, M3, SK1'})
    radius_km = FloatField('Coverage Radius (km)', validators=[Optional(), NumberRange(min=0, max=100)])
    insurance_document = FileField('Public Liability Insurance Document', 
                                  validators=[Optional(), FileAllowed(['pdf', 'doc', 'docx', 'jpg', 'png'])])
    submit = SubmitField('Update Profile')

class JobForm(FlaskForm):
    # Customer Contact Information (for anonymous posting)
    customer_name = StringField('Your Name', validators=[DataRequired(), Length(min=2, max=100)])
    customer_phone = StringField('Your Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    customer_email = StringField('Your Email', validators=[DataRequired(), Email()])
    
    # Job Details
    title = StringField('Job Title', validators=[DataRequired(), Length(min=5, max=200)])
    category = SelectField('Category', choices=[
        ('plumbing', 'Plumbing'),
        ('heating', 'Heating & Boilers'),
        ('electrical', 'Electrical'),
        ('gas', 'Gas Safety'),
        ('roofing', 'Roofing'),
        ('locksmith', 'Locksmith'),
        ('glazing', 'Glazing & Windows'),
        ('security', 'Security Systems'),
        ('other', 'Other Emergency')
    ], validators=[DataRequired()])
    description = TextAreaField('Description', validators=[
        DataRequired(), 
        Length(min=20, max=1000, message='Please provide a detailed description (20-1000 characters)')
    ], render_kw={'rows': 5})
    postcode = StringField('Postcode', validators=[
        DataRequired(),
        Regexp(r'^[A-Z]{1,2}[0-9][A-Z0-9]?\s?[0-9][A-Z]{2}$', message='Invalid UK postcode format')
    ])
    urgency = RadioField('Urgency', choices=[
        ('emergency_now', 'Emergency Now (immediate response needed)'),
        ('urgent_2h', 'Urgent (within 2 hours)'),
        ('same_day', 'Same Day (within 8 hours)'),
        ('next_day', 'Next Day (within 24 hours)')
    ], validators=[DataRequired()])
    photos = MultipleFileField('Photos (optional)', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    accept_terms = BooleanField('I agree to the terms of service and privacy policy', validators=[DataRequired()])
    submit = SubmitField('Get Emergency Trade Access')

class ReviewForm(FlaskForm):
    rating = SelectField('Rating', choices=[
        (5, '5 Stars - Excellent'),
        (4, '4 Stars - Very Good'),
        (3, '3 Stars - Good'),
        (2, '2 Stars - Fair'),
        (1, '1 Star - Poor')
    ], coerce=int, validators=[DataRequired()])
    text = TextAreaField('Review Comments', validators=[
        Optional(), 
        Length(max=500, message='Review must be less than 500 characters')
    ], render_kw={'rows': 4})
    submit = SubmitField('Submit Review')

class MessageForm(FlaskForm):
    message = TextAreaField('Message', validators=[
        DataRequired(),
        Length(min=1, max=500, message='Message must be between 1 and 500 characters')
    ], render_kw={'rows': 3})
    submit = SubmitField('Send Message')
