from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Product, Category
from django.http import HttpResponseRedirect
from django.db.models import F

class ProductListView(ListView):
    model = Product
    template_name = 'reviews/product_list.html'
    context_object_name = 'products'
    paginate_by = 6

    def get_queryset(self):
        qs = Product.objects.select_related('category').all()

        #search
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(name__icontains=q)

        #sorting
        sort = self.request.GET.get("sort", "name")
        
        allowed = {"name", "-name", "price", "-price"}
        if sort not in allowed:
            sort = "name"
        return qs.order_by(sort)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sort"] = self.request.GET.get("sort", "name")
        context["q"] = self.request.GET.get("q", "")
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'reviews/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        return context

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.all()
    return render(request, 'reviews/category_detail.html', {'category': category, 'products': products})

def affiliate_redirect(request, slug):
    product = get_object_or_404(Product, slug=slug)
    Product.objects.filter(pk=product.pk).update(clicks=F("clicks") + 1)
    return HttpResponseRedirect(product.affiliate_link)