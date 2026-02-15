from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import PermissionDenied

from .decorators import role_required
from .models import Cheese, CheeseType, Batch, BatchItem
from .forms import CheeseForm, BatchItemForm


# Детальное описание сыра
def cheese_detail(request, cheese_id):
    cheese = get_object_or_404(Cheese, id=cheese_id)
    return render(request, "catalog/cheese_detail.html", {"cheese": cheese})


# Страница "О сервисе"
def about(request):
    return render(request, "catalog/about.html")


@role_required(["admin"])
def cheese_create(request):
    if request.method == "POST":
        form = CheeseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("cheese_list")
    else:
        form = CheeseForm()

    return render(request, "catalog/cheese_form.html", {"form": form})


@role_required(["admin", "product_manager"])
def cheese_edit(request, cheese_id):
    cheese = get_object_or_404(Cheese, id=cheese_id)
    if request.method == "POST":
        form = CheeseForm(request.POST, instance=cheese)
        if form.is_valid():
            form.save()
            return redirect("cheese_detail", cheese_id=cheese.id)
    else:
        form = CheeseForm(instance=cheese)

    return render(request, "catalog/cheese_form.html", {"form": form})


@role_required(["admin"])
def cheese_delete(request, cheese_id):
    cheese = get_object_or_404(Cheese, id=cheese_id)
    if request.method == "POST":
        cheese.delete()
        return redirect("cheese_list")

    return render(request,
                  "catalog/cheese_confirm_delete.html", {"cheese": cheese})


def cheese_list(request):
    query = request.GET.get("q", "")  # Поиск по названию сыра
    cheese_type_id = request.GET.get("type")  # Фильтрация по типу сыра
    in_stock = request.GET.get("in_stock")  # Фильтрация по наличию
    order_by = request.GET.get("order_by",
                               "name")  # Сортировка по умолчанию (по имени)

    cheeses = Cheese.objects.all()
    cheese_types = CheeseType.objects.all()

    if query:
        cheeses = cheeses.filter(name__icontains=query)

    if cheese_type_id:
        cheeses = cheeses.filter(cheese_type_id=cheese_type_id)

    if in_stock is not None:
        if in_stock == "true":
            cheeses = cheeses.filter(in_stock=True)
        elif in_stock == "false":
            cheeses = cheeses.filter(in_stock=False)

    cheeses = cheeses.order_by(order_by)

    return render(
        request,
        "catalog/home.html",
        {
            "cheeses": cheeses,
            "cheese_types": cheese_types,
            "selected_type": cheese_type_id,
            "order_by": order_by,
            "query": query,
            "in_stock": in_stock,
        },
    )


@login_required
def batch_list(request):
    batches = (Batch.objects.filter(manager=request.user).
               order_by("-created_at"))
    return render(request, "catalog/batch_list.html",
                  {"batches": batches})


@login_required
def batch_detail(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)
    if batch.manager != request.user and request.user.role != "admin":
        raise PermissionDenied("Вы не можете просматривать чужие партии")
    items = batch.items.select_related("cheese")
    return render(
        request, "catalog/batch_detail.html", {"batch": batch, "items": items}
    )


@login_required
def batch_create(request):
    batch = Batch.objects.create(manager=request.user)
    return redirect("batch_detail", batch_id=batch.id)


@login_required
def batch_add_item(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)
    if batch.manager != request.user and request.user.role != "admin":
        raise PermissionDenied("Вы не можете изменять чужие партии")

    if request.method == "POST":
        form = BatchItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.batch = batch
            item.save()
            return redirect("batch_detail", batch_id=batch.id)
    else:
        form = BatchItemForm()

    return render(
        request, "catalog/batch_add_item.html", {"form": form, "batch": batch}
    )


@login_required
def batch_item_edit(request, item_id):
    item = get_object_or_404(BatchItem, id=item_id)
    batch = item.batch

    if batch.manager != request.user and request.user.role != "admin":
        raise PermissionDenied("Нет прав на редактирование этого товара")

    if request.method == "POST":
        form = BatchItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("batch_detail", batch_id=batch.id)
    else:
        form = BatchItemForm(instance=item)

    return render(
        request,
        "catalog/batch_item_form.html",
        {"form": form, "batch": batch, "item": item},
    )


@login_required
def batch_item_delete(request, item_id):
    item = get_object_or_404(BatchItem, id=item_id)
    batch = item.batch

    if batch.manager != request.user and request.user.role != "admin":
        raise PermissionDenied("Нет прав на удаление этого товара")

    if request.method == "POST":
        item.delete()
        return redirect("batch_detail", batch_id=batch.id)

    return render(
        request,
        "catalog/batch_item_confirm_delete.html",
        {"item": item, "batch": batch},
    )


@login_required
def batch_delete(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)

    if batch.manager != request.user and request.user.role != "admin":
        raise PermissionDenied("Нет прав на удаление этой партии")

    if request.method == "POST":
        batch.delete()
        return redirect("batch_list")

    return render(request, "catalog/batch_confirm_delete.html",
                  {"batch": batch})
