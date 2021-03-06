from django.contrib import admin
from .models import Product, Category, ProductImage


# Register your models here.

# Adds extra images
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


# Adds certain product info to admin
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline, ]

    list_display = (
        'sku',
        'name',
        'category',
        'price',
        'is_featured',
        'main_image',
    )

    ordering = ('category',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'friendly_name',
        'name',
    )


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
