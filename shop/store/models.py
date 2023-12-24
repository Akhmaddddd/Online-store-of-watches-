from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=150, verbose_name='Название категории')
    image = models.ImageField(upload_to='categories/', null=True, blank=True, verbose_name='Изображение')
    slug = models.SlugField(unique=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE,
                               null=True, blank=True, verbose_name='Категория',
                               related_name='subcategories')

    def get_absolute_url(self):
        return reverse('category_page', kwargs={'slug': self.slug})

    # Метод для получения картинки категории
    def get_image_category(self):
        if self.image:
            return self.image.url
        else:
            return ''

    def __str__(self):
        return self.title

    def __repr__(self):  # Метод для отображения объектов в Админке
        return f'Категория: pk={self.pk}, title={self.title}'

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Product(models.Model):
    title = models.CharField(max_length=150, verbose_name='Название товара')
    price = models.FloatField(verbose_name='Цена')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    quantity = models.IntegerField(default=0, verbose_name='Количество товара')
    description = models.TextField(default='Здесь скоро будит описание', verbose_name='Описание товара')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория',
                                 related_name='products')
    slug = models.SlugField(unique=True, null=True)
    size = models.IntegerField(default=30, verbose_name='Размер')
    color = models.CharField(max_length=50, default='Серебро', verbose_name='Цвет/Материал')

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})

    # Метод для получения картинки категории
    def get_image_product(self):
        if self.images:
            try:
                return self.images.first().image.url
            except:
                return ''
        else:
            return ''

    def __str__(self):
        return self.title

    def __repr__(self):  # Метод для отображения объектов в Админке
        return f'Товар: pk={self.pk}, title={self.title}, price={self.price}'

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


class Gallery(models.Model):
    image = models.ImageField(upload_to='products/', verbose_name='Изображение товаров')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'


class Review(models.Model):
    text = models.TextField(verbose_name='Отзыв покупателя')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Покупатель')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Продукт отзыва')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата отзыва')

    def __str__(self):
        return self.author.username

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'


# Меделька избранного

class FavouriteProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Покупатель')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Продукт')

    def __str__(self):
        return self.product.title

    class Meta:
        verbose_name = 'Избранный товар'
        verbose_name_plural = 'Избранные товары'


# Моделька для сохранения почт покупателей
class MailCustomer(models.Model):
    mail = models.EmailField(unique=True, verbose_name='Почта покупателя')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Покупатель')

    def __str__(self):
        return self.mail

    class Meta:
        verbose_name = 'Почта'
        verbose_name_plural = 'Почтовые  Адреса'


# Модельки Покупателя, Заказа, Заказанных продуктов, Адреса доставки


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Пользователь')
    first_name = models.CharField(max_length=250, default='', verbose_name='Имя пользовтеля')
    last_name = models.CharField(max_length=250, default='', verbose_name='Фамилия пользовтеля')

    def __str__(self):
        return self.first_name

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'


# Модель заказа

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Покупатель')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата заказа')
    is_completed = models.BooleanField(default=False, verbose_name='Выполнен ли закзаз')
    shipping = models.BooleanField(default=True)

    def __str__(self):
        return str(self.pk)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    # Реализуем методы для подсчёта суммы заказа и ко-ва товаров

    @property  # Метод для получения суммы заказа
    def get_cart_total_price(self):
        order_products = self.orderproduct_set.all()
        total_price = sum([product.get_total_price for product in order_products])
        return total_price

    @property  # Метод для получения кол-ва заказанного товара
    def get_cart_total_quantity(self):
        order_products = self.orderproduct_set.all()
        total_quantity = sum([product.quantity for product in order_products])
        return total_quantity


class OrderProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, verbose_name='Продукт')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, verbose_name='Заказ')
    quantity = models.IntegerField(default=0, null=True, blank=True, verbose_name='Кол-во товара')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    def __str__(self):
        return self.product.title

    class Meta:
        verbose_name = 'Товар заказа'
        verbose_name_plural = 'Товары зоказов'

    @property
    def get_total_price(self):  # Метод который будит считать сумму товара в его кол-ве
        total_price = self.product.price * self.quantity
        return total_price


# Модель Адреса доставки
class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, verbose_name='Покупатель')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, verbose_name='Заказ')
    address = models.CharField(max_length=300, verbose_name='Адрес доставки')
    city = models.ForeignKey('City', on_delete=models.SET_NULL, null=True, verbose_name='Город')
    region = models.CharField(max_length=250, verbose_name='Регион')
    phone = models.CharField(max_length=250, verbose_name='номер телефона')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата доставки')

    def __str__(self):
        return self.address

    class Meta:
        verbose_name = 'Адрес доставки'
        verbose_name_plural = 'Адреса доставок'


class City(models.Model):
    city = models.CharField(max_length=300, verbose_name='Название города')

    def __str__(self):
        return self.city

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'


# Модель Профиля
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    phone_number = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return self.user.username

    # Метод для получения фото профиля
    def get_photo(self):
        try:
            return self.photo.url
        except:
            return ''

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'



# Модель для сохраенния Заказов
class SaveOrder(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Покупатель')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата заказа')
    total_price = models.FloatField(default=0, verbose_name='Сумма заказа')


    def __str__(self):
        return f'Заказ №: {self.pk}'


    class Meta:
        verbose_name = 'История заказа'
        verbose_name_plural = 'Истории заказов'


# Модель для сохранения заказанных продуктов
class SaveOrderProducts(models.Model):
    order = models.ForeignKey(SaveOrder, on_delete=models.CASCADE, null=True, related_name='products')
    product = models.CharField(max_length=400, verbose_name='Товар')
    quantity = models.IntegerField(default=0, verbose_name='Количество')
    product_price = models.FloatField(verbose_name='Цена товара')
    final_price = models.FloatField(verbose_name='На сумму')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата покупки')
    photo = models.ImageField(upload_to='images/', verbose_name='Фото товара')

    def __str__(self):
        return f'{self.product}'


    class Meta:
        verbose_name = 'История заказанного товара'
        verbose_name_plural = 'Истории заказанных товаров'












