from rest_framework import serializers
from .models import NewsPost, Event, AboutSection, ContactMessage, ContactInfo

class NewsPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsPost
        fields = [
            'id', 'title', 'slug', 'content', 'excerpt', 'featured_image', 
            'featured_image_alt', 'published', 'featured', 'author', 'tags',
            'created_at', 'updated_at', 'meta_title', 'meta_description', 
            'meta_keywords', 'canonical_url', 'robots_index', 'robots_follow'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class NewsPostListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list views"""
    class Meta:
        model = NewsPost
        fields = [
            'id', 'title', 'slug', 'excerpt', 'featured_image', 
            'featured_image_alt', 'published', 'featured', 'author', 
            'tags', 'created_at'
        ]

class EventSerializer(serializers.ModelSerializer):
    is_upcoming = serializers.ReadOnlyField()
    is_past = serializers.ReadOnlyField()
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'slug', 'description', 'start_date', 'end_date',
            'location', 'address', 'featured_image', 'featured_image_alt',
            'is_featured', 'registration_required', 'registration_link',
            'max_participants', 'price', 'tags', 'created_at', 'is_upcoming',
            'is_past', 'meta_title', 'meta_description', 'meta_keywords',
            'canonical_url', 'robots_index', 'robots_follow'
        ]
        read_only_fields = ['id', 'created_at', 'is_upcoming', 'is_past']

class EventListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list views"""
    is_upcoming = serializers.ReadOnlyField()
    is_past = serializers.ReadOnlyField()
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'slug', 'start_date', 'end_date', 'location',
            'featured_image', 'featured_image_alt', 'is_featured',
            'registration_required', 'price', 'tags', 'is_upcoming', 'is_past'
        ]

class AboutSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutSection
        fields = [
            'id', 'section_title', 'content', 'image', 'image_alt',
            'order', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = [
            'id', 'name', 'email', 'phone', 'subject', 'message',
            'priority', 'created_at', 'is_read', 'is_replied'
        ]
        read_only_fields = ['id', 'created_at', 'is_read', 'is_replied']

class ContactMessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating contact messages from frontend"""
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']

class ContactInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInfo
        fields = [
            'id', 'organization_name', 'address', 'phone', 'email', 'website',
            'social_media_facebook', 'social_media_instagram', 'social_media_twitter',
            'business_hours', 'is_active'
        ]