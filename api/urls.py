from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    ListingImageViewSet,
    UserViewSet,
    PasswordResetRequestView,
    PasswordResetView,
    get_user_data, get_user_types, get_sale_types,
    RequestViewSet, ConditionViewSet, PropertyTypeViewSet,
    SectorViewSet, LocationViewSet,
    ListingViewSet, MessageViewSet,
    HeatingTypeViewSet, PlanningTypeViewSet, ConstructionTypeViewSet, SurfaceTypeViewSet,
    ApartmentViewSet, LandViewSet, CommercialSpaceViewSet, HouseViewSet,
    DeleteLandView, DeleteHouseView, DeleteApartmentView, DeleteCommercialView
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'requests', RequestViewSet, basename='request')
router.register(r'conditions', ConditionViewSet)
router.register(r'property-types', PropertyTypeViewSet)
router.register(r'sectors', SectorViewSet)
router.register(r'locations', LocationViewSet)
router.register(r'listings', ListingViewSet, basename='listing')
router.register(r'messages', MessageViewSet)
router.register(r'heating-types', HeatingTypeViewSet)
router.register(r'planning-types', PlanningTypeViewSet)
router.register(r'construction-types', ConstructionTypeViewSet)
router.register(r'surface-types', SurfaceTypeViewSet)
router.register(r'apartments', ApartmentViewSet)
router.register(r'houses', HouseViewSet)
router.register(r'lands', LandViewSet)
router.register(r'commercial-spaces', CommercialSpaceViewSet)

images_router = routers.NestedDefaultRouter(router, r'listings', lookup='listing')
images_router.register(r'images', ListingImageViewSet, basename='listing-images')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(images_router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', get_user_data, name='get-user-data'),
    path('user-types/', get_user_types, name='get-user-types'),
    path('sale-types/', get_sale_types, name='get-sale-types'),
    path('password-reset/request/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset/confirm/<uidb64>/<token>/', PasswordResetView.as_view(), name='password-reset-confirm'),
    path('delete-land/<int:listing_id>/', DeleteLandView.as_view(), name='delete-land'),
    path('delete-house/<int:listing_id>/', DeleteHouseView.as_view(), name='delete-house'),
    path('delete-apartment/<int:listing_id>/', DeleteApartmentView.as_view(), name='delete-apartment'),
    path('delete-commercial/<int:listing_id>/', DeleteCommercialView.as_view(), name='delete-commercial-space'),
]