from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import re


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, related_name='products', null=True, blank=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    affiliate_link = models.URLField()
    image = models.ImageField(upload_to="products/", null=True, blank=True)
    clicks = models.PositiveIntegerField(default=0)

    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)

    # NEW ✅
    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text="0.0 to 5.0 (use .5 for half stars, e.g. 4.5)"
    )
    pros = models.TextField(blank=True, help_text="One pro per line")
    cons = models.TextField(blank=True, help_text="One con per line")

    # ✅ Amazon-ready fields
    asin = models.CharField(max_length=10, blank=True, db_index=True, help_text="10-char Amazon ASIN")
    amazon_image_url = models.URLField(blank=True, help_text="Set by API later (do not upload Amazon images yourself)")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Optional: try to extract ASIN automatically from affiliate_link if asin is empty
        if not self.asin and self.affiliate_link:
            m = re.search(r"/dp/([A-Z0-9]{10})|/gp/product/([A-Z0-9]{10})|asin=([A-Z0-9]{10})", self.affiliate_link)
            if m:
                self.asin = next(g for g in m.groups() if g).upper()
        super().save(*args, **kwargs)
    
class Article(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name="articles",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    excerpt = models.TextField(blank=True)
    content = models.TextField()
    products = models.ManyToManyField(Product, blank=True, related_name="articles")
    created_at = models.DateTimeField(auto_now_add=True)
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)

    def __str__(self):
        return self.title
    
class Click(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="click_events")
    created_at = models.DateTimeField(auto_now_add=True)

    # optional analytics (nice to have)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    def __str__(self):
        return f"{self.product.name} @ {self.created_at}"