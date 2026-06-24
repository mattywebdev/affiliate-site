from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from .models import Product, Category, Article, Click
from django.http import HttpResponseRedirect
from django.db.models import F, Count
from django.utils import timezone
from django.db.models.functions import TruncDate
from django.urls import reverse
from .utils.geo import get_country_code
from .seo import (
    absolute_url,
    article_schema,
    clean_description,
    collection_schema,
    organization_schema,
    product_schema,
    sitemap_date,
    website_schema,
)


AMAZON_STORES = {
    "GB": ("amazon.co.uk", "mattydev-21"),
    "PL": ("amazon.pl", "mattydev04-21"),
    "DE": ("amazon.de", "your-german-tag"),
}


def get_client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")


def build_amazon_url(country_code, asin):
    domain, tag = AMAZON_STORES.get(country_code, AMAZON_STORES["GB"])
    return f"https://www.{domain}/dp/{asin}/?tag={tag}"

def affiliate_redirect(request, slug):
    product = get_object_or_404(Product, slug=slug)

    ip_address = get_client_ip(request)

    country_code = request.GET.get(
        "country",
        get_country_code(ip_address)
    ).upper()

    Click.objects.create(
        product=product,
        ip_address=ip_address,
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
    )

    Product.objects.filter(pk=product.pk).update(clicks=F("clicks") + 1)

    if product.asin:
        url = build_amazon_url(country_code, product.asin)
    else:
        url = product.affiliate_link

    return HttpResponseRedirect(url)

class ProductListView(ListView):
    model = Product
    template_name = 'reviews/product_list.html'
    context_object_name = 'products'
    paginate_by = 6

    def get_queryset(self):
        qs = Product.objects.select_related('category').all()

        # search
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(name__icontains=q)

        # category filter
        cat = self.request.GET.get("cat")
        if cat:
            qs = qs.filter(category__slug=cat)

        # sorting
        sort = self.request.GET.get("sort", "name")
        allowed = {"name", "-name", "price", "-price", "-clicks"}
        if sort not in allowed:
            sort = "name"

        return qs.order_by(sort)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sort"] = self.request.GET.get("sort", "name")
        context["q"] = self.request.GET.get("q", "")
        context["cat"] = self.request.GET.get("cat", "")
        context["meta_title"] = "Best Monitor Picks and Buying Guides"
        context["meta_description"] = "Compare curated monitor picks by category, rating, price, pros, and cons."
        context["canonical_url"] = absolute_url(reverse("reviews:product_list"))
        context["json_ld_data"] = collection_schema(
            "Best Monitor Picks and Buying Guides",
            context["meta_description"],
            context["canonical_url"],
            context["products"],
        )
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'reviews/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        context["meta_title"] = product.meta_title or product.name
        context["meta_description"] = product.meta_description or (product.description or "")[:150]
        context["canonical_url"] = absolute_url(product.get_absolute_url())
        context["og_type"] = "product"
        context["json_ld_data"] = product_schema(product)
        context["related_articles"] = getattr(self.object, "articles", []).all() if hasattr(self.object, "articles") else []
        context["categories"] = Category.objects.all()
        context["related_products"] = (
            Product.objects
            .filter(category=self.object.category)
            .exclude(pk=self.object.pk)[:4]
        )
        return context

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.all()
    meta_title = f"Best {category.name} Monitor Picks"
    meta_description = f"Compare curated {category.name.lower()} monitor picks with prices, pros, cons, and quick buying advice."
    canonical_url = absolute_url(reverse("reviews:category_detail", args=[category.slug]))
    return render(request, 'reviews/category_detail.html', {
        'category': category,
        'products': products,
        "meta_title": meta_title,
        "meta_description": meta_description,
        "canonical_url": canonical_url,
        "json_ld_data": collection_schema(meta_title, meta_description, canonical_url, products),
    })


class TopProductsView(ListView):
    model = Product
    template_name = "reviews/top_products.html"
    context_object_name = "products"

    def get_queryset(self):
        return Product.objects.order_by("-clicks")[:6]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["meta_title"] = "Top Rated Monitor Picks"
        context["meta_description"] = "See the monitor picks getting the most attention, with quick prices, ratings, and buying links."
        context["canonical_url"] = absolute_url(reverse("reviews:top_products"))
        context["json_ld_data"] = collection_schema(
            context["meta_title"],
            context["meta_description"],
            context["canonical_url"],
            context["products"],
        )
        return context
    
class ArticleListView(ListView):
    model = Article
    template_name = "reviews/article_list.html"
    context_object_name = "articles"
    paginate_by = 10

    def get_queryset(self):
        qs = Article.objects.select_related("category").order_by("-updated_at", "-created_at")

        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(title__icontains=q)

        cat = self.request.GET.get("cat")
        if cat:
            qs = qs.filter(category__slug=cat)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "")
        context["cat"] = self.request.GET.get("cat", "")
        context["meta_title"] = "Monitor Buying Guides and Reviews"
        context["meta_description"] = "Read practical monitor buying guides for gaming, office work, budget setups, and home productivity."
        context["canonical_url"] = absolute_url(reverse("reviews:article_list"))
        context["json_ld_data"] = collection_schema(
            context["meta_title"],
            context["meta_description"],
            context["canonical_url"],
            context["articles"],
        )
        return context


