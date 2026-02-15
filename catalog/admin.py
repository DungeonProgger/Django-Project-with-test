from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Cheese, CheeseType, User


admin.site.register(Cheese)
admin.site.register(CheeseType)


class UserAdmin(BaseUserAdmin):
    # Добавляем поле role в форму редактирования
    fieldsets = BaseUserAdmin.fieldsets + ((None, {"fields": ("role",)}),)
    # Чтобы поле role было видно в списке пользователей
    list_display = ("username", "email", "role", "is_staff", "is_superuser")

    # Чтобы поле role было доступно при создании пользователя через админку
    add_fieldsets = (BaseUserAdmin.add_fieldsets +
                     ((None, {"fields": ("role",)}),))


admin.site.register(User, UserAdmin)
