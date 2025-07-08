from rest_framework import serializers

from Api.models import Blog, Tag, Comment, BlogUser


class BlogUserSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(max_length=30, allow_empty_file=False, use_url=True)
    bio = serializers.CharField(allow_blank=True, allow_null=True, required=False)

    def create(self, validated_data):
        blog_user = BlogUser(
            username=validated_data['username'],
            email=validated_data['email'],
            profile_picture=validated_data['profile_picture'],
        )
        if 'bio' in validated_data:
            blog_user.bio = validated_data['bio']
        blog_user.set_password(validated_data['password'])
        blog_user.save()
        return blog_user

    class Meta:
        model = BlogUser
        fields = ['id', 'username', 'email', 'bio', 'profile_picture', 'password']
        read_only_fields = ['id']
        extra_kwargs = {'password': {'write_only': True}}


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class BlogSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = BlogUserSerializer(read_only=True)

    def create(self, validated_data):
        tag_names = validated_data.pop('tags', [])
        blog = Blog.objects.create(**validated_data)
        tags = [Tag.objects.get_or_create(name=tag['name'])[0] for tag in tag_names]
        blog.tags.set(tags)
        return blog

    def update(self, instance, validated_data):
        tag_names = validated_data.pop('tags', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tag_names:
            tags = [Tag.objects.get_or_create(name=tag['name'])[0] for tag in tag_names]
            instance.tags.set(tags)
        return instance

    class Meta:
        model = Blog
        fields = '__all__'
        read_only_fields = ['author', 'created', 'slug']


class CommentSerializer(serializers.ModelSerializer):
    blog = serializers.PrimaryKeyRelatedField(queryset=Blog.objects.none())

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['user', 'created']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            self.fields['blog'].queryset = Blog.objects.filter(author=request.user)
