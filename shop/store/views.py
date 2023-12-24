from random import randint

from django.shortcuts import render, redirect
from .models import *
from django.views.generic import ListView, DetailView
from django.contrib.auth import login, logout
from .forms import LoginForm, RegisterForm, ReviewForm, CustomerForm, ShippingForm
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import CartForAuthenticatedUser, get_cart_data
from shop import settings
import stripe


# Create your views here.

class ProductList(ListView):
    model = Product
    context_object_name = 'categories'
    extra_context = {
        'title': 'Главная страница'
    }
    template_name = 'store/product_list.html'

    def get_queryset(self):
        categories = Category.objects.filter(parent=None)  # Получили категории у которых нет родителей
        return categories


class CategoryView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'store/category_page.html'
    paginate_by = 1

    def get_queryset(self):
        sort_field = self.request.GET.get('sort')
        type_field = self.request.GET.get('type')
        if type_field:
            products = Product.objects.filter(category__slug=type_field)
            return products

        main_category = Category.objects.get(slug=self.kwargs['slug'])  # По слагу получили категорию
        subcategories = main_category.subcategories.all()
        products = Product.objects.filter(category__in=subcategories)
        if sort_field:
            products = products.order_by(sort_field)

        return products

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        main_category = Category.objects.get(slug=self.kwargs['slug'])
        context['category'] = main_category
        context['title'] = f'Категория: {main_category.title}'
        return context


class ProductDetail(DetailView):
    model = Product
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        product = Product.objects.get(slug=self.kwargs['slug'])
        context['title'] = f'{product.category}: {product.title}'

        products = Product.objects.all()
        data = []
        for i in range(4):
            random_index = randint(0, len(products) - 1)
            p = products[random_index]
            if p not in data:
                data.append(p)
        context['products'] = data
        context['reviews'] = Review.objects.filter(product=product)  # Получаем отзывы продукта

        if self.request.user.is_authenticated:
            context['review_form'] = ReviewForm()

        return context


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user:
                login(request, user)
                page = request.META.get('HTTP_REFERER', 'product_list')
                messages.success(request, 'Усмешный вход')
                return redirect(page)
            else:
                messages.error(request, 'Не верный логин или пароль')
                return redirect('product_list')
        else:
            messages.error(request, 'Не верный логин или пароль')
            return redirect('product_list')


def user_logout(request):
    logout(request)
    page = request.META.get('HTTP_REFERER', 'product_list')
    messages.warning(request, 'Вы вышли из аккаунта')
    return redirect(page)


def register(request):
    if request.method == 'POST':
        form = RegisterForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            page = request.META.get('HTTP_REFERER', 'product_list')
            return redirect(page)
        else:
            for field in form.errors:
                messages.error(request, form.errors[field].as_text())
                return redirect('product_list')


