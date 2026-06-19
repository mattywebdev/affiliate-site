# 🚀 Affiliate Review Site

A full-stack Django affiliate review platform for curated tech and gadget recommendations.
It combines product listings, editorial articles, affiliate redirects, and click analytics in a production-deployed web app.

🔗 **Live:** [https://affiliate.matty-dev.com](https://affiliate.matty-dev.com)

---

## 📸 Preview

### 🖥️ Homepage (Desktop)
<p align="center">
  <a href="https://matty-dev.com">
    <img src="screenshots/homepage-desktop.png" width="800">
  </a>
</p>

### 📱 Mobile View
<p align="center">
  <img src="screenshots/homepage-mobile.png" width="300">
</p>

### 🛒 Product Listing
<p align="center">
  <img src="screenshots/product-list.png" width="800">
</p>

---

## ✨ Features

- 📰 Article system (buying guides, top picks, category-based content)
- 🛒 Product catalog with categories (Gaming, Office, Budget, etc.)
- ⭐ Ratings with half-star support
- ✅ Pros & Cons system
- 🔗 Affiliate click tracking & redirect system
- 📊 Click analytics per product
- 🏠 Dynamic homepage:
  - Latest articles
  - Top rated products
  - Most clicked products
- 🔐 Admin analytics panel (`https://affiliate.matty-dev.com/analytics/`)
- 🖼️ Custom media handling (product + article images)
- 📱 Mobile-friendly responsive layout
- ⚙️ Production-ready setup (Gunicorn, static/media config)

---

## 🧩 What This Demonstrates

- Full-stack Django development with models, views, templates, routing, and admin workflows
- Practical product thinking around search, sorting, categories, ratings, and editorial content
- Affiliate redirect handling with click logging, basic geo-aware Amazon store routing, and analytics
- Responsive custom UI built with HTML and CSS without relying on a frontend framework
- Production deployment awareness, including environment-based settings and static/media handling

---

## 🧱 Tech Stack

- **Backend:** Django 6.x  
- **Language:** Python 3.12  
- **Frontend:** HTML, CSS (custom, no framework)  
- **Database:** SQLite (PostgreSQL ready)  
- **Deployment:** DigitalOcean (Ubuntu + Gunicorn)

---

## 🧠 Key Concepts

- Django class-based views  
- Slug-based routing  
- Template partials (`_stars.html`)  
- Context processors (dynamic navigation)  
- Click tracking system  
- JSON fixtures (`loaddata`)  
- Static & media file handling  
- Responsive UI patterns  

---

## ⚙️ Local Setup

```bash
git clone https://github.com/mattywebdev/affiliate-site.git
cd affiliate-site

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Add your own DJANGO_SECRET_KEY value before deploying

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
---

## 🚀 Deployment (simplified)

```bash
git pull origin main
source venv/bin/activate
python manage.py collectstatic --noinput
systemctl restart gunicorn
```
## 🔮 Future Improvements

- Amazon API integration  
- User accounts & saved products
- Product comparison tool
- Pagination / infinite scroll
- PostgreSQL migration for production-scale data
- SEO improvements (structured data, sitemap)  

---

## 👨‍💻 Author

**Mateusz Obstawski**  
🔗 https://github.com/mattywebdev  
🔗 https://www.linkedin.com/in/mateusz-obstawski-9a355ba0/

---

## 💡 Notes

This project is part of my transition into a professional web development career, focusing on real-world, production-ready applications.


## License

Copyright © 2026 Mateusz Obstawski. All rights reserved.

This project is publicly visible for portfolio and review purposes only.
No permission is granted to copy, modify, redistribute, or use this code commercially without written permission.
