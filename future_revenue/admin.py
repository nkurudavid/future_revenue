from django.contrib import admin
from . models import *

# Register your models here.

class ProductInline(admin.StackedInline):
    model = Product
    extra = 0


class SalesDataInline(admin.StackedInline):
    model = SalesData
    extra = 0


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'all_products',)
    fieldsets = (
        ('Product Category', {
         'fields': ('name',)}),
    )
    add_fieldsets = (
        ('New Product Category', {
         'fields': ('name',)}),
    )
    search_fields = ('name',)
    ordering = ('name',)
    list_per_page = 20
    inlines = [
        ProductInline,
    ]
    def all_products(self, obj):
        return obj.products.count()


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category',)
    list_filter = ('category',)
    fieldsets = (
        ('Product Info', {'fields': ('category', 'name', 'price',)}),
    )
    add_fieldsets = (
        ('New Product', {'fields': ('category', 'name', 'price',)}),
    )
    search_fields = ('name',)
    ordering = ('name', 'category',)
    list_per_page = 20
    inlines = [
        SalesDataInline,
    ]


@admin.register(SalesData)
class SalesDataAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity_sold', 'sales_amount', 'date',)
    list_filter = ('product',)
    fieldsets = (
        ('Sales Data', {'fields': ('product', 'quantity_sold', 'sales_amount', 'date', 'processed_by',)}),
    )
    add_fieldsets = (
        ('New Sales Data', {'fields': ('product', 'quantity_sold', 'sales_amount', 'date', 'processed_by',)}),
    )
    ordering = ('-date',)
    list_per_page = 30




# sorting models
def get_app_list(self, request, app_label=None):
    """
    Return a sorted list of all the installed apps that have been
    registered in this site.
    """
    # Retrieve the original list
    app_dict = self._build_app_dict(request, app_label)
    app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())

    # Sort the models customizable within each app.
    for app in app_list:
        if app['app_label'] == 'FUTURE REVENUE':
            ordering = {
                'ProductCategory': 1,
                'Product': 2,
                'SalesData': 3,
            }
            app['models'].sort(key=lambda x: ordering[x['name']])

    return app_list


admin.AdminSite.get_app_list = get_app_list