class ArticleDetailView(DetailView):
    model = Article
    template_name = "reviews/article_detail.html"
    context_object_name = "article"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.object
        context["meta_title"] = article.meta_title or article.title
        context["meta_description"] = article.meta_description or (article.excerpt or "")[:150]
        context["canonical_url"] = absolute_url(article.get_absolute_url())
        context["og_type"] = "article"
        if article.featured_image:
            context["og_image"] = absolute_url(article.featured_image.url)
        context["json_ld_data"] = article_schema(article)
        context["categories"] = Category.objects.all()
        return context
    
# Temporarily public for portfolio/demo purposes
# @staff_member_required
def analytics_dashboard(request):
    days = request.GET.get("days", "7")
    try:
        days_int = int(days)
    except ValueError:
        days_int = 7

    now = timezone.now()
    since = now - timezone.timedelta(days=days_int)

    clicks_qs = Click.objects.filter(created_at__gte=since).select_related("product")

    # 1) Top products
    top_products = (
        clicks_qs.values("product__id", "product__name", "product__slug")
        .annotate(clicks=Count("id"))
        .order_by("-clicks")[:20]
    )

    # 2) Clicks per day
    clicks_per_day = (
        clicks_qs.annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(clicks=Count("id"))
        .order_by("day")
    )

    total_clicks = sum(p['clicks'] for p in top_products)

    return render(
        request,
        "reviews/analytics.html",
        {
            "days": days_int,
            "top_products": top_products,
            "clicks_per_day": clicks_per_day,
            "total_clicks": total_clicks,
            "meta_title": "Affiliate Analytics",
            "meta_description": "Private affiliate click analytics dashboard.",
            "meta_robots": "noindex,nofollow",
        },
    )

class HomePageView(TemplateView):
    template_name = "reviews/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Top rated products (with ratings)
        context["top_rated"] = (
            Product.objects.select_related("category")
            .filter(rating__gt=0)
            .order_by("-rating", "-clicks")[:6]
        )

        # Most clicked products (social proof)
        context["most_clicked"] = (
            Product.objects.select_related("category")
            .order_by("-clicks")[:6]
        )

        # Latest articles (SEO + authority + internal links)
        context["latest_articles"] = (
            Article.objects.select_related("category")
            .order_by("-updated_at", "-created_at")[:6]
        )

        # Categories for “Browse by category”
        context["all_categories"] = Category.objects.all()
        context["meta_title"] = "Matty Dev Deals - Practical Monitor Buying Guides"
        context["meta_description"] = "Fast, practical monitor buying guides with curated picks, ratings, pros, cons, and affiliate links."
        context["canonical_url"] = absolute_url(reverse("reviews:home"))
        context["json_ld_data"] = [website_schema(), organization_schema()]

        return context
    
def contact(request):
    return render(request, "reviews/contact.html", {
        "meta_title": "Contact Matty Dev Deals",
        "meta_description": "Contact Matty Dev Deals about buying guides, affiliate recommendations, or site feedback.",
        "canonical_url": absolute_url(reverse("reviews:contact")),
        "json_ld_data": organization_schema(),
    })

def privacy(request):
    return render(request, "reviews/privacy.html", {
        "meta_title": "Privacy Policy - Matty Dev Deals",
        "meta_description": "Privacy and affiliate disclosure information for Matty Dev Deals.",
        "canonical_url": absolute_url(reverse("reviews:privacy")),
    })


def robots_txt(request):
    return render(request, "robots.txt", {"site_url": absolute_url()}, content_type="text/plain")


def sitemap_xml(request):
    urls = [
        {
            "loc": absolute_url(reverse("reviews:home")),
            "lastmod": sitemap_date(timezone.now()),
            "changefreq": "weekly",
            "priority": "1.0",
        },
        {
            "loc": absolute_url(reverse("reviews:product_list")),
            "lastmod": sitemap_date(timezone.now()),
            "changefreq": "weekly",
            "priority": "0.9",
        },
        {
            "loc": absolute_url(reverse("reviews:article_list")),
            "lastmod": sitemap_date(timezone.now()),
            "changefreq": "weekly",
            "priority": "0.9",
        },
        {
            "loc": absolute_url(reverse("reviews:top_products")),
            "lastmod": sitemap_date(timezone.now()),
            "changefreq": "weekly",
            "priority": "0.8",
        },
    ]

    for category in Category.objects.all():
        urls.append({
            "loc": absolute_url(reverse("reviews:category_detail", args=[category.slug])),
            "lastmod": sitemap_date(timezone.now()),
            "changefreq": "weekly",
            "priority": "0.8",
        })

    for product in Product.objects.all():
        urls.append({
            "loc": absolute_url(product.get_absolute_url()),
            "lastmod": sitemap_date(product.updated_at),
            "changefreq": "weekly",
            "priority": "0.7",
        })

    for article in Article.objects.all():
        urls.append({
            "loc": absolute_url(article.get_absolute_url()),
            "lastmod": sitemap_date(article.updated_at),
            "changefreq": "monthly",
            "priority": "0.75",
        })

    return render(request, "sitemap.xml", {"urls": urls}, content_type="application/xml")
