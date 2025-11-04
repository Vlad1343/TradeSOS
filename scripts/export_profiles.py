#!/usr/bin/env python3
"""
Export trade profiles (and linked documents) to CSV for easy management.
Run from the project root:
    python scripts/export_profiles.py

The script uses the Flask app factory in app.py, so it must be run where the project can import app.
"""
import csv
import os
from datetime import datetime
from app import app, db
from models import Trade, TradeDocument

OUT_DIR = os.path.join(os.getcwd(), 'exports')
os.makedirs(OUT_DIR, exist_ok=True)
OUT_FILE = os.path.join(OUT_DIR, f'trades_export_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv')

with app.app_context():
    trades = Trade.query.order_by(Trade.created_at.asc()).all()

    with open(OUT_FILE, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'trade_id', 'user_email', 'company', 'companies_house_number', 'vat_number',
            'skills', 'coverage_areas', 'coverage_districts', 'insurance_url', 'gas_safe_url',
            'qualification_files', 'verified', 'plan_tier', 'subscription_status', 'created_at'
        ])

        for t in trades:
            user_email = t.user.email if t.user else ''
            skills = ','.join(t.get_skills()) if t.get_skills() else ''
            coverage_areas = ','.join(t.get_coverage_areas()) if t.get_coverage_areas() else ''
            coverage_districts = ','.join(t.get_coverage_districts()) if t.get_coverage_districts() else ''

            docs = TradeDocument.query.filter_by(trade_id=t.id).all()
            insurance = ''
            gas_safe = ''
            qualifications = []
            for d in docs:
                if d.file_type == 'insurance':
                    insurance = d.url()
                elif d.file_type == 'gas_safe':
                    gas_safe = d.url()
                elif d.file_type == 'qualification':
                    qualifications.append(d.url())
                else:
                    qualifications.append(d.url())

            writer.writerow([
                t.id,
                user_email,
                t.company,
                t.companies_house_number or '',
                t.vat_number or '',
                skills,
                coverage_areas,
                coverage_districts,
                insurance,
                gas_safe,
                '|'.join(qualifications),
                'yes' if t.verified else 'no',
                t.plan_tier or '',
                t.subscription_status or '',
                t.created_at.strftime('%Y-%m-%d %H:%M:%S') if t.created_at else ''
            ])

print(f'Exported {len(trades)} trades to {OUT_FILE}')
