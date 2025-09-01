from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, MultipleFileField
from wtforms import StringField, TextAreaField, PasswordField, SelectField, BooleanField, FloatField, IntegerField, SubmitField, RadioField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional, Regexp

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

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
    companies_house_number = StringField('Companies House Registration Number', validators=[Optional(), Length(max=20)], 
                                        render_kw={'placeholder': 'e.g., 12345678'})
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    submit = SubmitField('Register')

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
