from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class CheeseType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Cheese(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8,
                                decimal_places=2)  # цена за единицу

    price_small_opt = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Цена мелкий опт",
    )
    min_qty_small_opt = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name="Минимальное количество для мелкого опта"
    )

    price_big_opt = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Цена крупный опт",
    )
    min_qty_big_opt = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name="Минимальное количество для крупного опта"
    )

    weight = models.DecimalField(max_digits=6, decimal_places=2)
    cheese_type = models.ForeignKey(CheeseType, on_delete=models.CASCADE)
    in_stock = models.BooleanField(default=True)
    production_date = models.DateField()

    def __str__(self):
        return self.name


class User(AbstractUser):
    ROLE_CHOICES = [
        ("admin", "Администратор"),
        ("product_manager", "Товаровед"),
        ("sales_manager",
         "Менеджер по продажам"),
        ("guest", "Гость"),
    ]
    role = models.CharField(max_length=20,
                            choices=ROLE_CHOICES, default="guest")


class Batch(models.Model):
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="batches"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Партия #{self.id} менеджер: {self.manager.username}"

    @property
    def total_base_price(self):
        """Общая цена без скидок (базовая цена * количество)"""
        return sum(item.cheese.price *
                   item.quantity for item in self.items.all())

    @property
    def total_price_before_batch_discount(self):
        """Сумма по позициям с учётом скидок товаров"""
        return sum(item.total_price for item in self.items.all())

    @property
    def total_discount_amount(self):
        """Сумма скидки по позициям"""
        return self.total_base_price - self.total_price_before_batch_discount

    @property
    def total_discount_percent(self):
        """Общая скидка по позициям в партии в процентах"""
        base = self.total_base_price
        if base == 0:
            return 0
        discount = (base - self.total_price_before_batch_discount) / base * 100
        return round(discount, 2)

    @property
    def total_price(self):
        """Итоговая сумма партии с учётом скидок товаров"""
        return self.total_price_before_batch_discount


class BatchItem(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE,
                              related_name="items")
    cheese = models.ForeignKey(Cheese, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.cheese.name} x {self.quantity}"

    @property
    def unit_price(self):
        qty = self.quantity
        c = self.cheese
        # Проверяем крупный опт первым, чтобы применить максимальную скидку
        if (
            c.min_qty_big_opt
            and qty >= c.min_qty_big_opt
            and c.price_big_opt is not None
        ):
            return c.price_big_opt
        # Потом мелкий опт
        if (
            c.min_qty_small_opt
            and qty >= c.min_qty_small_opt
            and c.price_small_opt is not None
        ):
            return c.price_small_opt
        # Иначе базовая цена
        return c.price

    @property
    def total_price(self):
        return self.unit_price * self.quantity

    @property
    def discount_percent(self):
        base_price = self.cheese.price
        actual_price = self.unit_price
        if base_price == 0:
            return 0
        discount = (base_price - actual_price) / base_price * 100
        return round(discount, 2)
