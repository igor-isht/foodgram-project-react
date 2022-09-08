from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipys.models import (Basket, Favorite, Ingredient, IngredientsForRecipy,
                            Recipy, Tag)
from users.models import Follow, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'password'
        )
        extra_kwargs = {'password': {'write_only': True}}


class BriefRecipySerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipy
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            'id', 'username', 'email', 'first_name',
            'last_name', 'is_subscribed', 'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return (
                user.is_authenticated
                and Follow.objects.filter(
                    user=user,
                    author=obj.author
                ).exists()
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        if recipes_limit:
            recipes = Recipy.objects.filter(
                author=obj.author
            )[:int(recipes_limit)]
        else:
            recipes = Recipy.objects.filter(author=obj.author)
        serializer = BriefRecipySerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipy.objects.filter(author=obj.author).count()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientsForRecipyEditSerializer(serializers.ModelSerializer):
    """ Сериализатор для игредиентов при создании/редактировании рецептов. """

    id = serializers.IntegerField(source='ingredient.id')
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientsForRecipy
        fields = ('id', 'amount')


class IngredientsForRecipySerializer(serializers.ModelSerializer):
    """ Сериализатор для игредиентов для GET запросов. """

    id = serializers.IntegerField(read_only=True,
                                  source='ingredient.id')
    name = serializers.CharField(read_only=True,
                                 source='ingredient.name')
    measurement_unit = serializers.CharField(
        read_only=True,
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientsForRecipy
        fields = ('id', 'name', 'measurement_unit', 'amount')


class ReadRecipySerializer(serializers.ModelSerializer):
    """ Для рецептов в GET запросах. """

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientsForRecipySerializer(
        many=True,
        source='recipy')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipy
        fields = ('id', 'tags', 'author', 'ingredients', 'name',
                  'image', 'text', 'cooking_time', 'is_favorited',
                  'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (
                    request.user.is_authenticated
                    and Favorite.objects.filter(
                        user=request.user,
                        recipy_id=obj.id
                    ).exists()
            )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (
                request.user.is_authenticated
                and Basket.objects.filter(
                    user=request.user,
                    recipy_id=obj.id
                ).exists()
        )


class PostRecipySerializer(serializers.ModelSerializer):
    """ Для создания/редактирования рецептов. """

    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = IngredientsForRecipyEditSerializer(
        many=True,
        source='recipy')

    class Meta:
        model = Recipy
        fields = ('id', 'tags', 'author', 'name', 'ingredients',
                  'image', 'text', 'cooking_time')

    def validate_ingredients(self, value):
        ingredients = value
        ingredients_list = []
        for ingredient in ingredients:
            if ingredient['amount'] < 1:
                raise serializers.ValidationError(
                    'Проверьте количество ингредиентов')
            if ingredient['ingredient'] in ingredients_list:
                raise serializers.ValidationError(
                    'Ингредиенты повторяются')
            ingredients_list.append(ingredient['ingredient'])
        return value

    def validate_cooking_time(self, value):
        if int(value) < 1:
            raise serializers.ValidationError(
                    'Проверьте время приготовления')
        return value


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'

    def validate(self, attrs):
        return super().validate(attrs)


class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = '__all__'

    def validate_subscribe(self, author):
        if author == self.context['request'].user:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого cебя!')
        return author


class ShoppingCart(serializers.ModelSerializer):
    class Meta:
        model = Basket
        fields = '__all__'
