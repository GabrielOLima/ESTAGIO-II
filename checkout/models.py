# coding=utf-8

from django.db import models
from django.conf import settings

from catalogo.models import Product


class CartItemManager(models.Manager):

    def add_item(self, cart_key, product):
        if self.filter(cart_key=cart_key, product=product).exists():
            created = False
            cart_item = self.get(cart_key=cart_key, product=product)
            cart_item.quantity = cart_item.quantity + 1
            cart_item.save()
        else:
            created = True
            cart_item = CartItem.objects.create(
                cart_key=cart_key, product=product, price=product.price
            )
        return cart_item, created


class CartItem(models.Model):

    cart_key = models.CharField(
        'Chave do Carrinho', max_length=40, db_index=True
    )
    product = models.ForeignKey('catalogo.Product', verbose_name='Produto')
    quantity = models.PositiveIntegerField('Quantidade', default=1)
    price = models.DecimalField('Preço', decimal_places=2, max_digits=8)


    objects = CartItemManager()

    class Meta:
        verbose_name = 'Item do Carrinho'
        verbose_name_plural = 'Itens dos Carrinhos'
        unique_together = (('cart_key', 'product'),)

    def total(self):
        return self.price * self.quantity

    def __str__(self):
        return '{} [{}]'.format(self.product, self.quantity)

class OrderManager(models.Manager): #criação do pedido,o usuário tem que está logado

    def create_order(self, user, cart_items): #funçao do pedido
        order = self.create(user=user) #o método self.create(existe no manage) para criar o objeto
        for cart_item in cart_items:
            order_item = OrderItem.objects.create(
            order=order, quantity=cart_item.quantity, product=cart_item.product,
            price=cart_item.price
            ) #item do pedido
        return order

class Order(models.Model):

    STATUS_CHOICES = (
        (0, 'Aguardando Pagamento'),
        (1,'Concluído'),
        (2,'Cancelado'),
    )#tupla de tuplas

    PAYMENT_OPTIONS_CHOICES = (
        ('deposit' , 'Depósito'),
        ('pagseguro', 'Pagseguro'),
        ('paypal', 'Paypal'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Usuário')
    status = models.IntegerField(
        'Situação', choices=STATUS_CHOICES, default=0, blank=True
    ) #escolher a situação do pedido
    payment_option = models.CharField(
        'Opção de Pagamento', choices=PAYMENT_OPTIONS_CHOICES,max_length=20,
        default='deposit'
    )

    created = models.DateTimeField('Criado em', auto_now_add=True)
    modified = models.DateTimeField('Modificado em', auto_now=True)

    objects = OrderManager() #para fazer a funcao do pedido funcionar

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return 'Pedido #{}'.format(self.pk)


    def products(self): #método para listar os pedidos
        products_ids = self.items.values_list('product')
        return Product.objects.filter(pk__in=products_ids)

    def total(self):
        aggregate_queryset = self.items.aggregate(
            total = models.Sum(
                models.F('price') * models.F('quantity'),
                output_field=models.DecimalField()
            )
        )
        return aggregate_queryset['total']



class OrderItem(models.Model):

    order = models.ForeignKey(Order, verbose_name='Pedido', related_name='items')#retorna apenas a queryset com os Itens
    product = models.ForeignKey('catalogo.Product', verbose_name='Produto')
    quantity = models.PositiveIntegerField('Quantidade', default=1)
    price = models.DecimalField('Preço', decimal_places=2, max_digits=8)

    class Meta:
        verbose_name = 'Item do pedido'
        verbose_name_plural = 'Itens dos pedidos'


    def __str__(self): #retorna o pedidoe o produto
        return '[{}] {}'.format(self.order, self.product) #product é o nome do produto

def post_save_cart_item(instance, **kwargs): # função de remoção de quantidade do carrinho < 0
                if instance.quantity < 1:
                    instance.delete()

models.signals.post_save.connect(
        post_save_cart_item, sender=CartItem, dispatch_uid='post_save_cart_item'
    ) # a função dispatch_uid evita redundância da ação
