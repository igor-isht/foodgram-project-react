from django.contrib import admin
from .models import Follow, User


class UserAdmin(admin.ModelAdmin):
    list_filter = ('email', 'username')
    search_fields = ('email', 'username')
    list_display = ('id', 'email', 'username', 'role')
    list_editable = ('role',)


admin.site.register(User, UserAdmin)
admin.site.register(Follow)