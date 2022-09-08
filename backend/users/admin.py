from django.contrib import admin

from .models import Follow, User


class FollowAdmin(admin.StackedInline):
    model = Follow
    extra = 0
    fk_name = 'user'


class UserAdmin(admin.ModelAdmin):
    inlines = (FollowAdmin,)
    list_filter = ('email', 'username')
    search_fields = ('email', 'username')
    list_display = ('id', 'email', 'username',
                    'first_name', 'last_name', 'is_superuser')
    list_editable = ('is_superuser',)


admin.site.register(User, UserAdmin)
