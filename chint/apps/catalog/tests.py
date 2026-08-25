import uuid

from django.test import TestCase

from apps.catalog.models import Category, Product


class CategoryModelTest(TestCase):
    """Category model routed to the 'catalog' database."""

    # catalog models live in a separate DB (see config/db_router.py)
    databases = {"default", "catalog"}

    def test_str_returns_name(self):
        category = Category.objects.create(name="Circuit Breakers")
        self.assertEqual(str(category), "Circuit Breakers")

    def test_category_gets_uuid_pk(self):
        category = Category.objects.create(name="Relays")
        self.assertIsInstance(category.id, uuid.UUID)

    def test_parent_child_relation(self):
        parent = Category.objects.create(name="Low Voltage")
        child = Category.objects.create(name="Modular Devices", parent=parent)
        self.assertEqual(child.parent, parent)
        self.assertIn(child, parent.children.all())


class ProductModelTest(TestCase):
    """Product model with vendor code and category relation."""

    databases = {"default", "catalog"}

    def test_str_contains_vendor_code_and_name(self):
        product = Product.objects.create(
            id=uuid.uuid4(),
            vendor_code="NB1-63",
            name="Miniature Circuit Breaker",
            full_name="Miniature Circuit Breaker NB1-63",
            short_name="MCB NB1-63",
            raw={},
        )
        self.assertIn("NB1-63", str(product))
        self.assertIn("Miniature Circuit Breaker", str(product))

    def test_product_belongs_to_category(self):
        category = Category.objects.create(name="Breakers")
        product = Product.objects.create(
            id=uuid.uuid4(),
            category=category,
            vendor_code="NXB-63",
            name="Breaker",
            full_name="Breaker NXB-63",
            short_name="NXB",
            raw={},
        )
        self.assertEqual(product.category.name, "Breakers")
