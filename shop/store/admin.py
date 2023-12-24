from django.contrib import admin
from django.utils.safestring import mark_safe
from modeltranslation.admin import TranslationAdmin

from .models import *

# Register your models here.

class GalleryAdmin(admin.TabularInline):
    fk_name = 'product'
    model = Gallery
    extra = 1

@admin.register(Category)
class CategoryAdmin(TranslationAdmin):
    list_display = ('title', 'parent', 'get_count_products')
    prepopulated_fields = {'slug': ('title',)}  # Это параматер который будит заполняться автоматом когда будите писать название категории

    # Метод для получения кол-ва продуктов категории
    def get_count_products(self, obj):
        if obj.products:
            return str(len(obj.products.all()))
        else:
            return '0'

    get_count_products.short_description = 'Количество товаров'

@admin.register(Product)
class ProductAdmin(TranslationAdmin):
    list_display = ('pk', 'title', 'category', 'quantity', 'price', 'created_at', 'size', 'color', 'get_photo')
    list_editable = ('price', 'quantity', 'size', 'color')
    list_display_links = ('title',)
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('title', 'price', 'category')
    inlines = [GalleryAdmin]

    # Метод для отображения картинки товара в Админке
    def get_photo(self, obj):
        if obj.images:
            try:
                return mark_safe(f'<img src="{obj.images.all()[0].image.url}" width="75">')
            except:
                return '-'
        else:
            return '-'

    get_photo.short_description = 'Изображение'

# admin.site.register(Category)
# admin.site.register(Product)
admin.site.register(Gallery)
admin.site.register(Review)
admin.site.register(FavouriteProduct)
admin.site.register(MailCustomer)

admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderProduct)
admin.site.register(ShippingAddress)
admin.site.register(City)


admin.site.register(Profile)
admin.site.register(SaveOrder)
admin.site.register(SaveOrderProducts)