from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone


def assign_existing_ownership_and_audits(apps, schema_editor):
    """Preserve products while converting shared legacy categories per seller."""
    Category = apps.get_model("products", "Category")
    Product = apps.get_model("products", "Product")

    for product in Product.objects.all().iterator():
        product.created_by_id = product.seller_id
        product.updated_by_id = product.seller_id
        product.save(update_fields=["created_by", "updated_by"])

    for category in Category.objects.all().iterator():
        if category.deleted_at is not None:
            continue

        seller_ids = list(
            Product.objects.filter(category_id=category.pk)
            .order_by("seller_id")
            .values_list("seller_id", flat=True)
            .distinct()
        )

        if not seller_ids:
            # Legacy empty categories have no reliable owner. Keep them for a
            # manual administrator decision, but application queries hide them.
            continue

        primary_seller_id = seller_ids[0]
        primary_category = Category.objects.filter(
            seller_id=primary_seller_id,
            name=category.name,
            deleted_at__isnull=True,
        ).exclude(pk=category.pk).first()

        if primary_category is not None:
            Product.objects.filter(
                category_id=category.pk,
                seller_id=primary_seller_id,
            ).update(category_id=primary_category.pk)
            category.seller_id = primary_seller_id
            category.created_by_id = primary_seller_id
            category.updated_by_id = primary_seller_id
            category.deleted_at = timezone.now()
            category.deleted_by_id = primary_seller_id
            category.save(
                update_fields=[
                    "seller",
                    "created_by",
                    "updated_by",
                    "deleted_at",
                    "deleted_by",
                ]
            )
        else:
            category.seller_id = primary_seller_id
            category.created_by_id = primary_seller_id
            category.updated_by_id = primary_seller_id
            category.save(
                update_fields=["seller", "created_by", "updated_by"]
            )

        for seller_id in seller_ids[1:]:
            duplicate = Category.objects.filter(
                seller_id=seller_id,
                name=category.name,
                deleted_at__isnull=True,
            ).first()
            if duplicate is None:
                duplicate = Category.objects.create(
                    seller_id=seller_id,
                    name=category.name,
                    created_by_id=seller_id,
                    updated_by_id=seller_id,
                )

            Product.objects.filter(
                category_id=category.pk,
                seller_id=seller_id,
            ).update(category_id=duplicate.pk)


def reverse_existing_ownership_and_audits(apps, schema_editor):
    # A reversible migration cannot safely merge seller-specific categories.
    # Keep the separated categories and clear only fields introduced here.
    Category = apps.get_model("products", "Category")
    Product = apps.get_model("products", "Product")

    Category.objects.update(
        seller=None,
        created_by=None,
        updated_by=None,
        deleted_at=None,
        deleted_by=None,
    )
    Product.objects.update(
        created_by=None,
        updated_by=None,
        deleted_at=None,
        deleted_by=None,
    )


class Migration(migrations.Migration):

    # The data migration updates products before their audit fields become
    # non-nullable. PostgreSQL must commit those trigger events first.
    atomic = False

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="created_categories",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="category",
            name="deleted_at",
            field=models.DateTimeField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="category",
            name="deleted_by",
            field=models.ForeignKey(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="deleted_categories",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="category",
            name="seller",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="categories",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="category",
            name="updated_by",
            field=models.ForeignKey(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="updated_categories",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="created_products",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="deleted_at",
            field=models.DateTimeField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="deleted_by",
            field=models.ForeignKey(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="deleted_products",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="updated_by",
            field=models.ForeignKey(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="updated_products",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="sku",
            field=models.CharField(max_length=100),
        ),
        migrations.RunPython(
            assign_existing_ownership_and_audits,
            reverse_existing_ownership_and_audits,
        ),
        migrations.AlterField(
            model_name="product",
            name="created_by",
            field=models.ForeignKey(
                editable=False,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="created_products",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="updated_by",
            field=models.ForeignKey(
                editable=False,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="updated_products",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddConstraint(
            model_name="category",
            constraint=models.UniqueConstraint(
                fields=("seller", "name"),
                condition=models.Q(deleted_at__isnull=True),
                name="unique_category_name_per_seller",
            ),
        ),
        migrations.AddConstraint(
            model_name="product",
            constraint=models.UniqueConstraint(
                fields=("seller", "sku"),
                condition=models.Q(deleted_at__isnull=True),
                name="unique_product_sku_per_seller",
            ),
        ),
    ]
