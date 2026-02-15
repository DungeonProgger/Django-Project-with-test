from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from catalog.models import Cheese, CheeseType, Batch, BatchItem
from decimal import Decimal

User = get_user_model()


class BatchTests(TestCase):
    def setUp(self):
        # Создаём пользователей с разными ролями
        self.admin = User.objects.create_user(
            username="admin", password="pass", role="admin"
        )
        self.manager = User.objects.create_user(
            username="manager", password="pass", role="sales_manager"
        )
        self.product_manager = User.objects.create_user(
            username="prodman", password="pass", role="product_manager"
        )
        self.guest_client = Client()

        self.admin_client = Client()
        self.admin_client.login(username="admin", password="pass")

        self.manager_client = Client()
        self.manager_client.login(username="manager", password="pass")

        self.product_manager_client = Client()
        self.product_manager_client.login(username="prodman", password="pass")

        # Создаём сыр и тип сыра
        self.cheese_type = CheeseType.objects.create(name="Мягкий")
        self.cheese = Cheese.objects.create(
            name="Бринза",
            price=100,
            price_small_opt=70,
            min_qty_small_opt=5,
            price_big_opt=50,
            min_qty_big_opt=10,
            weight=100,
            cheese_type=self.cheese_type,
            in_stock=True,
            production_date="2023-01-01",
        )

        # Создаём партию менеджера
        self.batch = Batch.objects.create(manager=self.manager)

    def test_guest_can_view_batches(self):
        url = reverse("batch_list")
        response = self.guest_client.get(url)
        self.assertIn(response.status_code, [302, 403])  # редирект или запрет

        url = reverse("batch_detail", args=[self.batch.id])
        response = self.guest_client.get(url)
        self.assertIn(response.status_code, [302, 403])

    def test_guest_cannot_create_batch(self):
        url = reverse("batch_create")
        response = self.guest_client.get(url)
        self.assertNotEqual(response.status_code,
                            200)  # 302 редирект на логин или 403

    def test_manager_can_create_and_edit_batch(self):
        # Создание партии
        url = reverse("batch_create")
        response = self.manager_client.get(url)
        self.assertEqual(response.status_code, 302)  # редирект после создания

        # Добавление товара
        url = reverse("batch_add_item", args=[self.batch.id])
        response = self.manager_client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.manager_client.post(
            url,
            data={
                "cheese": self.cheese.id,
                "quantity": 7,
            },
        )
        self.assertEqual(response.status_code,
                         302)  # редирект после добавления

        # Проверяем, что товар добавлен и цена корректна с учётом скидки
        item = BatchItem.objects.get(batch=self.batch, cheese=self.cheese)
        self.assertEqual(item.quantity, 7)
        self.assertEqual(item.unit_price, 70)  # Цена мелкий опт

    def test_only_owner_can_edit_batch(self):
        other_batch = Batch.objects.create(manager=self.product_manager)
        url = reverse("batch_detail", args=[other_batch.id])

        response = self.manager_client.get(url)
        self.assertEqual(response.status_code,
                         403)  # Нет доступа к чужой партии

    def test_total_price_and_discount_calculation(self):
        BatchItem.objects.create(
            batch=self.batch, cheese=self.cheese, quantity=3
        )  # по базовой цене 100
        BatchItem.objects.create(
            batch=self.batch, cheese=self.cheese, quantity=7
        )  # мелкий опт 70

        total_base = self.batch.total_base_price
        total_price = self.batch.total_price
        discount_percent = self.batch.total_discount_percent

        self.assertEqual(total_base, 100 * 3 + 100 * 7)  # 1000
        self.assertEqual(total_price, 100 * 3 + 70 * 7)  # 790
        expected_discount = (
            (Decimal("1000") - Decimal("790")) /
            Decimal("1000") * Decimal("100")
        )
        self.assertAlmostEqual(
            float(discount_percent), float(expected_discount), places=2
        )
