# Amazon Affiliate Review Site

Niche product review site (e.g. tech/gadgets) built with Django. Goal: display products, user reviews, track clicks to Amazon affiliate links (pending approval).

## Current Features
- Product listing with category filtering, sorting
- Click tracking & redirect for affiliate links
- Homepage + basic CSS styling
- Media upload for product images
- Separate apps: core + reviews

## Tech Stack
- Django 5.x
- Python 3.x
- (add any extras from requirements.txt)

## Setup (local)
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
