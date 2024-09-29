from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import CustomUser, Subscription

admin.site.register(CustomUser, UserAdmin)
admin.site.register(Subscription)
