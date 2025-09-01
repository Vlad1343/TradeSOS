from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
import json

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='customer')  # customer, trade, admin
    verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    customer_profile = db.relationship('Customer', backref='user', uselist=False, cascade='all, delete-orphan')
    trade_profile = db.relationship('Trade', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'

class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    postcode = db.Column(db.String(10))
    addresses = db.Column(db.Text)  # JSON string of addresses
    
    # Relationships
    jobs = db.relationship('Job', backref='customer', lazy=True, cascade='all, delete-orphan')
    reviews_given = db.relationship('Review', backref='customer', lazy=True, cascade='all, delete-orphan')
    
    def get_addresses(self):
        return json.loads(self.addresses) if self.addresses else []
    
    def set_addresses(self, addresses_list):
        self.addresses = json.dumps(addresses_list)

class Trade(db.Model):
    __tablename__ = 'trades'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    companies_house_number = db.Column(db.String(20), nullable=False)
    vat_number = db.Column(db.String(20))
    utr_number = db.Column(db.String(20))
    skills = db.Column(db.Text)  # JSON array of skills
    coverage_areas = db.Column(db.Text)  # JSON array of postcode areas (e.g., ["M", "SK"])
    coverage_districts = db.Column(db.Text)  # JSON array of postcode districts (e.g., ["M1", "M3"])
    radius_km = db.Column(db.Float)
    insurance_document_url = db.Column(db.String(255))
    rating_avg = db.Column(db.Float, default=0.0)
    review_count = db.Column(db.Integer, default=0)
    verified = db.Column(db.Boolean, default=False)
    plan_tier = db.Column(db.String(20), default='standard')  # standard, premium
    stripe_customer_id = db.Column(db.String(100))
    stripe_subscription_id = db.Column(db.String(100))
    subscription_status = db.Column(db.String(20), default='inactive')  # active, inactive, canceled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    accepted_jobs = db.relationship('Job', backref='accepted_trade', lazy=True)
    reviews_received = db.relationship('Review', backref='trade', lazy=True)
    
    def get_skills(self):
        return json.loads(self.skills) if self.skills else []
    
    def set_skills(self, skills_list):
        self.skills = json.dumps(skills_list)
    
    def get_coverage_areas(self):
        return json.loads(self.coverage_areas) if self.coverage_areas else []
    
    def set_coverage_areas(self, areas_list):
        self.coverage_areas = json.dumps(areas_list)
    
    def get_coverage_districts(self):
        return json.loads(self.coverage_districts) if self.coverage_districts else []
    
    def set_coverage_districts(self, districts_list):
        self.coverage_districts = json.dumps(districts_list)

class Job(db.Model):
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True)
    
    # Anonymous customer fields (when no account exists)
    customer_name = db.Column(db.String(100))
    customer_phone = db.Column(db.String(20))
    customer_email = db.Column(db.String(120))
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    photos = db.Column(db.Text)  # JSON array of photo URLs
    postcode_full = db.Column(db.String(10), nullable=False)
    postcode_area = db.Column(db.String(5), nullable=False)
    postcode_district = db.Column(db.String(5), nullable=False)
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    urgency = db.Column(db.String(20), nullable=False)  # emergency_now, urgent_2h, same_day, next_day
    urgency_sla_minutes = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='posted')  # posted, accepted, en_route, in_progress, completed, canceled
    accepted_trade_id = db.Column(db.Integer, db.ForeignKey('trades.id'))
    accepted_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages = db.relationship('Message', backref='job', lazy=True, cascade='all, delete-orphan')
    location_pings = db.relationship('JobLocationPing', backref='job', lazy=True, cascade='all, delete-orphan')
    review = db.relationship('Review', backref='job', uselist=False, cascade='all, delete-orphan')
    
    def get_photos(self):
        return json.loads(self.photos) if self.photos else []
    
    def set_photos(self, photos_list):
        self.photos = json.dumps(photos_list)
    
    @staticmethod
    def get_urgency_sla_minutes(urgency):
        urgency_mapping = {
            'emergency_now': 0,
            'urgent_2h': 120,
            'same_day': 480,
            'next_day': 1440
        }
        return urgency_mapping.get(urgency, 480)

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    sender_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sender = db.relationship('User', backref='sent_messages')

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    trade_id = db.Column(db.Integer, db.ForeignKey('trades.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class JobLocationPing(db.Model):
    __tablename__ = 'job_location_pings'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    trade_id = db.Column(db.Integer, db.ForeignKey('trades.id'), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AdPlacement(db.Model):
    __tablename__ = 'ad_placements'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(50), nullable=False)  # banner, card, etc.
    image_url = db.Column(db.String(255))
    link_url = db.Column(db.String(255))
    starts_at = db.Column(db.DateTime)
    ends_at = db.Column(db.DateTime)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PartsBasket(db.Model):
    __tablename__ = 'parts_baskets'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    supplier = db.Column(db.String(100), nullable=False)
    items = db.Column(db.Text)  # JSON array of items
    estimated_total = db.Column(db.Float)
    status = db.Column(db.String(20), default='offered')  # offered, accepted, collected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    job_ref = db.relationship('Job', backref='parts_baskets')
    
    def get_items(self):
        return json.loads(self.items) if self.items else []
    
    def set_items(self, items_list):
        self.items = json.dumps(items_list)

class WebhookEvent(db.Model):
    __tablename__ = 'webhook_events'
    
    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(50), nullable=False)  # stripe, etc.
    event_type = db.Column(db.String(100), nullable=False)
    payload = db.Column(db.Text, nullable=False)  # JSON payload
    processed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
