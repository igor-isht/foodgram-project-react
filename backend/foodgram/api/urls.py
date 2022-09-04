from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, TagViewSet, RecipyVeiwSet,
                    ShoppingCartViewSet, FollowViewSet, FavoriteViewSet,
                    SubscribeViewSet, DownloadShoppingCart)

router = DefaultRouter()
router.register(r'ingredients', IngredientViewSet)
router.register(r'tags', TagViewSet)
router.register(r'recipes', RecipyVeiwSet)


urlpatterns = [
    path(
        r'recipes/<recipe_id>/favorite/',
        FavoriteViewSet.as_view({
            'post': 'create',
            'delete': 'delete'
        }),
        name='favorite'),
    path(
        r'recipes/<recipe_id>/shopping_cart/',
        ShoppingCartViewSet.as_view({
            'post': 'create',
            'delete': 'delete'
        }),
        name='shopping_cart'),
    path(
        'recipes/download_shopping_cart/',
        DownloadShoppingCart,
        name='download_shopping_cart'
    ),
    path(
        'users/subscriptions/',
        FollowViewSet.as_view({'get': 'list'}),
        name='subscriptions'
    ),
    path(
        r'users/<user_id>/subscribe/',
        SubscribeViewSet.as_view({
            'post': 'create',
            'delete': 'delete'
        }),
        name='favorite'),


    
    path('', include('djoser.urls')),
    path('', include(router.urls)),
    path(r'auth/', include('djoser.urls.authtoken')),
]


