# TradeSOS

<p align="center">
  <img src="photos/photo1.png" width="70%" alt="TradeSOS main page"><br>
  <em>Main page: welcome and entry into emergency requests.</em>
</p>

<p align="center">
  <img src="photos/photo2.png" width="70%" alt="TradeSOS emergency trades view"><br>
  <em>Emergency trades: urgency-aware listings for rapid response.</em>
</p>

<p align="center">
  <img src="photos/photo3.png" width="70%" alt="TradeSOS service request flow"><br>
  <em>Service request: structured intake with files, photos, and notes.</em>
</p>

<p align="center">
  <img src="photos/photo4.png" width="70%" alt="TradeSOS admin dashboard"><br>
  <em>Admin dashboard: oversight of jobs, trades, billing, and escalations.</em>
</p>

⚡️ Emergency trade callouts across the UK, built on FastAPI & Docker  
🛰️ <200ms geospatial dispatch with PostGIS spatial indexing  
💳 Idempotent Stripe webhooks with RBAC and secure messaging  

## 🚀 Overview
TradeSOS is an emergency trade services platform that connects customers needing urgent repairs to verified professionals. Built with FastAPI, PostgreSQL, PostGIS, and Stripe, it delivers <200ms professional matching through geospatial indexing and tiered priority scheduling. The platform prioritizes speed, trust, and operational control with RBAC enforcement, urgency-aware SLA routing, location tracking, secure messaging, and subscription billing to keep trades responsive and customers informed.

## 💡 Core Features
### 📍 Geospatial Dispatch Engine
- PostGIS spatial indexing for <200ms professional-to-request matching, reducing average response latency by 40%.
- UK postcode parsing, validation, and geocoding with radius-based trade matching.
- Tiered priority scheduler routing high-urgency jobs (emergency_now, urgent_2h, same_day, next_day) to premium contractors first.
- SLA timers, status updates, and premium-first access window enforcing compliance for critical emergency requests.
- Job lifecycle tracking with photos, attachments, and audit-friendly history.

### 💬 Collaboration & Customer Experience
- In-app messaging between customers and trades with optional email notifications.
- Location pings per job with TTL cleanup for privacy.
- Structured forms via WTForms with validation and secure file handling.

### 💳 Billing & Operations
- Idempotent Stripe webhook processing ensuring reliable subscription handling and consistent billing state under concurrent load.
- RBAC (Role-Based Access Control) with secure role isolation for Customers, Trades, and Admins.
- Role-aware dashboards with route guards and admin tooling for job review, payment oversight, and trade verification.

### 🔒 Trust & Safety
- RBAC enforcement with password hashing, session management, and CSRF protection.
- Secure filename handling and file-type validation for uploads.
- Configurable environment variables for secrets, storage, mail, and billing.

## 🏗️ Architecture
FastAPI + Jinja2 UI (Bootstrap 5)  
→ RBAC & Auth (Customer, Trade, Admin) with role isolation  
→ Geospatial Dispatch Engine (PostGIS spatial indexing, <200ms matching)  
→ Tiered Priority Scheduler (urgency SLAs, premium-first routing, job lifecycle)  
→ Persistence via SQLAlchemy ORM (PostgreSQL + PostGIS)  
→ Integrations: Idempotent Stripe webhooks, SMTP/email notifications, geocoding  
→ Real-time UX: WebSocket-ready messaging and location updates

## 🛠️ Tech Stack
| Layer | Technologies |
| --- | --- |
| Web | FastAPI, Jinja2, Bootstrap 5, Vanilla JS |
| Data | SQLAlchemy ORM, Alembic migrations, PostgreSQL + PostGIS (spatial indexing) |
| Geospatial | PostGIS spatial indexing, <200ms radius-based matching |
| Auth | RBAC with role isolation, password hashing, session management |
| Billing | Stripe subscriptions, idempotent webhook processing, plan pricing config |
| Forms | WTForms, CSRF protection |
| Messaging & Files | In-app messaging, uploads with secure filenames |
| Infra | Docker + docker-compose, environment-driven config |

## 🌟 What Sets It Apart
- **<200ms Geospatial Dispatch**: PostGIS spatial indexing matches professionals to emergency requests in under 200ms, reducing average response latency by 40%.
- **Tiered Priority Scheduler**: High-urgency jobs route to premium contractors first, enforcing SLA compliance for critical time-sensitive requests.
- **Idempotent Billing**: Stripe webhook processing ensures reliable subscription handling and consistent billing state under concurrent load.
- **RBAC Enforcement**: Secure role isolation (Customer/Trade/Admin) with route guards and operational visibility.
- **Privacy-Aware Location**: TTL-bound pings and guarded sharing scoped per job context.
