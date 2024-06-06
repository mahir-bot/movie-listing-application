from django.contrib import admin
from .models import Profile


class ProfileAdmin(admin.ModelAdmin):
    list_display = ["pkid", "id", "user", "gender",
                    "phone_number", "country", "city"]
    list_display_links = ["pkid", "id", "user"]
    list_filter = ["pkid", "id", "gender", "country", "city"]
    search_fields = ["first_name", "last_name",
                     "phone_number", "country", "city"]
    list_per_page = 10


admin.site.register(Profile, ProfileAdmin)
