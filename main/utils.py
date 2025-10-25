"""utils.py - Utility helpers used across the TradeSOS application.
Contains postcode parsing, geocoding mock, matchmaking logic, email helpers,
and small helpers like distance calculation and formatting utilities.
"""

import re
import logging
from datetime import datetime, timedelta
from flask import current_app
from flask_mail import Message
from app import mail, db
from models import Trade, Job

def parse_postcode(postcode):
    """Parse a UK postcode into components."""
    if not postcode:
        return None
    
    # Clean and normalize postcode
    postcode = postcode.upper().strip().replace(' ', '')
    
    # UK postcode regex pattern
    pattern = r'^([A-Z]{1,2})([0-9][A-Z0-9]?)([0-9])([A-Z]{2})$'
    match = re.match(pattern, postcode)
    
    if not match:
        return None
    
    area = match.group(1)
    district_num = match.group(2)
    sector = match.group(3)
    unit = match.group(4)
    
    district = area + district_num
    full_postcode = f"{area}{district_num} {sector}{unit}"
    
    return {
        'full': full_postcode,
        'area': area,
        'district': district,
        'sector': sector,
        'unit': unit
    }

def geocode_postcode(postcode):
    """Get lat/lon coordinates for a UK postcode. Mock implementation for MVP."""
    # In production, this would call a real geocoding service
    # For now, return approximate coordinates for major UK areas
    
    postcode_coords = {
        'M': (53.4808, -2.2426),  # Manchester
        'B': (52.4862, -1.8904),  # Birmingham
        'L': (53.4084, -2.9916),  # Liverpool
        'LS': (53.8008, -1.5491), # Leeds
        'S': (53.3811, -1.4701),  # Sheffield
        'E': (51.5074, -0.1278),  # London East
        'W': (51.5074, -0.1278),  # London West
        'N': (51.5074, -0.1278),  # London North
        'SW': (51.5074, -0.1278), # London Southwest
        'SE': (51.5074, -0.1278), # London Southeast
        'NW': (51.5074, -0.1278), # London Northwest
        'EC': (51.5074, -0.1278), # London City
        'WC': (51.5074, -0.1278), # London West Central
    }
    
    postcode_info = parse_postcode(postcode)
    if not postcode_info:
        return 51.5074, -0.1278  # Default to London
    
    area = postcode_info['area']
    return postcode_coords.get(area, (51.5074, -0.1278))

def find_matching_trades(job):
    """Find trades that match a job's requirements."""
    matching_trades = []
    
    # Find verified trades with matching coverage
    query = Trade.query.filter_by(verified=True)
    
    # Filter by coverage areas or districts
    from sqlalchemy import or_, and_
    
    coverage_conditions = []
    
    # Check if trade covers the job's postcode area
    coverage_conditions.append(Trade.coverage_areas.contains(f'"{job.postcode_area}"'))
    
    # Check if trade covers the job's postcode district
    coverage_conditions.append(Trade.coverage_districts.contains(f'"{job.postcode_district}"'))
    
    if coverage_conditions:
        query = query.filter(or_(*coverage_conditions))
        matching_trades = query.all()
    
    # Additional filtering could be added here:
    # - Skills matching (if job category matches trade skills)
    # - Radius checking (if lat/lon coordinates are available)
    # - Availability checking
    
    logging.info(f"Found {len(matching_trades)} matching trades for job {job.id}")
    return matching_trades

def send_job_notification(job, trades):
    """Send job notifications to matching trades."""
    if not trades:
        logging.info(f"No trades to notify for job {job.id}")
        return
    
    # Separate premium and standard trades
    premium_trades = [t for t in trades if t.plan_tier == 'premium']
    standard_trades = [t for t in trades if t.plan_tier == 'standard']
    
    # Send immediate notifications to premium trades
    if premium_trades:
        send_email_notifications(job, premium_trades, is_premium=True)
        logging.info(f"Sent premium notifications for job {job.id} to {len(premium_trades)} trades")
    
    # For MVP, send to standard trades immediately too
    # In production, this would be delayed by PREMIUM_FIRST_ACCESS_MINUTES
    if standard_trades:
        send_email_notifications(job, standard_trades, is_premium=False)
        logging.info(f"Sent standard notifications for job {job.id} to {len(standard_trades)} trades")

