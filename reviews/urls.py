from django.urls import path
from .views import ProductListView, ProductDetailView
from . import views

app_name = "reviews"

urlpatterns = [
    path("", ProductListView.as_view(), name="product_list"),
    path("category/<slug:slug>/", views.category_detail, name="category_detail"),
    path("go/<slug:slug>/", views.affiliate_redirect, name="affiliate_redirect"),
    path("<slug:slug>/", ProductDetailView.as_view(), name="product_detail"),
]