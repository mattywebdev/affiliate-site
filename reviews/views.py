from itertools import product
from multiprocessing import context
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from .models import Product, Category, Article, Click
from django.http import HttpResponseRedirect
from django.db.models import F, Count
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.db.models.functions import TruncDate


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
    return render(request, 'reviews/category_detail.html', {'category': category, 'products': products})

def affiliate_redirect(request, slug):
    product = get_object_or_404(Product, slug=slug)

    # 1) store raw click event
    Click.objects.create(
        product=product,
        ip_address=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],  # keep it reasonable
    )

    # 2) keep fast counter for sorting/leaderboards
    Product.objects.filter(pk=product.pk).update(clicks=F("clicks") + 1)

    return HttpResponseRedirect(product.affiliate_link)

class TopProductsView(ListView):
    model = Product
    template_name = "reviews/top_products.html"
    context_object_name = "products"

    def get_queryset(self):
        return Product.objects.order_by("-clicks")[:5]
    
class ArticleListView(ListView):
    model = Article
    template_name = "reviews/article_list.html"
    context_object_name = "articles"
    paginate_by = 10

    def get_queryset(self):
        qs = Article.objects.select_related("category").order_by("-created_at")

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
        context["categories"] = Category.objects.all()
        return context
    
@staff_member_required
def analytics_dashboard(request):
    # timeframe selector: ?days=7 or ?days=30
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

    return render(
        request,
        "reviews/analytics.html",
        {
            "days": days_int,
            "top_products": top_products,
            "clicks_per_day": clicks_per_day,
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
            .order_by("-created_at")[:6]
        )

        # Categories for “Browse by category”
        context["all_categories"] = Category.objects.all()

        return context