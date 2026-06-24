import json
from datetime import date
from decimal import Decimal

from django.conf import settings
from django.urls import reverse
from django.utils.html import strip_tags


def absolute_url(path=""):
    if not path:
        return settings.SITE_URL
    if path.startswith("http://") or path.startswith("https://"):
        return path
    if not path.startswith("/"):
        path = f"/{path}"
    return f"{settings.SITE_URL}{path}"


def clean_description(value, fallback=None, limit=155):
    text = strip_tags(value or fallback or settings.SITE_DESCRIPTION)
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return f"{text[: limit - 1].rsplit(' ', 1)[0]}..."


def json_ld(data):
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def product_schema(product):
    url = absolute_url(reverse("reviews:product_detail", args=[product.slug]))
    data = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": product.name,
        "description": clean_description(product.description, limit=240),
        "url": url,
        "category": product.category.name if product.category else "Affiliate product",
        "offers": {
            "@type": "Offer",
            "url": url,
            "priceCurrency": "GBP",
            "price": str(product.price),
            "availability": "https://schema.org/InStock",
            "itemCondition": "https://schema.org/NewCondition",
        },
    }

    if product.asin:
        data["sku"] = product.asin

    if product.amazon_image_url:
        data["image"] = [product.amazon_image_url]

    if product.rating and Decimal(product.rating) > 0:
        data["review"] = {
            "@type": "Review",
            "author": {
                "@type": "Person",
                "name": "Mateusz Obstawski",
            },
            "reviewRating": {
                "@type": "Rating",
                "ratingValue": str(product.rating),
                "bestRating": "5",
                "worstRating": "1",
            },
        }

    return data


def article_schema(article):
    url = absolute_url(reverse("reviews:article_detail", args=[article.slug]))
    data = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": article.title,
        "description": clean_description(article.excerpt, limit=180),
        "url": url,
        "datePublished": article.created_at.date().isoformat(),
        "dateModified": article.updated_at.date().isoformat(),
        "author": {
            "@type": "Person",
            "name": "Mateusz Obstawski",
        },
        "publisher": {
            "@type": "Organization",
            "name": settings.SITE_NAME,
            "url": settings.SITE_URL,
        },
    }

    if article.featured_image:
        data["image"] = [absolute_url(article.featured_image.url)]

    return data


def website_schema():
    return {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": settings.SITE_NAME,
        "url": settings.SITE_URL,
        "description": settings.SITE_DESCRIPTION,
        "potentialAction": {
            "@type": "SearchAction",
            "target": f"{settings.SITE_URL}{reverse('reviews:product_list')}?q={{search_term_string}}",
            "query-input": "required name=search_term_string",
        },
    }


def organization_schema():
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": settings.SITE_NAME,
        "url": settings.SITE_URL,
        "email": "hello@matty-dev.com",
        "contactPoint": {
            "@type": "ContactPoint",
            "email": "hello@matty-dev.com",
            "contactType": "customer support",
        },
    }


def collection_schema(name, description, url, items):
    return {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": name,
        "description": description,
        "url": url,
        "mainEntity": {
            "@type": "ItemList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": index,
                    "url": absolute_url(item.get_absolute_url()),
                    "name": item.name if hasattr(item, "name") else item.title,
                }
                for index, item in enumerate(items, start=1)
            ],
        },
    }


def sitemap_date(value):
    if not value:
        return date.today().isoformat()
    return value.date().isoformat()
