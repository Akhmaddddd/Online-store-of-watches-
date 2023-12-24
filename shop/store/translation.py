from modeltranslation.translator import translator, TranslationOptions
from .models import Category, Product

class CategoryTranslationOptions(TranslationOptions):
    fields = ('title',)


class ProductTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'color')


translator.register(Category, CategoryTranslationOptions)
translator.register(Product, ProductTranslationOptions)



