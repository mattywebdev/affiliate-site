from django.core.management.base import BaseCommand
from reviews.models import Product
from reviews.services.amazon import fetch_product_data_by_asin

class Command(BaseCommand):
    help = "Fetch Amazon image URLs for products with an ASIN and store them in amazon_image_url."

    def add_arguments(self, parser):
        parser.add_argument("--only-missing", action="store_true", help="Only update products missing amazon_image_url")
        parser.add_argument("--limit", type=int, default=0, help="Limit number of products processed")

    def handle(self, *args, **options):
        qs = Product.objects.exclude(asin="").exclude(asin__isnull=True)

        if options["only_missing"]:
            qs = qs.filter(amazon_image_url="")

        if options["limit"]:
            qs = qs[: options["limit"]]

        updated = 0
        for p in qs:
            data = fetch_product_data_by_asin(p.asin)
            if data.image_url and data.image_url != p.amazon_image_url:
                p.amazon_image_url = data.image_url
                p.save(update_fields=["amazon_image_url"])
                updated += 1
                self.stdout.write(self.style.SUCCESS(f"Updated {p.slug} -> {data.image_url}"))
            else:
                self.stdout.write(f"Skipped {p.slug} (no image returned)")

        self.stdout.write(self.style.WARNING(f"Done. Updated: {updated}"))
