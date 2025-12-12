from django.contrib import admin
from .models import User, Profile, Badge, PasswordResetCode

admin.site.register(User)
admin.site.register(Profile)
admin.site.register(Badge)
admin.site.register(PasswordResetCode)
