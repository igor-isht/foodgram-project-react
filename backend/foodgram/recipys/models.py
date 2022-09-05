from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField('ингредиент', max_length=200)
    measurement_unit = models.CharField('единицы измерения', max_length=200)

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Tag(models.Model):
    name = models.CharField('тег', max_length=200, unique=True)
    color = models.CharField('цвет', max_length=7, null=True, unique=True)
    slug = models.SlugField('слаг', max_length=200, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.slug


class Recipy(models.Model):
    name = models.CharField('название блюда', max_length=200)
    text = models.TextField('подробное описание')
    image = models.ImageField('изображение', upload_to='recipes/',)
    pub_date = models.DateTimeField('дата добавления', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recipy',
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientsForRecipy',
        verbose_name='ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipy',
        verbose_name='теги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'время приготовления',
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'


class IngredientsForRecipy(models.Model):
    recipy = models.ForeignKey(
        Recipy,
        on_delete=models.CASCADE,
        related_name='recipy',
        verbose_name='рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient',
        verbose_name='ингредиенты'
    )
    amount = models.PositiveSmallIntegerField(
        'количество',
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['recipy', 'ingredient'],
            name='unique_ingredients_list'
        )]
        verbose_name = 'ингредиент для рецепта'
        verbose_name_plural = 'ингредиенты для рецепта'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='добавивший в избранное пользователь'
    )
    recipy = models.ForeignKey(
        Recipy,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='добавленный в избранное рецепт'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipy'],
                name='unique_favorite'
            )
        ]
        ordering = ['-id']
        verbose_name = 'избранный рецепт'
        verbose_name_plural = 'избранные рецепты'


class Basket(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,

        verbose_name='добавивший в корзину'
    )
    recipy = models.ForeignKey(
        Recipy,
        on_delete=models.CASCADE,
        related_name='recipy_in_basket',
        verbose_name='рецепт в корзине'
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipy'],
            name='unique_basket'
        )]
        ordering = ['-id']
        verbose_name = 'рецепт в корзине'
        verbose_name_plural = 'рецепты в корзине'
