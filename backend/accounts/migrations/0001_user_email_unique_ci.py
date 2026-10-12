from django.conf import settings
from django.db import migrations
from django.db.models import Count
from django.db.models.functions import Lower


INDEX_NAME = "auth_user_email_ci_uniq"


def create_unique_email_index(apps, schema_editor):
    user_app, user_model = settings.AUTH_USER_MODEL.split(".")
    User = apps.get_model(user_app, user_model)

    duplicate_emails_exist = (
        User.objects.exclude(email="")
        .annotate(normalized_email=Lower("email"))
        .values("normalized_email")
        .annotate(user_count=Count("pk"))
        .filter(user_count__gt=1)
        .exists()
    )
    if duplicate_emails_exist:
        raise RuntimeError(
            "Cannot enforce unique email addresses: case-insensitive duplicates "
            "already exist. Resolve them before applying this migration."
        )

    table = schema_editor.quote_name(User._meta.db_table)
    email_column = schema_editor.quote_name(User._meta.get_field("email").column)
    index = schema_editor.quote_name(INDEX_NAME)
    schema_editor.execute(
        f"CREATE UNIQUE INDEX {index} ON {table} (LOWER({email_column})) "
        f"WHERE {email_column} <> ''"
    )


def remove_unique_email_index(apps, schema_editor):
    index = schema_editor.quote_name(INDEX_NAME)
    schema_editor.execute(f"DROP INDEX {index}")


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(
            create_unique_email_index,
            remove_unique_email_index,
        ),
    ]
