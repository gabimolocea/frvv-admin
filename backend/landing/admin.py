from django.contrib import admin
from django.utils.html import format_html
from .models import NewsPost, Event, AboutSection, ContactMessage, ContactInfo

@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'published', 'featured', 'author', 'created_at', 'updated_at']
    list_filter = ['published', 'featured', 'created_at', 'author']
    search_fields = ['title', 'content', 'excerpt', 'author', 'tags']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['published', 'featured']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'excerpt', 'tags')
        }),
        ('Content', {
            'fields': ('content', 'featured_image', 'featured_image_alt')
        }),
        ('Publication Settings', {
            'fields': ('published', 'featured')
        }),
        ('SEO Settings', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'canonical_url', 'robots_index', 'robots_follow'),
            'classes': ('collapse',),
            'description': 'Search Engine Optimization settings'
        }),
    )

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_date', 'location', 'is_featured', 'registration_required', 'event_status']
    list_filter = ['is_featured', 'registration_required', 'start_date']
    search_fields = ['title', 'description', 'location', 'tags']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_featured']
    ordering = ['start_date']
    
    fieldsets = (
        ('Event Details', {
            'fields': ('title', 'slug', 'description', 'featured_image', 'featured_image_alt', 'tags')
        }),
        ('Date & Location', {
            'fields': ('start_date', 'end_date', 'location', 'address')
        }),
        ('Registration', {
            'fields': ('registration_required', 'registration_link', 'max_participants', 'price')
        }),
        ('Display Settings', {
            'fields': ('is_featured',)
        }),
        ('SEO Settings', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'canonical_url', 'robots_index', 'robots_follow'),
            'classes': ('collapse',),
            'description': 'Search Engine Optimization settings'
        }),
    )
    
    def event_status(self, obj):
        if obj.is_upcoming:
            return format_html('<span style="color: green;">Upcoming</span>')
        else:
            return format_html('<span style="color: red;">Past</span>')
    event_status.short_description = 'Status'

@admin.register(AboutSection)
class AboutSectionAdmin(admin.ModelAdmin):
    list_display = ['section_title', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['section_title', 'content']
    list_editable = ['order', 'is_active']
    ordering = ['order']
    
    fieldsets = (
        ('Section Information', {
            'fields': ('section_title', 'content', 'image', 'image_alt')
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active')
        }),
    )

# Keep the existing ContactMessage and ContactInfo admin classes...
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'priority', 'is_read', 'is_replied', 'created_at']
    list_filter = ['priority', 'is_read', 'is_replied', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    list_editable = ['is_read', 'is_replied', 'priority']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Message Details', {
            'fields': ('name', 'email', 'phone', 'subject', 'message', 'created_at')
        }),
        ('Status', {
            'fields': ('priority', 'is_read', 'is_replied')
        }),
        ('Admin Notes', {
            'fields': ('admin_notes',),
            'classes': ('collapse',)
        }),
    )

@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ['organization_name', 'email', 'phone', 'is_active']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Organization Details', {
            'fields': ('organization_name', 'address', 'phone', 'email', 'website')
        }),
        ('Social Media', {
            'fields': ('social_media_facebook', 'social_media_instagram', 'social_media_twitter')
        }),
        ('Additional Info', {
            'fields': ('business_hours', 'is_active')
        }),
    )
    
    def has_add_permission(self, request):
        return not ContactInfo.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False