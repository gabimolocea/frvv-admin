from rest_framework import viewsets, status, filters
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import NewsPost, Event, AboutSection, ContactMessage, ContactInfo
from .serializers import (
    NewsPostSerializer, NewsPostListSerializer,
    EventSerializer, EventListSerializer,
    AboutSectionSerializer, ContactMessageSerializer,
    ContactMessageCreateSerializer, ContactInfoSerializer
)

class NewsPostViewSet(viewsets.ModelViewSet):
    queryset = NewsPost.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['published', 'featured', 'author']
    search_fields = ['title', 'content', 'excerpt', 'tags']
    ordering_fields = ['created_at', 'updated_at', 'title']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return NewsPostListSerializer
        return NewsPostSerializer

    def get_queryset(self):
        queryset = NewsPost.objects.all()
        
        # Filter published posts for non-authenticated users
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(published=True)
            
        return queryset

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured news posts"""
        featured_posts = self.get_queryset().filter(featured=True, published=True)
        serializer = NewsPostListSerializer(featured_posts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent news posts"""
        recent_posts = self.get_queryset().filter(published=True)[:5]
        serializer = NewsPostListSerializer(recent_posts, many=True)
        return Response(serializer.data)

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_featured', 'registration_required']
    search_fields = ['title', 'description', 'location', 'tags']
    ordering_fields = ['start_date', 'created_at', 'title']
    ordering = ['start_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return EventListSerializer
        return EventSerializer

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming events"""
        upcoming_events = self.get_queryset().filter(start_date__gt=timezone.now())
        serializer = EventListSerializer(upcoming_events, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def past(self, request):
        """Get past events"""
        past_events = self.get_queryset().filter(start_date__lt=timezone.now())
        serializer = EventListSerializer(past_events, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured events"""
        featured_events = self.get_queryset().filter(is_featured=True)
        serializer = EventListSerializer(featured_events, many=True)
        return Response(serializer.data)

class AboutSectionViewSet(viewsets.ModelViewSet):
    queryset = AboutSection.objects.filter(is_active=True)
    serializer_class = AboutSectionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    ordering = ['order', 'section_title']

class ContactMessageViewSet(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['priority', 'is_read', 'is_replied']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return ContactMessageCreateSerializer
        return ContactMessageSerializer

    def perform_create(self, serializer):
        # Save the contact message (frontend form submission)
        serializer.save()

class ContactInfoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ContactInfo.objects.filter(is_active=True)
    serializer_class = ContactInfoSerializer

# Simple API views for common use cases
@api_view(['GET'])
def landing_page_data(request):
    """Get all data needed for landing page in one API call"""
    data = {
        'featured_news': NewsPostListSerializer(
            NewsPost.objects.filter(featured=True, published=True)[:3], 
            many=True
        ).data,
        'upcoming_events': EventListSerializer(
            Event.objects.filter(start_date__gt=timezone.now(), is_featured=True)[:3],
            many=True
        ).data,
        'about_sections': AboutSectionSerializer(
            AboutSection.objects.filter(is_active=True),
            many=True
        ).data,
        'contact_info': ContactInfoSerializer(
            ContactInfo.objects.filter(is_active=True).first()
        ).data if ContactInfo.objects.filter(is_active=True).exists() else None
    }
    return Response(data)

@api_view(['POST'])
def submit_contact_form(request):
    """Simple contact form submission endpoint"""
    serializer = ContactMessageCreateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {'message': 'Contact message sent successfully!'}, 
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)