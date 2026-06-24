from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
import re


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("reviews:product_detail", args=[self.slug])

class Product(models.Model):
    VISUAL_MONITOR = "monitor"
    VISUAL_LAPTOP = "laptop"
    VISUAL_STORAGE = "storage"
    VISUAL_ACCESSORY = "accessory"
    VISUAL_TYPE_CHOICES = [
        (VISUAL_MONITOR, "Monitor"),
        (VISUAL_LAPTOP, "Laptop"),
        (VISUAL_STORAGE, "Storage"),
        (VISUAL_ACCESSORY, "Accessory"),
    ]

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

    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text="0.0 to 5.0 (use .5 for half stars, e.g. 4.5)"
    )
    pros = models.TextField(blank=True, help_text="One pro per line")
    cons = models.TextField(blank=True, help_text="One con per line")

    asin = models.CharField(max_length=10, blank=True, db_index=True, help_text="10-char Amazon ASIN")
    amazon_image_url = models.URLField(blank=True, help_text="Set by API later (do not upload Amazon images yourself)")
    visual_type = models.CharField(max_length=30, choices=VISUAL_TYPE_CHOICES, default=VISUAL_MONITOR)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def pros_list(self):
        return [line.strip() for line in self.pros.splitlines() if line.strip()]

    @property
    def cons_list(self):
        return [line.strip() for line in self.cons.splitlines() if line.strip()]

    @property
    def visual_specs(self):
        text = f"{self.name} {self.description}".lower()
        specs = []

        size_match = re.search(r'(\d{2}(?:\.\d)?)\s*(?:["”]|-?inch| inch)', text)
        if size_match:
            specs.append(f'{size_match.group(1)}"')

        if "4k" in text:
            specs.append("4K")
        elif "qhd" in text or "1440p" in text or "2560x1440" in text:
            specs.append("QHD")
        elif "1080p" in text or "full hd" in text:
            specs.append("FHD")

        refresh_match = re.search(r"(\d{2,3})\s*hz", text)
        if refresh_match:
            specs.append(f"{refresh_match.group(1)}Hz")

        for panel in ("mini-led", "ips", "va", "oled", "usb-c"):
            if panel in text:
                specs.append(panel.upper())

        seen = set()
        return [spec for spec in specs if not (spec in seen or seen.add(spec))][:4]

    @property
    def visual_tagline(self):
        if self.visual_type == self.VISUAL_LAPTOP:
            return "Laptop pick"
        if self.visual_type == self.VISUAL_STORAGE:
            return "Storage pick"
        if self.visual_type == self.VISUAL_ACCESSORY:
            return "Accessory pick"
        if self.category and self.category.slug == "gaming":
            return "Gaming display"
        if self.category and self.category.slug == "office":
            return "Workstation display"
        if self.category and self.category.slug == "budget":
            return "Value display"
        return "Monitor pick"

    def save(self, *args, **kwargs):
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
    featured_image = models.ImageField(upload_to="articles/", null=True, blank=True)
    products = models.ManyToManyField(Product, blank=True, related_name="articles")
    verdict = models.TextField(blank=True)
    best_for = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("reviews:article_detail", args=[self.slug])
    
class Click(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="click_events")
    created_at = models.DateTimeField(auto_now_add=True)

    # optional analytics (nice to have)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    def __str__(self):
        return f"{self.product.name} @ {self.created_at}"