def send_email_notifications(job, trades, is_premium=False):
    """Send email notifications to trades about a new job."""
    try:
        priority_text = "PREMIUM EARLY ACCESS" if is_premium else "NEW JOB ALERT"
        urgency_text = {
            'emergency_now': 'EMERGENCY - Immediate Response Required',
            'urgent_2h': 'URGENT - Within 2 Hours',
            'same_day': 'Same Day Service Required',
            'next_day': 'Next Day Service Required'
        }.get(job.urgency, 'Service Required')
        
        subject = f"TradeSOS {priority_text}: {urgency_text} - {job.title}"
        
        for trade in trades:
            if trade.user and trade.user.email:
                try:
                    msg = Message(
                        subject=subject,
                        recipients=[trade.user.email],
                        html=render_job_notification_email(job, trade, is_premium)
                    )
                    mail.send(msg)
                except Exception as e:
                    logging.error(f"Failed to send email to {trade.user.email}: {str(e)}")
                    
    except Exception as e:
        logging.error(f"Error sending email notifications: {str(e)}")

def render_job_notification_email(job, trade, is_premium):
    """Render the job notification email template."""
    urgency_colors = {
        'emergency_now': '#dc3545',  # Red
        'urgent_2h': '#fd7e14',      # Orange
        'same_day': '#ffc107',       # Yellow
        'next_day': '#28a745'        # Green
    }
    
    urgency_color = urgency_colors.get(job.urgency, '#6c757d')
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>New Job Alert - TradeSOS</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px;">
                <h1 style="color: #1a472a; margin: 0;">TradeSOS</h1>
                {'<p style="color: #dc3545; font-weight: bold; margin: 5px 0;">PREMIUM EARLY ACCESS</p>' if is_premium else ''}
            </div>
            
            <div style="background: {urgency_color}; color: white; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
                <h2 style="margin: 0;">{job.urgency.replace('_', ' ').title()}</h2>
            </div>
            
            <h3>{job.title}</h3>
            <p><strong>Category:</strong> {job.category.title()}</p>
            <p><strong>Location:</strong> {job.postcode_full}</p>
            <p><strong>Description:</strong></p>
            <p>{job.description}</p>
            
            <div style="background: #e9ecef; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 0;"><strong>To accept this job, log in to your TradeSOS dashboard:</strong></p>
                <a href="{current_app.config.get('BASE_URL', 'http://localhost:5000')}/trade/dashboard" 
                   style="display: inline-block; background: #1a472a; color: white; padding: 10px 20px; 
                          text-decoration: none; border-radius: 5px; margin-top: 10px;">
                    View Job & Accept
                </a>
            </div>
            
            <p style="font-size: 12px; color: #6c757d;">
                This job was sent to you because it matches your coverage area and skills. 
                First trade to accept gets the job!
            </p>
        </div>
    </body>
    </html>
    """

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula."""
    import math
    
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    
    return c * r

def get_urgency_display(urgency):
    """Get display text and CSS class for urgency level."""
    urgency_info = {
        'emergency_now': {
            'text': 'Emergency Now',
            'class': 'badge-danger',
            'description': 'Immediate response required'
        },
        'urgent_2h': {
            'text': 'Urgent (2h)',
            'class': 'badge-warning',
            'description': 'Response needed within 2 hours'
        },
        'same_day': {
            'text': 'Same Day',
            'class': 'badge-info',
            'description': 'Response needed within 8 hours'
        },
        'next_day': {
            'text': 'Next Day',
            'class': 'badge-success',
            'description': 'Response needed within 24 hours'
        }
    }
    
    return urgency_info.get(urgency, {
        'text': urgency.replace('_', ' ').title(),
        'class': 'badge-secondary',
        'description': 'Service required'
    })

def format_price_gbp(amount_pence):
    """Format price in pence to GBP string."""
    pounds = amount_pence / 100
    return f"£{pounds:.2f}"

def allowed_file(filename, allowed_extensions=None):
    """Check if uploaded file has allowed extension."""
    if allowed_extensions is None:
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions
