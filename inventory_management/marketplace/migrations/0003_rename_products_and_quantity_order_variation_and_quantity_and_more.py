# Generated by Django 4.1.4 on 2022-12-13 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "marketplace",
            "0002_remove_product_number_in_stock_remove_product_price_and_more",
        ),
    ]

    operations = [
        migrations.RenameField(
            model_name="order",
            old_name="products_and_quantity",
            new_name="variation_and_quantity",
        ),
        migrations.RenameField(
            model_name="variation",
            old_name="name",
            new_name="type",
        ),
        migrations.RemoveField(
            model_name="product",
            name="labels",
        ),
        migrations.AddField(
            model_name="order",
            name="payment_reference",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="variation",
            name="var_id",
            field=models.CharField(default=123, max_length=15),
            preserve_default=False,
        ),
    ]