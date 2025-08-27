from django.db import models
from django.utils import timezone
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field  # Updated import

class SEOModel(models.Model):
    """Abstract model for SEO fields"""
    meta_title = models.CharField(
        max_length=60, 
        blank=True, 
        help_text="SEO title (60 chars max). If empty, uses the main title."
    )
    meta_description = models.CharField(
        max_length=160, 
        blank=True, 
        help_text="SEO description (160 chars max)"
    )
    meta_keywords = models.CharField(
        max_length=255, 
        blank=True, 
        help_text="SEO keywords, separated by commas"
    )
    canonical_url = models.URLField(
        blank=True, 
        help_text="Canonical URL to avoid duplicate content"
    )
    robots_index = models.BooleanField(
        default=True, 
        help_text="Allow search engines to index this page"
    )
    robots_follow = models.BooleanField(
        default=True, 
        help_text="Allow search engines to follow links on this page"
    )
    
    class Meta:
        abstract = True
    
    def get_meta_title(self):
        return self.meta_title or getattr(self, 'title', '')
    
    def get_robots_content(self):
        index = 'index' if self.robots_index else 'noindex'
        follow = 'follow' if self.robots_follow else 'nofollow'
        return f'{index}, {follow}'

class NewsPost(SEOModel):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, help_text="URL-friendly version of the title")
    content = CKEditor5Field('Content', config_name='extends')  # Updated field
    excerpt = CKEditor5Field('Excerpt', config_name='default', blank=True)  # Updated field
    featured_image = models.ImageField(upload_to='news/', blank=True, null=True)
    featured_image_alt = models.CharField(
        max_length=100, 
        blank=True, 
        help_text="Alt text for featured image (SEO)"
    )
    published = models.BooleanField(default=False)
    featured = models.BooleanField(default=False, help_text="Show on homepage")
    author = models.CharField(max_length=100, blank=True)
    tags = models.CharField(
        max_length=255, 
        blank=True, 
        help_text="Tags separated by commas"
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "News Post"
        verbose_name_plural = "News Posts"
    
    def __str__(self):
        return self.title

class Event(SEOModel):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, help_text="URL-friendly version of the title")
    description = CKEditor5Field('Description', config_name='extends')  # Updated field
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    location = models.CharField(max_length=200)
    address = models.TextField(blank=True, help_text="Full address of the event")
    featured_image = models.ImageField(upload_to='events/', blank=True, null=True)
    featured_image_alt = models.CharField(
        max_length=100, 
        blank=True, 
        help_text="Alt text for featured image (SEO)"
    )
    is_featured = models.BooleanField(default=False, help_text="Show on homepage")
    registration_required = models.BooleanField(default=False)
    registration_link = models.URLField(blank=True, help_text="External registration link")
    max_participants = models.IntegerField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tags = models.CharField(
        max_length=255, 
        blank=True, 
        help_text="Tags separated by commas"
    )
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['start_date']
        verbose_name = "Event"
        verbose_name_plural = "Events"
    
    def __str__(self):
        return f"{self.title} - {self.start_date.strftime('%Y-%m-%d')}"
    
    @property
    def is_upcoming(self):
        return self.start_date > timezone.now()
    
    @property
    def is_past(self):
        return self.start_date < timezone.now()

class AboutSection(models.Model):
    section_title = models.CharField(max_length=100)
    content = CKEditor5Field('Content', config_name='extends')  # Updated field
    image = models.ImageField(upload_to='about/', blank=True, null=True)
    image_alt = models.CharField(
        max_length=100, 
        blank=True, 
        help_text="Alt text for image (SEO)"
    )
    order = models.IntegerField(default=0, help_text="Order in which sections appear")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['order', 'section_title']
        verbose_name = "About Section"
        verbose_name_plural = "About Sections"
    
    def __str__(self):
        return self.section_title

class ContactMessage(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    is_replied = models.BooleanField(default=False)
    admin_notes = models.TextField(blank=True, help_text="Internal notes for staff")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"
    
    def __str__(self):
        return f"{self.name} - {self.subject}"

class ContactInfo(models.Model):
    organization_name = models.CharField(max_length=200)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True)
    social_media_facebook = models.URLField(blank=True)
    social_media_instagram = models.URLField(blank=True)
    social_media_twitter = models.URLField(blank=True)
    business_hours = CKEditor5Field('Business Hours', config_name='default', blank=True)  # Updated field
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Contact Information"
        verbose_name_plural = "Contact Information"
    
    def __str__(self):
        return self.organization_name