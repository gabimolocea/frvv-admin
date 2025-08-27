from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

class CustomAPIRouter(DefaultRouter):
    """
    Custom router that provides information about other APIs
    """
    
    def get_api_root_view(self, api_urls=None):
        api_root_dict = {}
        list_name = self.routes[0].name
        for prefix, viewset, basename in self.registry:
            api_root_dict[prefix] = list_name.format(basename=basename)

        class APIRootView(APIView):
            _ignore_model_permissions = True
            
            def get(self, request, format=None):
                # Get the standard router URLs
                ret = {}
                namespace = request.resolver_match.namespace
                for key, url_name in api_root_dict.items():
                    if namespace:
                        url_name = namespace + ':' + url_name
                    try:
                        ret[key] = reverse(
                            url_name,
                            args=(),
                            kwargs={},
                            request=request,
                            format=format
                        )
                    except:
                        continue
                
                # Add information about other APIs
                ret['_info'] = {
                    'description': 'Main Sports Management API',
                    'version': '1.0',
                    'other_apis': {
                        'landing': {
                            'url': request.build_absolute_uri('/landing/'),
                            'description': 'Landing page content API (news, events, about, contact)',
                            'endpoints': [
                                '/landing/news/',
                                '/landing/events/', 
                                '/landing/about/',
                                '/landing/contact-info/',
                                '/landing/landing-page-data/'
                            ]
                        }
                    }
                }
                
                return Response(ret)

        return APIRootView.as_view()