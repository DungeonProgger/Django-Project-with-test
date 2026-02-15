from django.test import TestCase
from django.urls import reverse
from catalog.models import Cheese, CheeseType


class TestRoutes(TestCase):
    def setUp(self):
        # Создаем тип сыра
        cheese_type = CheeseType.objects.create(name="Твердый")

        # Создаем сыр
        self.cheese = Cheese.objects.create(
            name="Чеддер",
            price=100,
            weight=1.5,
            cheese_type=cheese_type,
            production_date="2024-01-01",
        )

        print(f"Создан сыр с ID: {self.cheese.id}")

    def test_cheese_detail_route(self):
        all_cheeses = Cheese.objects.all()
        print(f"Все сыры в базе данных: "
              f"{[cheese.id for cheese in all_cheeses]}")

        # Печатаем ID перед запросом
        print(f"Запрос к объекту с ID: {self.cheese.id}")

        # Ответ от сервера
        response = self.client.get(reverse("cheese_detail",
                                           args=[self.cheese.id]))

        # self.assertEqual(response.status_code, 200)

        self.assertContains(response, "Чеддер")


class TestCheeseSorting(TestCase):
    def setUp(self):
        # Создание типов сыра
        cheese_type1 = CheeseType.objects.create(name="Твердый")
        cheese_type2 = CheeseType.objects.create(name="Мягкий")

        # Создание нескольких сыра с разными аттрибутами для теста
        Cheese.objects.create(
            name="Чеддер",
            price=100,
            weight=1.5,
            cheese_type=cheese_type1,
            production_date="2024-01-01",
        )
        Cheese.objects.create(
            name="Бри",
            price=150,
            weight=0.5,
            cheese_type=cheese_type2,
            production_date="2024-02-01",
        )
        Cheese.objects.create(
            name="Гауда",
            price=120,
            weight=1.2,
            cheese_type=cheese_type1,
            production_date="2024-01-01",
        )

    def test_sort_by_name(self):
        # Получаем товары, отсортированные по имени
        response = self.client.get(reverse("cheese_list") + "?order_by=name")
        cheeses = response.context["cheeses"]
        # Проверяем правильность сортировки
        self.assertEqual(cheeses[0].name, "Бри")
        self.assertEqual(cheeses[1].name, "Гауда")
        self.assertEqual(cheeses[2].name, "Чеддер")

    def test_sort_by_price(self):
        # Получаем товары, отсортированные по цене
        response = self.client.get(reverse("cheese_list") + "?order_by=price")
        cheeses = response.context["cheeses"]
        # Проверяем правильность сортировки
        self.assertEqual(cheeses[0].name, "Чеддер")
        self.assertEqual(cheeses[1].name, "Гауда")
        self.assertEqual(cheeses[2].name, "Бри")

    def test_sort_by_weight(self):
        # Получаем товары, отсортированные по весу
        response = self.client.get(reverse("cheese_list") + "?order_by=weight")
        cheeses = response.context["cheeses"]
        # Проверяем правильность сортировки
        self.assertEqual(cheeses[0].name, "Бри")
        self.assertEqual(cheeses[1].name, "Гауда")
        self.assertEqual(cheeses[2].name, "Чеддер")

    def test_filter_by_cheese_type(self):
        # Фильтрация по типу сыра (например, "Твердый")
        response = self.client.get(
            reverse("cheese_list") + "?type=1"
        )  # 1 - это ID типа "Твердый"
        cheeses = response.context["cheeses"]

        # Проверяем, что фильтруются только сыры типа "Твердый"
        self.assertEqual(len(cheeses), 2)  # Ожидаем 2 сыра с типом "Твердый"
        self.assertTrue(all(cheese.cheese_type.name ==
                            "Твердый" for cheese in cheeses))

    def test_filter_by_cheese_type_mixed(self):
        # Фильтрация по типу сыра (например, "Мягкий")
        response = self.client.get(
            reverse("cheese_list") + "?type=2"
        )  # 2 - это ID типа "Мягкий"
        cheeses = response.context["cheeses"]

        # Проверяем, что фильтруется только 1 сыр с типом "Мягкий"
        self.assertEqual(len(cheeses), 1)
        self.assertEqual(cheeses[0].name, "Бри")
