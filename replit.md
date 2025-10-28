# Overview

TradeSOS is an emergency trade services platform built in Python Flask that connects customers needing urgent repairs with verified trade professionals across the UK. The application focuses on emergency callouts with real-time matching, location tracking, and subscription-based business model for trades. Key features include user authentication, job management with urgency levels, in-app messaging, location tracking, Stripe integration for subscriptions, and comprehensive admin tools.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Architecture
- **Framework**: Flask web framework with Blueprint-based route organization
- **Database**: SQLAlchemy ORM with SQLite for development, configured for PostgreSQL production
- **Authentication**: Flask-Login for session management with role-based access control (Customer, Trade, Admin)
- **Email**: Flask-Mail for notification and verification emails
- **File Handling**: Local file storage with abstraction layer for future S3 integration

## Data Layer
- **ORM**: SQLAlchemy with declarative base model structure
- **Key Models**: User, Customer, Trade, Job, Message, Review, AdPlacement, PartsBasket
- **Geographic Data**: UK postcode parsing and validation with geocoding service integration
- **Location Tracking**: JobLocationPing model with TTL retention for privacy

## Frontend Architecture
- **Templates**: Jinja2 templating with Bootstrap 5 responsive design
- **JavaScript**: Vanilla JS with modular component initialization
- **Real-time Features**: WebSocket support for live messaging and location updates
- **Form Handling**: WTForms with comprehensive validation and file upload support

## Business Logic
- **Job Matching**: Geographic matching by UK postcode areas/districts with radius-based filtering
- **Urgency System**: Four-tier urgency levels (emergency_now, urgent_2h, same_day, next_day) with SLA tracking
- **Premium Access**: First-access window for premium subscribers with configurable timing
- **Subscription Tiers**: Standard (£40/month) and Premium (£80/month) with feature differentiation

## Security & Privacy
- **Authentication**: Password hashing with Werkzeug security
- **Location Privacy**: Trade location sharing limited to active jobs with automatic cleanup
- **Role-based Access**: Comprehensive route guards and data access controls
- **File Security**: Secure filename handling and file type validation

# External Dependencies

## Payment Processing
- **Stripe**: Complete subscription management, checkout flows, and webhook handling for billing lifecycle events

## Communication Services
- **Email Service**: SMTP configuration for transactional emails (job notifications, verification, password reset)
- **Future SMS Integration**: Architecture prepared for SMS notifications via configurable provider

## Geographic Services
- **Geocoding API**: Pluggable interface for UK postcode to latitude/longitude conversion (currently stubbed)
- **Postcode Validation**: UK-specific postcode format validation and parsing

## File Storage
- **Local Storage**: Development configuration with abstraction layer
- **Cloud Storage Ready**: Architecture supports future S3 or similar cloud storage integration

## Infrastructure
- **Database**: PostgreSQL for production deployment
- **Session Management**: Redis-compatible session storage preparation
- **Environment Configuration**: Comprehensive environment variable configuration for all external services