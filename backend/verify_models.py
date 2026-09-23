import os
import sys
import django
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()
    from django.contrib.auth import get_user_model
    from products.models import Category, Product
    User = get_user_model()
    # Clean up previous test data if any
    User.objects.filter(username='seller_test').delete()
    Category.objects.filter(name='TestCategory').delete()
    Product.objects.filter(sku__in=['SKU123','SKU124','SKU125','SKU_DUP']).delete()

    # Create test user
    user = User.objects.create_user(username='seller_test', password='test')
    # Create category
    cat = Category.objects.create(name='TestCategory')
    # Valid product
    prod = Product(
        seller=user,
        category=cat,
        name='ValidProduct',
        sku='SKU123',
        price=199.99,
        stock=10,
    )
    try:
        prod.full_clean()
        prod.save()
        print('Valid product created successfully')
    except ValidationError as e:
        print('Unexpected ValidationError for valid product:', e)

    # Negative price
    bad_price = Product(
        seller=user,
        category=cat,
        name='BadPrice',
        sku='SKU124',
        price=-5,
        stock=5,
    )
    try:
        bad_price.full_clean()
        print('Error: Negative price passed validation')
    except ValidationError as e:
        print('ValidationError for negative price as expected:', e)

    # Negative stock
    bad_stock = Product(
        seller=user,
        category=cat,
        name='BadStock',
        sku='SKU125',
        price=10,
        stock=-1,
    )
    try:
        bad_stock.full_clean()
        print('Error: Negative stock passed validation')
    except ValidationError as e:
        print('ValidationError for negative stock as expected:', e)

    # Duplicate SKU
    dup = Product(
        seller=user,
        category=cat,
        name='DupSKU',
        sku='SKU123',
        price=20,
        stock=5,
    )
    try:
        dup.full_clean()
        dup.save()
        print('Error: Duplicate SKU allowed')
    except (IntegrityError, ValidationError) as e:
        print('IntegrityError or ValidationError for duplicate SKU as expected:', e)

    # on_delete PROTECT test for Category
    try:
        cat.delete()
        print('Error: Category deletion succeeded despite PROTECT')
    except Exception as e:
        print('ProtectedError on deleting Category as expected:', e)

    # on_delete PROTECT test for User
    try:
        user.delete()
        print('Error: User deletion succeeded despite PROTECT')
    except Exception as e:
        print('ProtectedError on deleting User as expected:', e)

if __name__ == '__main__':
    main()
