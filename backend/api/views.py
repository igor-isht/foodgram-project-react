from http import HTTPStatus

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipys.models import Basket, Favorite, Ingredient, Recipy, Tag
from rest_framework import mixins, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from users.models import Follow, User

from .filter import IngredientFilter, RecipyFilter
from .permissions import AdminPermission, AuthorOrReadOnly
from .serializers import (BriefRecipySerializer, FavoriteSerializer,
                          FollowSerializer, IngredientSerializer,
                          IngredientsForRecipy, PostRecipySerializer,
                          ReadRecipySerializer, ShoppingCart,
                          SubscribeSerializer, TagSerializer, UserSerializer)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AdminPermission | AuthorOrReadOnly]

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


class FollowViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FollowSerializer

    def get_queryset(self):
        follower = self.request.user
        return follower.follower.all()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipyVeiwSet(viewsets.ModelViewSet):
    queryset = Recipy.objects.all()
    permission_classes = [AdminPermission | AuthorOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipyFilter
    serializer_class = ReadRecipySerializer

    def create_ingredients_for_recipy(self, recipy, ingredients):
        recipy_list = []
        for ingredient in ingredients:
            ingredients_for_recipy = IngredientsForRecipy(
                recipy=recipy,
                ingredient_id=ingredient.get('ingredient').get('id'),
                amount=ingredient.get('amount')
            )
            recipy_list.append(ingredients_for_recipy)
        IngredientsForRecipy.objects.bulk_create(recipy_list)

    def create(self, request, *args, **kwargs):
        author = self.request.user
        serializer = PostRecipySerializer(data=request.data)
        if serializer.is_valid():
            tags = serializer.validated_data.pop('tags')
            ingredients = serializer.validated_data.pop('recipy')
            recipy = Recipy.objects.create(
                author=author,
                **serializer.validated_data
            )
            recipy.tags.set(tags)
            self.create_ingredients_for_recipy(recipy, ingredients)

        context = {'request': self.request}
        serializer = ReadRecipySerializer(instance=recipy, context=context)
        return Response(
            data=serializer.data,
            status=HTTPStatus.CREATED
        )

    def update(self, request, *args, **kwargs):
        author = self.request.user
        serializer = PostRecipySerializer(data=request.data)
        if serializer.is_valid():
            tags = serializer.validated_data.pop('tags')
            ingredients = serializer.validated_data.pop('recipy')
            recipy = Recipy.objects.create(
                author=author,
                **serializer.validated_data
            )
            recipy = get_object_or_404(Recipy, id=self.kwargs.get('pk'))
            IngredientsForRecipy.objects.filter(recipy=recipy).delete()
            recipy.tags.set(tags)
            self.create_ingredients_for_recipy(recipy, ingredients)

        context = {'request': self.request}
        serializer = ReadRecipySerializer(instance=recipy, context=context)
        return Response(
            data=serializer.data,
            status=HTTPStatus.CREATED
        )


class CreateDestroyViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    """Вьюсет для создания/удаления подписок, избранного, корзины продуктов."""
    pass


class SubscribeViewSet(CreateDestroyViewSet):
    serializer_class = SubscribeSerializer

    def get_queryset(self):
        user = self.request.user
        return user.author.all()

    def create(self, request, *args, **kwargs):
        author = get_object_or_404(
            User,
            id=self.kwargs.get('user_id')
        )

        if self.request.user == author:
            return Response(
                'Нельзя подписываться на самого себя!',
                status=HTTPStatus.BAD_REQUEST
            )
        if Follow.objects.filter(user=request.user,
                                 author=author).exists():
            return Response(
                'Вы уже подписаны на этого автора!',
                status=HTTPStatus.BAD_REQUEST
            )

        follow = Follow.objects.create(
            user=self.request.user,
            author=author
        )
        serializer = FollowSerializer(
            follow,
            context={'request': request}
        )
        return Response(
            data=serializer.data,
            status=HTTPStatus.CREATED
        )

    def delete(self, request, *args, **kwargs):
        author = get_object_or_404(
            User,
            id=self.kwargs.get('user_id')
        )
        get_object_or_404(
            Follow,
            user=self.request.user,
            author=author
        ).delete()
        return Response(status=HTTPStatus.NO_CONTENT)


class FavoriteViewSet(CreateDestroyViewSet):
    serializer_class = FavoriteSerializer

    def get_queryset(self):
        user = self.request.user
        return user.favorite.all()

    def create(self, request, *args, **kwargs):
        recipy = get_object_or_404(
            Recipy,
            id=self.kwargs.get('recipe_id')
        )
        Favorite.objects.create(
            user=request.user,
            recipy=recipy
        )
        serializer = BriefRecipySerializer(
            recipy,
            many=False
        )
        return Response(
            data=serializer.data,
            status=HTTPStatus.CREATED
        )

    def delete(self, request, *args, **kwargs):
        recipy = get_object_or_404(
            Recipy,
            id=self.kwargs.get('recipe_id')
        )
        get_object_or_404(
            Favorite,
            user=request.user,
            recipy=recipy
        ).delete()
        return Response(status=HTTPStatus.NO_CONTENT)


class ShoppingCartViewSet(CreateDestroyViewSet):
    serializer_class = ShoppingCart

    def get_queryset(self):
        user = self.request.user
        return user.recipy_in_basket.all()

    def create(self, request, *args, **kwargs):
        recipy = get_object_or_404(
            Recipy,
            id=self.kwargs.get('recipe_id')
        )
        Basket.objects.create(
            user=request.user,
            recipy=recipy
        )
        serializer = BriefRecipySerializer(
            recipy,
            many=False
        )
        return Response(
            data=serializer.data,
            status=HTTPStatus.CREATED
        )

    def delete(self, request, *args, **kwargs):
        recipy = get_object_or_404(
            Recipy,
            id=self.kwargs.get('recipe_id')
        )
        get_object_or_404(
            Basket,
            user=request.user,
            recipy=recipy
        ).delete()
        return Response(status=HTTPStatus.NO_CONTENT)


@api_view()
def download_shopping_cart(request):
    baskets = Basket.objects.filter(user=request.user)
    cart_list = {}
    for basket in baskets:
        for ingredient in basket.recipy.ingredients.all():
            amount = get_object_or_404(
                IngredientsForRecipy,
                recipy=basket.recipy,
                ingredient=ingredient
            ).amount
            if ingredient.name not in cart_list:
                cart_list[ingredient.name] = amount
            else:
                cart_list[ingredient.name] += amount

    content = 'Список покупок:\n\n'
    if not cart_list:
        content += 'Корзина пуста!'
    for item in cart_list:
        measurement_unit = get_object_or_404(
            Ingredient,
            name=item
        ).measurement_unit
        content += f'{item}: {cart_list[item]} {measurement_unit}\n'

    response = HttpResponse(
        content, content_type='text/plain,charset=utf8'
    )
    response['Content-Disposition'] = 'attachment; filename="grocery_list.txt"'
    return response
