from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from drf_extra_fields.fields import Base64ImageField

from recipys.models import Ingredient, Tag, Recipy, IngredientsForRecipy, Favorite, Basket
from users.models import User, Follow





class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


    @action(detail=False, url_path='subscriptions')
    def subscriptions(self, request):
        """Получить подписки."""

        user = request.user
        print(user)
        queryset = Follow.objects.filter(user=user)
        serializer = FollowSerializer(
            many=True,
            context={'request': request})
        return Response(serializer.data)


class BriefRecipySerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipy
        fields = ('id', 'name', 'image', 'cooking_time')

class FollowSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    is_subscribed = serializers.SerializerMethodField()
    last_name = serializers.ReadOnlyField(source='author.last_name')
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
        limit = request.GET.get('recipes_limit')
        if limit:
            recipes = Recipy.objects.filter(author=obj.author)[:int(limit)]
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
    id = serializers.IntegerField(source='ingredient.id')
    amount = serializers.IntegerField()
    class Meta:
        model = IngredientsForRecipy
        fields = ('id', 'amount')


class IngredientsForRecipySerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(read_only=True,
        source='ingredient.id')
    name = serializers.CharField(read_only=True,
        source='ingredient.name')
    measurement_unit = serializers.CharField(read_only=True,
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientsForRecipy
        fields = ('id', 'name', 'measurement_unit', 'amount')
        

class ReadRecipySerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientsForRecipySerializer(
        many=True,
        source='recipy')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField(
    )
    
    class Meta:
        model = Recipy
        fields = ('id', 'tags', 'author', 'ingredients', 'name',
        'image', 'text', 'cooking_time', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return (
            request.user.is_authenticated
            and Favorite.objects.filter(
                user=request.user,
                recipy_id=obj.id
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return (
            request.user.is_authenticated
            and Basket.objects.filter(
                user=request.user,
                recipy_id=obj.id
            ).exists()
        )


class PostRecipySerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    image=Base64ImageField()
    ingredients = IngredientsForRecipyEditSerializer(
        many=True,
        source='recipy')
    

    class Meta:
        model = Recipy
        fields = ('id', 'tags', 'author', 'name', 'ingredients',
        'image', 'text', 'cooking_time')

    def create_ingredients_for_recipy(self, recipy, ingredients):
        for ingredient in ingredients:
            IngredientsForRecipy.objects.create(
                recipy=recipy,
                ingredient_id=ingredient.get('ingredient').get('id'),
                amount=ingredient.get('amount')
            )


    def create(self, validated_data):
        author = self.context.get('request').user
        tags=validated_data.pop('tags')
        ingredients=validated_data.pop('recipy')
        recipy=Recipy.objects.create(author=author, **validated_data)
        recipy.tags.set(tags)
        recipy.save()
        self.create_ingredients_for_recipy(recipy, ingredients)
        return recipy
    

    def update(self, instance, validated_data):
        if 'recipy' in validated_data:
            ingredients = validated_data.pop('recipy')
            IngredientsForRecipy.objects.filter(recipy=instance).delete()
            self.create_ingredients_for_recipy(instance, ingredients)
        if 'tags' in validated_data:
            tags=validated_data.pop('tags')
            instance.tags.set(tags)
        return super().update(instance, validated_data)


    def to_representation(self, instance):
        return ReadRecipySerializer(instance).data




class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'


class SubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = '__all__'

class ShoppingCart(serializers.ModelSerializer):
    class Meta:
        model = Basket
        fields = '__all__'