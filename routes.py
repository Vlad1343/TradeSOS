import os
import json
import stripe
from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, flash, jsonify, current_app, session
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from app import db, login_manager, app
from models import User, Customer, Trade, Job, Message, Review, AdPlacement, PartsBasket, WebhookEvent
from forms import LoginForm, RegisterForm, CustomerProfileForm, TradeProfileForm, JobForm, ReviewForm
from utils import parse_postcode, geocode_postcode, find_matching_trades, send_job_notification

# Set up Stripe
stripe.api_key = app.config.get('STRIPE_SECRET_KEY')

# Helper function for file uploads
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Simple session setup
@app.before_request
def setup_session():
    pass

# Public routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'customer':
            return redirect(url_for('customer_dashboard'))
        elif current_user.role == 'trade':
            return redirect(url_for('trade_dashboard'))
        elif current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
    
    # Show public trade directory for anonymous users
    verified_trades = Trade.query.filter_by(verified=True).limit(6).all()
    return render_template('index.html', trades=verified_trades)

@app.route('/trade-directory')
def trade_directory():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    area = request.args.get('area', '')
    
    query = Trade.query.filter_by(verified=True)
    
    if search:
        query = query.filter(Trade.company.contains(search))
    
    if area:
        query = query.filter(Trade.coverage_areas.contains(f'"{area}"'))
    
    trades = query.paginate(page=page, per_page=12, error_out=False)
    
    return render_template('public/trade_directory.html', trades=trades, search=search, area=area)

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f'Welcome back! Logged in as {user.role}.', 'success')
            return redirect(url_for('index'))
        flash('Invalid email or password', 'danger')
    
    return render_template('auth/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if email already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('An account with this email already exists. Please use a different email or sign in.', 'danger')
            return render_template('auth/register.html', form=form)
        
        try:
            # Create user account
            user = User(email=form.email.data, role=form.role.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.flush()  # Get the user ID
            
            # Create role-specific profile
            if form.role.data == 'customer':
                customer = Customer(
                    user_id=user.id, 
                    name=form.name.data, 
                    phone=form.phone.data or None
                )
                db.session.add(customer)
                
            elif form.role.data == 'trade':
                # Handle file uploads for trade professionals
                insurance_doc_url = None
                qualification_docs = []
                gas_safe_doc_url = None
                
                # Upload insurance document
                if form.insurance_document.data:
                    insurance_file = form.insurance_document.data
                    if insurance_file and allowed_file(insurance_file.filename):
                        filename = secure_filename(f"insurance_{user.id}_{insurance_file.filename}")
                        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                        insurance_file.save(file_path)
                        insurance_doc_url = filename
                
                # Upload qualification documents
                if form.qualification_documents.data:
                    for i, qual_file in enumerate(form.qualification_documents.data):
                        if qual_file and allowed_file(qual_file.filename):
                            filename = secure_filename(f"qualification_{user.id}_{i}_{qual_file.filename}")
                            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                            qual_file.save(file_path)
                            qualification_docs.append(filename)
                
                # Upload Gas Safe certificate
                if form.gas_safe_certificate.data:
                    gas_safe_file = form.gas_safe_certificate.data
                    if gas_safe_file and allowed_file(gas_safe_file.filename):
                        filename = secure_filename(f"gas_safe_{user.id}_{gas_safe_file.filename}")
                        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                        gas_safe_file.save(file_path)
                        gas_safe_doc_url = filename
                
                # Create trade profile
                trade = Trade(
                    user_id=user.id,
                    company=form.name.data,
                    companies_house_number=form.companies_house_number.data or None,
                    vat_number=form.vat_number.data or None,
                    insurance_document_url=insurance_doc_url
                )
                
                # Set skills and coverage areas
                if form.skills.data:
                    trade.set_skills([form.skills.data])
                
                if form.coverage_areas.data:
                    areas = [area.strip().upper() for area in form.coverage_areas.data.split(',')]
                    trade.set_coverage_areas(areas)
                
                db.session.add(trade)
            
            db.session.commit()
            flash('Registration successful! Your account has been created. Trade professionals will be verified before accessing job offers.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Registration failed: {str(e)}. Please try again.', 'danger')
            return render_template('auth/register.html', form=form)
    
    return render_template('auth/register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Customer routes
@app.route('/customer/dashboard')
@login_required
def customer_dashboard():
    if current_user.role != 'customer':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    
    customer = Customer.query.filter_by(user_id=current_user.id).first()
    if not customer:
        flash('Customer profile not found.', 'danger')
        return redirect(url_for('index'))
    
    # Get recent jobs
    recent_jobs = Job.query.filter_by(customer_id=customer.id).order_by(Job.created_at.desc()).limit(5).all()
    
    # Get active ads for display
    active_ads = AdPlacement.query.filter(
        AdPlacement.active == True,
        AdPlacement.starts_at <= datetime.utcnow(),
        AdPlacement.ends_at >= datetime.utcnow()
    ).all()
    
    return render_template('customer/dashboard.html', customer=customer, jobs=recent_jobs, ads=active_ads)

# Public job creation (anonymous) - main entry point
@app.route('/job-request', methods=['GET', 'POST'])
def job_request():
    if request.method == 'GET':
        return render_template('job_request.html')
    
    # Handle form submission
    try:
        # Get form data
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        house_number = request.form.get('house_number', '').strip()
        street = request.form.get('street', '').strip()
        town = request.form.get('town', '').strip()
        urgency = request.form.get('urgency', '').strip()
        title = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()
        postcode = request.form.get('postcode', '').strip().upper()
        
        # Handle file uploads
        photo_urls = []
        if 'photos' in request.files:
            uploaded_files = request.files.getlist('photos')
            for file in uploaded_files:
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Add timestamp to filename to avoid conflicts
                    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                    filename = f"{timestamp}_{filename}"
                    
                    # Ensure upload directory exists
                    upload_path = os.path.join(app.root_path, 'uploads')
                    if not os.path.exists(upload_path):
                        os.makedirs(upload_path)
                    
                    file_path = os.path.join(upload_path, filename)
                    file.save(file_path)
                    photo_urls.append(f"/uploads/{filename}")
        
        # Basic validation
        if not all([name, phone, email, house_number, street, town, urgency, title, category, description, postcode]):
            flash('Please fill in all required fields.', 'danger')
            return render_template('job_request.html')
        
        # Parse postcode
        postcode_info = parse_postcode(postcode)
        if not postcode_info:
            flash('Invalid UK postcode format.', 'danger')
            return render_template('job_request.html')
        
        # Get coordinates (mock for now)
        lat, lon = geocode_postcode(postcode)
        
        # Create job with anonymous customer information
        job = Job(
            customer_name=name,
            customer_phone=phone,
            customer_email=email,
            customer_house_number=house_number,
            customer_street=street,
            customer_town=town,
            title=title,
            category=category,
            description=description,
            postcode_full=postcode_info['full'],
            postcode_area=postcode_info['area'],
            postcode_district=postcode_info['district'],
            lat=lat,
            lon=lon,
            urgency=urgency,
            urgency_sla_minutes=Job.get_urgency_sla_minutes(urgency)
        )
        
        # Add uploaded files to job
        if photo_urls:
            job.set_photos(photo_urls)
        
        db.session.add(job)
        db.session.commit()
        
        # Find and notify matching trades
        matching_trades = find_matching_trades(job)
        send_job_notification(job, matching_trades)
        
        return render_template('job_request.html', success=True)
        
    except Exception as e:
        flash('Something went wrong. Please try again.', 'danger')
        return render_template('job_request.html')

@app.route('/create-job', methods=['GET', 'POST'])
def create_job():
    form = JobForm()
    
    if form.validate_on_submit():
        # Parse postcode
        postcode_info = parse_postcode(form.postcode.data)
        if not postcode_info:
            flash('Invalid UK postcode format.', 'danger')
            return render_template('customer/create_job.html', form=form)
        
        # Get coordinates (mock for now)
        lat, lon = geocode_postcode(form.postcode.data)
        
        # Handle photo uploads
        photo_urls = []
        if form.photos.data:
            for photo in form.photos.data:
                if photo and allowed_file(photo.filename):
                    filename = secure_filename(photo.filename)
                    filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    photo.save(photo_path)
                    photo_urls.append(f"/uploads/{filename}")
        
        # Create job with anonymous customer information
        job = Job(
            customer_name=form.customer_name.data,
            customer_phone=form.customer_phone.data,
            customer_email=form.customer_email.data,
            title=form.title.data,
            category=form.category.data,
            description=form.description.data,
            postcode_full=postcode_info['full'],
            postcode_area=postcode_info['area'],
            postcode_district=postcode_info['district'],
            lat=lat,
            lon=lon,
            urgency=form.urgency.data,
            urgency_sla_minutes=Job.get_urgency_sla_minutes(form.urgency.data)
        )
        job.set_photos(photo_urls)
        
        db.session.add(job)
        db.session.commit()
        
        # Find and notify matching trades
        matching_trades = find_matching_trades(job)
        send_job_notification(job, matching_trades)
        
        flash('Job created successfully! Matching trades have been notified and will contact you directly.', 'success')
        return redirect(url_for('job_confirmation', job_id=job.id))
    
    return render_template('customer/create_job.html', form=form)

# Existing customer route (for registered customers)
@app.route('/customer/create-job', methods=['GET', 'POST'])
@login_required
def customer_create_job():
    if current_user.role != 'customer':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    
    # Redirect to public job creation for simplicity
    return redirect(url_for('create_job'))

# Public job confirmation page
@app.route('/job/<int:job_id>/confirmation')
def job_confirmation(job_id):
    job = Job.query.get_or_404(job_id)
    return render_template('customer/job_confirmation.html', job=job)

@app.route('/job/<int:job_id>')
@login_required
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    
    # Check permissions
    if current_user.role == 'customer':
        customer = Customer.query.filter_by(user_id=current_user.id).first()
        if not customer or job.customer_id != customer.id:
            flash('Access denied.', 'danger')
            return redirect(url_for('customer_dashboard'))
    elif current_user.role == 'trade':
        trade = Trade.query.filter_by(user_id=current_user.id).first()
        if not trade or (job.accepted_trade_id and job.accepted_trade_id != trade.id):
            flash('Access denied.', 'danger')
            return redirect(url_for('trade_dashboard'))
    elif current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    
    # Get messages for this job
    messages = Message.query.filter_by(job_id=job.id).order_by(Message.created_at.asc()).all()
    
    return render_template('customer/job_detail.html', job=job, messages=messages)

# Trade routes
@app.route('/trade/dashboard')
@login_required
def trade_dashboard():
    if not current_user.is_authenticated or current_user.role != 'trade':
        flash('Access denied. Please log in as a trade professional.', 'danger')
        return redirect(url_for('login'))
    
    trade = Trade.query.filter_by(user_id=current_user.id).first()
    if not trade:
        flash('Trade profile not found.', 'danger')
        return redirect(url_for('index'))
    
    # Get available jobs in coverage areas
    available_jobs = []
    if trade.get_coverage_areas() or trade.get_coverage_districts():
        query = Job.query.filter_by(status='posted')
        
        area_conditions = []
        if trade.get_coverage_areas():
            for area in trade.get_coverage_areas():
                area_conditions.append(Job.postcode_area == area)
        
        if trade.get_coverage_districts():
            for district in trade.get_coverage_districts():
                area_conditions.append(Job.postcode_district == district)
        
        if area_conditions:
            from sqlalchemy import or_
            query = query.filter(or_(*area_conditions))
            available_jobs = query.order_by(Job.created_at.desc()).limit(10).all()
    
    # Get accepted jobs
    accepted_jobs = Job.query.filter_by(accepted_trade_id=trade.id).order_by(Job.created_at.desc()).limit(5).all()
    
    return render_template('trade/dashboard.html', trade=trade, available_jobs=available_jobs, accepted_jobs=accepted_jobs)

@app.route('/trade/profile', methods=['GET', 'POST'])
@login_required
def trade_profile():
    if current_user.role != 'trade':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    
    trade = Trade.query.filter_by(user_id=current_user.id).first()
    form = TradeProfileForm(obj=trade)
    
    if form.validate_on_submit():
        trade.company = form.company.data
        trade.companies_house_number = form.companies_house_number.data
        trade.vat_number = form.vat_number.data
        trade.utr_number = form.utr_number.data
        trade.set_skills(form.skills.data.split(',') if form.skills.data else [])
        trade.set_coverage_areas(form.coverage_areas.data.split(',') if form.coverage_areas.data else [])
        trade.set_coverage_districts(form.coverage_districts.data.split(',') if form.coverage_districts.data else [])
        trade.radius_km = form.radius_km.data
        
        # Handle insurance document upload
        if form.insurance_document.data:
            file = form.insurance_document.data
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = f"insurance_{trade.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                trade.insurance_document_url = f"/uploads/{filename}"
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('trade_profile'))
    
    # Pre-populate form fields
    if trade:
        form.skills.data = ','.join(trade.get_skills())
        form.coverage_areas.data = ','.join(trade.get_coverage_areas())
        form.coverage_districts.data = ','.join(trade.get_coverage_districts())
    
    return render_template('trade/profile.html', form=form, trade=trade)

@app.route('/trade/accept-job/<int:job_id>', methods=['POST'])
@login_required
def accept_job(job_id):
    if current_user.role != 'trade':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    
    trade = Trade.query.filter_by(user_id=current_user.id).first()
    job = Job.query.get_or_404(job_id)
    
    if job.status != 'posted':
        flash('This job is no longer available.', 'warning')
        return redirect(url_for('trade_dashboard'))
    
    # Accept the job
    job.status = 'accepted'
    job.accepted_trade_id = trade.id
    job.accepted_at = datetime.utcnow()
    
    db.session.commit()
    
    flash('Job accepted successfully!', 'success')
    return redirect(url_for('job_detail', job_id=job.id))

@app.route('/trade/billing')
@login_required
def trade_billing():
    if current_user.role != 'trade':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    
    trade = Trade.query.filter_by(user_id=current_user.id).first()
    return render_template('trade/billing.html', trade=trade)

@app.route('/trade/upgrade-to-premium')
@login_required
def upgrade_to_premium():
    if current_user.role != 'trade':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    
    trade = Trade.query.filter_by(user_id=current_user.id).first()
    
    try:
        # Create Stripe checkout session
        YOUR_DOMAIN = request.host_url.rstrip('/')
        
        checkout_session = stripe.checkout.Session.create(
            customer_email=current_user.email,
            line_items=[{
                'price_data': {
                    'currency': 'gbp',
                    'unit_amount': current_app.config['PREMIUM_PLAN_PRICE'],
                    'product_data': {
                        'name': 'TradeSOS Premium Subscription',
                        'description': 'Monthly premium subscription with priority job access',
                    },
                    'recurring': {
                        'interval': 'month',
                    },
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url=YOUR_DOMAIN + url_for('trade_billing') + '?success=true',
            cancel_url=YOUR_DOMAIN + url_for('trade_billing') + '?canceled=true',
            metadata={
                'trade_id': trade.id,
                'user_id': current_user.id,
            }
        )
        
        return redirect(checkout_session.url, code=303)
    
    except Exception as e:
        flash(f'Error creating checkout session: {str(e)}', 'danger')
        return redirect(url_for('trade_billing'))

# Admin routes
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    
    # Get statistics
    stats = {
        'total_users': User.query.count(),
        'total_customers': Customer.query.count(),
        'total_trades': Trade.query.count(),
        'verified_trades': Trade.query.filter_by(verified=True).count(),
        'total_jobs': Job.query.count(),
        'active_jobs': Job.query.filter(Job.status.in_(['posted', 'accepted', 'en_route', 'in_progress'])).count(),
    }
    
    # Get recent activity
    recent_jobs = Job.query.order_by(Job.created_at.desc()).limit(5).all()
    recent_trades = Trade.query.order_by(Trade.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', stats=stats, recent_jobs=recent_jobs, recent_trades=recent_trades)

@app.route('/admin/trades')
@login_required
def admin_trades():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    
    page = request.args.get('page', 1, type=int)
    trades = Trade.query.paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/trades.html', trades=trades)

@app.route('/admin/verify-trade/<int:trade_id>')
@login_required
def verify_trade(trade_id):
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    
    trade = Trade.query.get_or_404(trade_id)
    trade.verified = not trade.verified
    db.session.commit()
    
    status = 'verified' if trade.verified else 'unverified'
    flash(f'Trade {trade.company} has been {status}.', 'success')
    return redirect(url_for('admin_trades'))

# Messaging routes
@app.route('/job/<int:job_id>/send-message', methods=['POST'])
@login_required
def send_message(job_id):
    job = Job.query.get_or_404(job_id)
    message_text = request.form.get('message', '').strip()
    
    if not message_text:
        flash('Message cannot be empty.', 'danger')
        return redirect(url_for('job_detail', job_id=job_id))
    
    # Check permissions
    allowed = False
    if current_user.role == 'customer':
        customer = Customer.query.filter_by(user_id=current_user.id).first()
        if customer and job.customer_id == customer.id:
            allowed = True
    elif current_user.role == 'trade':
        trade = Trade.query.filter_by(user_id=current_user.id).first()
        if trade and job.accepted_trade_id == trade.id:
            allowed = True
    elif current_user.role == 'admin':
        allowed = True
    
    if not allowed:
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    
    # Create message
    message = Message(
        job_id=job.id,
        sender_user_id=current_user.id,
        text=message_text
    )
    
    db.session.add(message)
    db.session.commit()
    
    flash('Message sent successfully.', 'success')
    return redirect(url_for('job_detail', job_id=job_id))

# Review routes
@app.route('/job/<int:job_id>/review', methods=['GET', 'POST'])
@login_required
def create_review(job_id):
    if current_user.role != 'customer':
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    
    job = Job.query.get_or_404(job_id)
    customer = Customer.query.filter_by(user_id=current_user.id).first()
    
    if not customer or job.customer_id != customer.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('customer_dashboard'))
    
    if job.status != 'completed':
        flash('You can only review completed jobs.', 'warning')
        return redirect(url_for('job_detail', job_id=job_id))
    
    # Check if review already exists
    existing_review = Review.query.filter_by(job_id=job.id, customer_id=customer.id).first()
    if existing_review:
        flash('You have already reviewed this job.', 'info')
        return redirect(url_for('job_detail', job_id=job_id))
    
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            job_id=job.id,
            customer_id=customer.id,
            trade_id=job.accepted_trade_id,
            rating=form.rating.data,
            text=form.text.data
        )
        
        db.session.add(review)
        
        # Update trade's average rating
        trade = Trade.query.get(job.accepted_trade_id)
        if trade:
            trade.review_count += 1
            total_rating = (trade.rating_avg * (trade.review_count - 1)) + form.rating.data
            trade.rating_avg = total_rating / trade.review_count
        
        db.session.commit()
        
        flash('Review submitted successfully!', 'success')
        return redirect(url_for('job_detail', job_id=job_id))
    
    return render_template('customer/create_review.html', form=form, job=job)

# File serving
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return redirect(url_for('static', filename=f'uploads/{filename}'))

# Stripe webhook
@app.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, current_app.config['STRIPE_WEBHOOK_SECRET']
        )
    except ValueError:
        # Invalid payload
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return 'Invalid signature', 400
    
    # Log the webhook event
    webhook_event = WebhookEvent(
        provider='stripe',
        event_type=event['type'],
        payload=json.dumps(event)
    )
    db.session.add(webhook_event)
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session_data = event['data']['object']
        trade_id = session_data['metadata'].get('trade_id')
        
        if trade_id:
            trade = Trade.query.get(int(trade_id))
            if trade:
                trade.stripe_customer_id = session_data['customer']
                trade.stripe_subscription_id = session_data['subscription']
                trade.subscription_status = 'active'
                trade.plan_tier = 'premium'
    
    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        trade = Trade.query.filter_by(stripe_subscription_id=subscription['id']).first()
        
        if trade:
            if subscription['status'] == 'active':
                trade.subscription_status = 'active'
                trade.plan_tier = 'premium'
            else:
                trade.subscription_status = subscription['status']
                if subscription['status'] in ['canceled', 'unpaid']:
                    trade.plan_tier = 'standard'
    
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        trade = Trade.query.filter_by(stripe_subscription_id=subscription['id']).first()
        
        if trade:
            trade.subscription_status = 'canceled'
            trade.plan_tier = 'standard'
    
    # Mark as processed
    webhook_event.processed = True
    db.session.commit()
    
    return 'OK', 200

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    flash('File too large. Maximum size is 16MB.', 'danger')
    return redirect(request.url)