def save_review(request, slug):
    form = ReviewForm(data=request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.author = request.user
        product = Product.objects.get(slug=slug)
        review.product = product
        review.save()
        messages.success(request, 'Ваш отзыв оставлен')
    else:
        pass

    return redirect('product_detail', product.slug)


# Функция для сохраенния товара в избранное

def save_favorite_products(request, slug):
    if request.user.is_authenticated:
        user = request.user
        product = Product.objects.get(slug=slug)
        favorite_products = FavouriteProduct.objects.filter(user=user)
        if user:
            if product in [i.product for i in favorite_products]:
                fav_product = FavouriteProduct.objects.get(user=user, product=product)
                fav_product.delete()
                messages.error(request, 'Товар удалён из Избранного')
            else:
                FavouriteProduct.objects.create(user=user, product=product)
                messages.success(request, 'Товар добавлен в Избранное')
    else:
        messages.warning(request, 'Авторизуйтесь что бы добавить в Избранное')

    page = request.META.get('HTTP_REFERER', 'product_list')

    return redirect(page)


# Вьюшка для страницы избранного

class FavoriteProductView(LoginRequiredMixin, ListView):
    model = FavouriteProduct
    context_object_name = 'products'
    template_name = 'store/favorite.html'
    login_url = 'product_list'

    def get_queryset(self):
        user = self.request.user
        fav = FavouriteProduct.objects.filter(user=user)
        products = [i.product for i in fav]
        return products


# Функция для соранения почт
def save_mail_customer(request):
    if request.user.is_authenticated:
        email = request.POST.get('email')
        user = request.user
        if email:
            try:
                MailCustomer.objects.create(user=user, mail=email)
                messages.success(request, 'Ваша почта сохранена')
            except:
                page = request.META.get('HTTP_REFERER', 'product_list')
                messages.warning(request, 'Ваша почта уже есть')
                return redirect(page)
    else:
        messages.warning(request, 'Авторизуйтесь что бы оставить почту')

    page = request.META.get('HTTP_REFERER', 'product_list')
    return redirect(page)


# Функция для отправки сообщений на почты
from shop import settings
from django.core.mail import send_mail


def send_mail_to_customer(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            text = request.POST.get('text')
            mail_list = MailCustomer.objects.all()
            for email in mail_list:
                mail = send_mail(
                    subject='Взможно вас заинтересует',
                    message=text,
                    from_email=settings.EMAIL_HOST_USER,  # От кого отправлять
                    recipient_list=[email],  # Кому отправлять
                    fail_silently=False  # Если почта не сущ избегу ошибки
                )
                print(f'Сообщения были отправлены на почты {email}? - {bool(mail)}')

        else:
            pass
    else:
        return redirect('product_list')

    return render(request, 'store/send_mail_customer.html')


# Функция для страницы корзины
def cart(request):
    if request.user.is_authenticated:
        cart_info = get_cart_data(request)

        context = {
            'title': 'Моя корзина',
            'order': cart_info['order'],
            'products': cart_info['products']
        }

        return render(request, 'store/cart.html', context)
    else:
        messages.warning(request, 'Авторизуйтесь что бы попасть в Корзину')
        return redirect('product_list')


# Функция для добавления товара в корзину
def to_cart(request, product_id, action):
    if request.user.is_authenticated:
        print(product_id, action)
        user_cart = CartForAuthenticatedUser(request, product_id, action)
        page = request.META.get('HTTP_REFERER', 'product_list')
        return redirect(page)
    else:
        messages.success(request, 'Авторизуйтесь что бы добавить в Корзину')
        page = request.META.get('HTTP_REFERER', 'product_list')
        return redirect(page)


# Функция для страницы  оформления заказа
def checkout(request):
    if request.user.is_authenticated:
        cart_info = get_cart_data(request)

        context = {
            'title': 'Оформление заказа',
            'order': cart_info['order'],
            'items': cart_info['products'],
            'customer_form': CustomerForm(),
            'shipping_form': ShippingForm()
        }

        return render(request, 'store/checkout.html', context)

    else:
        return redirect('product_list')



# Вьщка для оформления и реализации оплаты
def create_checkout_session(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY   # Указали ключ для оплаты
    if request.method == 'POST':
        user_cart = CartForAuthenticatedUser(request)
        cart_info = user_cart.get_cart_info()   # Получим инфо о корзине словарём

        customer_form = CustomerForm(data=request.POST)
        if customer_form.is_valid():  # В данном условии сохраняем Ф и И покупателя из формы
            customer = Customer.objects.get(user=request.user)
            customer.first_name = customer_form.cleaned_data['first_name']
            customer.last_name = customer_form.cleaned_data['last_name']
            customer.save()


        shipping_form = ShippingForm(data=request.POST)
        if shipping_form.is_valid():
            address = shipping_form.save(commit=False)
            address.customer = Customer.objects.get(user=request.user)
            address.order = user_cart.get_cart_info()['order']
            address.save()

        total_price = cart_info['cart_total_price']
        session = stripe.checkout.Session.create(
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Покупка а сайте TOTEMBO'
                    },
                    'unit_amount': int(total_price * 100)
                },
                'quantity': 1
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('success')),
            cancel_url=request.build_absolute_uri(reverse('checkout'))
        )

        return redirect(session.url, 303)





# Функция для страницы успешной оплаты
def success_payment(request):
    if request.user.is_authenticated:
        user_cart = CartForAuthenticatedUser(request)
        cart_info = user_cart.get_cart_info()
        order = cart_info['order']
        order_save = SaveOrder.objects.create(customer=order.customer, total_price=order.get_cart_total_price)
        order_save.save()
        order_products = order.orderproduct_set.all()
        for item in order_products:
            save_order_product = SaveOrderProducts.objects.create(order_id=order_save.pk,
                                                                  product=str(item),
                                                                  quantity=item.quantity,
                                                                  product_price=item.product.price,
                                                                  final_price=item.get_total_price,
                                                                  photo=item.product.get_image_product())
            print(f'Заказанный продукт {item} сохраенён')
            save_order_product.save()

        user_cart.clear()
        messages.success(request, 'Ваша оплата прошл успешно')
        return render(request, 'store/success.html')
    else:
        return redirect('product_list')




# Функция для очищения корзины
def clear_cart(request):
    user_cart = CartForAuthenticatedUser(request)
    order = user_cart.get_cart_info()['order']
    order_products = order.orderproduct_set.all() # Получаю заказанные продукты заказа
    for order_product in order_products:
        quantity = order_product.quantity  # Каждого закзанного продукта получ кол-во
        product = order_product.product
        order_product.delete()
        product.quantity += quantity
        product.save()

    return redirect('my_cart')







