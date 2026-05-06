import re
import markdown as md

from django import template
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string

from reviews.models import Product

register = template.Library()


PRODUCT_CARD_PATTERN  = re.compile(r"\[product:([a-zA-Z0-9_-]+)\]")
PRODUCT_IMAGE_PATTERN = re.compile(r"\[product_image:([a-zA-Z0-9_-]+)\]")
PRODUCT_BUTTON_PATTERN = re.compile(r"\[product_button:([a-zA-Z0-9_-]+)\]")
PRODUCT_PRICE_PATTERN = re.compile(r"\[product_price:([a-zA-Z0-9_-]+)\]")

def replace_product_buttons(text):
    def repl(match):
        slug = match.group(1)
        product = get_product_by_slug(slug)

        if not product:
            return f"<p><strong>Missing product button:</strong> {slug}</p>"

        return render_to_string(
            "reviews/includes/inline_product_button.html",
            {"product": product},
        )

    return PRODUCT_BUTTON_PATTERN.sub(repl, text)

def replace_product_cards(text):
    def repl(match):
        slug = match.group(1)
        product = get_product_by_slug(slug)

        if not product:
            return f"<p><strong>Missing product:</strong> {slug}</p>"

        return render_to_string(
            "reviews/includes/inline_product_card.html",
            {"product": product},
        )

    return PRODUCT_CARD_PATTERN.sub(repl, text)


@register.filter
def markdownify(text):
    if not text:
        return ""

    text = replace_product_images(text)
    text = replace_product_buttons(text)
    text = replace_product_cards(text)
    text = replace_product_prices(text)

    html = md.markdown(
        text,
        extensions=["extra"],
    )
    return mark_safe(html)

def get_product_by_slug(slug):
    try:
        return Product.objects.get(slug=slug)
    except Product.DoesNotExist:
        return None
    

def replace_product_images(text):
    def repl(match):
        slug = match.group(1)
        product = get_product_by_slug(slug)

        if not product:
            return f"<p><strong>Missing product image:</strong> {slug}</p>"

        return render_to_string(
            "reviews/includes/inline_product_image.html",
            {"product": product},
        )

    return PRODUCT_IMAGE_PATTERN.sub(repl, text)

def replace_product_prices(text):
    def repl(match):
        slug = match.group(1)
        product = get_product_by_slug(slug)

        if not product:
            return f"<strong>Price unavailable</strong>"

        if product.price:
            price_str = f"~£{product.price:.0f}"
            return f'<span class="product-price">{price_str}</span>'
        else:
            return "Price not set"

    return PRODUCT_PRICE_PATTERN.sub(repl, text)