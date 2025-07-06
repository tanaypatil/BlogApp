from django.contrib import admin

from Api.models import Blog, Tag, BlogUser, Comment


class BlogUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('username', 'email', 'first_name', 'last_name')

    class Meta:
        model = BlogUser
        fields = '__all__'


admin.site.register(BlogUser)
admin.site.register(Tag)
admin.site.register(Blog)
admin.site.register(Comment)
