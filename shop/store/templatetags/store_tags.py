from django import template
from store.models import Category, FavouriteProduct


register = template.Library()


@register.simple_tag()
def get_categories():
    return Category.objects.filter(parent=None)


@register.simple_tag()
def get_sorted():
    sorters = [
        {
            'title': 'По цене',
            'sorters': [
                ('price', 'По возрастания'),
                ('-price', 'По убыванию')
            ]
        },
        {
            'title': 'По цвету',
            'sorters':[
                ('color', 'От А до Я'),
                ('-color', 'От Я до А')
            ]
        },
        {
            'title': 'По размеру',
            'sorters': [
                ('size', 'По возрастанию'),
                ('-size', 'По убыванию')
            ]
        }
    ]

    return sorters


@register.simple_tag()
def get_favorite_products(user):
    fav = FavouriteProduct.objects.filter(user=user)
    products = [i.product for i in fav]
    return products







