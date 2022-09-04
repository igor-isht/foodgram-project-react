from django.contrib import admin

from .models import Follow, User


class UserAdmin(admin.ModelAdmin):
    list_filter = ('email', 'username')
    search_fields = ('email', 'username')
    list_display = ('id', 'email', 'username', 'is_superuser')
    list_editable = ('is_superuser',)


admin.site.register(User, UserAdmin)
admin.site.register(Follow)
