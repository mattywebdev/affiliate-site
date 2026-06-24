from django.db import migrations


def clear_legacy_product_images(apps, schema_editor):
    Product = apps.get_model("reviews", "Product")
    Product.objects.exclude(image="").update(image="")


class Migration(migrations.Migration):

    dependencies = [
        ("reviews", "0014_product_visual_type"),
    ]

    operations = [
        migrations.RunPython(clear_legacy_product_images, migrations.RunPython.noop),
    ]