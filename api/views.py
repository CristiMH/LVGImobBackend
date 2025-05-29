from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from django.db.models import Max
from .models import (
    Request, SaleType, User, Condition, PropertyType, Sector, Location, UserType, Listing, ListingImage,
    Message, House, HeatingType, PlanningType, ConstructionType, SurfaceType, Apartment, Land,
    CommercialSpace
)
from rest_framework.exceptions import MethodNotAllowed
from .serializers import (
    RequestSerializer, SaleTypeSerializer, UserSerializer, PasswordResetRequestSerializer, PasswordResetSerializer,
    ConditionSerializer, PropertyTypeSerializer, SectorSerializer, LocationSerializer,
    UserTypeSerializer, ListingImageSerializer, ListingSerializer, MessageSerializer,
    HouseSerializer, HeatingTypeSerializer, PlanningTypeSerializer, ConstructionTypeSerializer,
    SurfaceTypeSerializer, ApartmentSerializer, LandSerializer, CommercialSpaceSerializer
)
from .permissions import CanUpdateUser, IsUserType2Or3, IsOwnerOfListing  
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Q
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework import generics, status
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_str, force_bytes
from rest_framework import filters
from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, NumberFilter, BooleanFilter
from rest_framework.views import APIView
from django.db import transaction

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_data(request):
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_types(request):
    user_types = UserType.objects.all()
    serializer = UserTypeSerializer(user_types, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_sale_types(request):
    sale_types = SaleType.objects.all()
    serializer = SaleTypeSerializer(sale_types, many=True)
    return Response(serializer.data)

class DeleteLandView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOfListing]

    def delete(self, request, listing_id, *args, **kwargs):
        try:
            listing = Listing.objects.get(id=listing_id)
            land = Land.objects.get(listing_id=listing_id)

            self.check_object_permissions(request, land)

            with transaction.atomic():
                ListingImage.objects.filter(listing_id=listing_id).delete()
                Land.objects.get(listing_id=listing_id).delete()
                listing.delete()

            return Response({"detail": "Succes"}, status=status.HTTP_204_NO_CONTENT)

        except Listing.DoesNotExist:
            return Response({"error": "Anunțul nu a fost găsit."}, status=status.HTTP_404_NOT_FOUND)
        except Land.DoesNotExist:
            return Response({"error": "Terenul nu a fost găsit."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Eroare la ștergerea anunțului: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        
class DeleteHouseView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOfListing]

    def delete(self, request, listing_id, *args, **kwargs):
        try:
            listing = Listing.objects.get(id=listing_id)
            house = House.objects.get(listing_id=listing_id)

            self.check_object_permissions(request, house)

            with transaction.atomic():
                ListingImage.objects.filter(listing_id=listing_id).delete()
                House.objects.get(listing_id=listing_id).delete()
                listing.delete()

            return Response({"detail": "Succes"}, status=status.HTTP_204_NO_CONTENT)

        except Listing.DoesNotExist:
            return Response({"error": "Anunțul nu a fost găsit."}, status=status.HTTP_404_NOT_FOUND)
        except Land.DoesNotExist:
            return Response({"error": "Casa nu a fost găsită."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Eroare la ștergerea anunțului: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        
class DeleteApartmentView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOfListing]

    def delete(self, request, listing_id, *args, **kwargs):
        try:
            listing = Listing.objects.get(id=listing_id)
            apartment = Apartment.objects.get(listing_id=listing_id)

            self.check_object_permissions(request, apartment)

            with transaction.atomic():
                ListingImage.objects.filter(listing_id=listing_id).delete()
                Apartment.objects.get(listing_id=listing_id).delete()
                listing.delete()

            return Response({"detail": "Succes"}, status=status.HTTP_204_NO_CONTENT)

        except Listing.DoesNotExist:
            return Response({"error": "Anunțul nu a fost găsit."}, status=status.HTTP_404_NOT_FOUND)
        except Land.DoesNotExist:
            return Response({"error": "Apartamentul nu a fost găsit."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Eroare la ștergerea anunțului: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        
class DeleteCommercialView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOfListing]

    def delete(self, request, listing_id, *args, **kwargs):
        try:
            listing = Listing.objects.get(id=listing_id)
            com = CommercialSpace.objects.get(listing_id=listing_id)

            self.check_object_permissions(request, com)

            with transaction.atomic():
                ListingImage.objects.filter(listing_id=listing_id).delete()
                CommercialSpace.objects.get(listing_id=listing_id).delete()
                listing.delete()

            return Response({"detail": "Succes"}, status=status.HTTP_204_NO_CONTENT)

        except Listing.DoesNotExist:
            return Response({"error": "Anunțul nu a fost găsit."}, status=status.HTTP_404_NOT_FOUND)
        except Land.DoesNotExist:
            return Response({"error": "Spațiul comercial nu a fost găsit."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Eroare la ștergerea anunțului: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    ordering_fields = ['last_name', 'first_name', 'last_login']
    filter_backends = [filters.OrderingFilter]
    ordering = ['last_name']
    permission_classes=[CanUpdateUser, IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')

        if search:
            search_terms = search.strip().lower().split()

            if len(search_terms) == 1:
                term = search_terms[0]
                queryset = queryset.filter(
                    Q(first_name__icontains=term) | Q(last_name__icontains=term)
                )
            elif len(search_terms) == 2:
                first_term, last_term = search_terms
                queryset = queryset.filter(
                    (Q(first_name__icontains=first_term) & Q(last_name__icontains=last_term)) |
                    (Q(first_name__icontains=last_term) & Q(last_name__icontains=first_term))
                )
            else:
                queryset = queryset.none()

        return queryset

class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = User.objects.get(email=serializer.validated_data['email'])
        token_generator = PasswordResetTokenGenerator()
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)
        
        reset_link = f"http://localhost:3000/resetare-parola/{uid}/{token}"
        send_mail(
            'Resetare parolă',
            f'Apasă pe linkul următor pentru a-ți reseta parola: {reset_link}',
            'noreply@example.com',
            [user.email],
            fail_silently=False,
        )
        
        return Response({"detail": "Linkul de resetare a fost trimis prin email."}, status=status.HTTP_200_OK)
    
class PasswordResetView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"detail": "ID-ul sau token-ul este invalid."}, status=status.HTTP_400_BAD_REQUEST)
        
        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(user, token):
            return Response({"detail": "Token invalid sau expirat."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({"detail": "Parola a fost resetată cu succes."}, status=status.HTTP_200_OK)
    
class ConditionViewSet(viewsets.ModelViewSet):
    queryset = Condition.objects.all()
    serializer_class = ConditionSerializer
    pagination_class = None

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [AllowAny()]

class PropertyTypeViewSet(viewsets.ModelViewSet):
    queryset = PropertyType.objects.all()
    serializer_class = PropertyTypeSerializer
    pagination_class = None
    
    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        raise MethodNotAllowed(self.action)
    
    def retrieve(self, request, *args, **kwargs):
        raise MethodNotAllowed('retrieve')

    def create(self, request, *args, **kwargs):
        raise MethodNotAllowed('create')

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed('update')

    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed('partial_update')

    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed('destroy')

class SectorViewSet(viewsets.ModelViewSet):
    queryset = Sector.objects.all()
    serializer_class = SectorSerializer
    pagination_class = None
    
    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated(), IsUserType2Or3()]

class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    pagination_class = None
    
    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated(), IsUserType2Or3()]

class RequestViewSet(viewsets.ModelViewSet):
    queryset = Request.objects.all().order_by('-created_at')
    serializer_class = RequestSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        request = serializer.save()
        
        send_mail(
            "Cerere nouă",
            f"Ai primit o cerere nouă de la {request.first_name} {request.last_name}",
            'noreply@example.com',
            ['uiprime61@gmail.com'], #email of the company
            fail_silently=False,
        )
    
class ListingImageViewSet(viewsets.ViewSet):
    
    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request, listing_pk=None):
        listing = get_object_or_404(Listing, pk=listing_pk)
        images = listing.images.all()
        serializer = ListingImageSerializer(images, many=True, context={'request': request})
        return Response(serializer.data)

    def create(self, request, listing_pk=None):
        listing = get_object_or_404(Listing, pk=listing_pk)
        if listing.user != request.user:
            return Response({'detail': 'Nu ai permisiunea să modifici acest anunț.'}, status=403)

        image_file = request.FILES.get('image')
        if not image_file:
            return Response({'error': 'Fișierul este necesar.'}, status=400)

        image = ListingImage.objects.create(
            listing=listing,
            image=image_file
        )
        serializer = ListingImageSerializer(image, context={'request': request})
        return Response(serializer.data, status=201)

    def destroy(self, request, pk=None, listing_pk=None):
        listing = get_object_or_404(Listing, pk=listing_pk)
        if listing.user != request.user:
            return Response({'detail': 'Nu ai permisiunea să modifici acest anunț.'}, status=403)

        image = get_object_or_404(ListingImage, pk=pk, listing__pk=listing_pk)
        image.delete()
        return Response(status=204)

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all().select_related(
        'location', 'sector', 'sale_type', 'property_type', 'user'
    ).prefetch_related('images')
    serializer_class = ListingSerializer
    permission_classes=[IsAuthenticated, IsOwnerOfListing]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        return Response(
            {"detail": "Not allowed."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed('delete')

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all().order_by('-created_at')
    serializer_class = MessageSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        message = serializer.save()
        send_mail(
            f"Mesaj nou: {message.subject}",
            f"Ai primit un mesaj nou de la {message.name}\n\nEmail: {message.email}\nTelefon: {message.phone}\nSubiect: {message.subject}\n\nMesaj:\n{message.message}",
            'noreply@example.com',
            ['lvgimob1@gmail.com'],
            fail_silently=False,
        )
    
    def update(self, request, *args, **kwargs):
        return Response({"detail": "Updates are not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response({"detail": "Partial updates are not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
class HouseFilter(FilterSet):
    surface = NumberFilter()
    min_surface = NumberFilter(field_name='surface', lookup_expr='gte')
    max_surface = NumberFilter(field_name='surface', lookup_expr='lte')
    land_surface = NumberFilter()
    min_land_surface = NumberFilter(field_name='land_surface', lookup_expr='gte')
    max_land_surface = NumberFilter(field_name='land_surface', lookup_expr='lte')
    rooms = NumberFilter()
    min_rooms = NumberFilter(field_name='rooms', lookup_expr='gte')
    max_rooms = NumberFilter(field_name='rooms', lookup_expr='lte')
    total_floors = NumberFilter()
    bathrooms = NumberFilter()
    water_installation = BooleanFilter()
    gas_installation = BooleanFilter()
    sewerage_installation = BooleanFilter()

    price_min = NumberFilter(field_name='listing__price', lookup_expr='gte')
    price_max = NumberFilter(field_name='listing__price', lookup_expr='lte')
    availability = BooleanFilter(field_name='listing__availability')
    location = NumberFilter(field_name='listing__location')
    sector = NumberFilter(field_name='listing__sector')
    sale_type = NumberFilter(field_name='listing__sale_type')
    property_type = NumberFilter(field_name='listing__property_type')

    class Meta:
        model = House
        fields = [
            'surface',
            'land_surface',
            'rooms',
            'total_floors',
            'bathrooms',
            'water_installation',
            'gas_installation',
            'sewerage_installation',

            'listing__price',
            'listing__availability',
            'listing__location',
            'listing__sector',
            'listing__sale_type',
            'listing__property_type',
        ]

class HouseViewSet(viewsets.ModelViewSet):
    queryset = House.objects.select_related(
        'listing',
        'listing__location',
        'listing__sector',
        'listing__sale_type',
        'listing__property_type',
        'listing__user',
    ).prefetch_related('listing__images')
    serializer_class = HouseSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = HouseFilter

    ordering_fields = [
        'listing__price',
        'listing__created_at',
        'listing__modified_at',
        'listing__availability'
    ]
    ordering = ['-listing__created_at']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated(), IsOwnerOfListing()]
    
    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed('delete')

class HeatingTypeViewSet(viewsets.ModelViewSet):
    queryset = HeatingType.objects.all()
    serializer_class = HeatingTypeSerializer
    pagination_class = None
    
    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated(), IsUserType2Or3()]
    
class PlanningTypeViewSet(viewsets.ModelViewSet):
    queryset = PlanningType.objects.all()
    serializer_class = PlanningTypeSerializer
    pagination_class = None
    
    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated(), IsUserType2Or3()]
    
class ConstructionTypeViewSet(viewsets.ModelViewSet):
    queryset = ConstructionType.objects.all()
    serializer_class = ConstructionTypeSerializer
    pagination_class = None
    
    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated(), IsUserType2Or3()]
    
class SurfaceTypeViewSet(viewsets.ModelViewSet):
    queryset = SurfaceType.objects.all()
    serializer_class = SurfaceTypeSerializer
    pagination_class = None
    
    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated(), IsUserType2Or3()]
    
class ApartmentFilter(FilterSet):
    surface = NumberFilter()
    min_surface = NumberFilter(field_name='surface', lookup_expr='gte')
    max_surface = NumberFilter(field_name='surface', lookup_expr='lte')
    rooms = NumberFilter()
    min_rooms = NumberFilter(field_name='rooms', lookup_expr='gte')
    max_rooms = NumberFilter(field_name='rooms', lookup_expr='lte')
    floor = NumberFilter()
    min_floor = NumberFilter(field_name='floor', lookup_expr='gte')
    max_floor = NumberFilter(field_name='floor', lookup_expr='lte')
    total_floors = NumberFilter()
    bathrooms = NumberFilter()
    condition = NumberFilter(field_name='condition')
    construction_type = NumberFilter(field_name='construction_type')
    planning_type = NumberFilter(field_name='planning_type')
    heating_type = NumberFilter(field_name='heating_type')

    price_min = NumberFilter(field_name='listing__price', lookup_expr='gte')
    price_max = NumberFilter(field_name='listing__price', lookup_expr='lte')
    availability = BooleanFilter(field_name='listing__availability')
    location = NumberFilter(field_name='listing__location')
    sector = NumberFilter(field_name='listing__sector')
    sale_type = NumberFilter(field_name='listing__sale_type')
    property_type = NumberFilter(field_name='listing__property_type')

    class Meta:
        model = Apartment
        fields = [
            'surface', 'rooms', 'floor', 'total_floors', 'bathrooms',
            'condition', 'construction_type', 'planning_type', 'heating_type',

            'listing__price', 'listing__availability',
            'listing__location', 'listing__sector',
            'listing__sale_type', 'listing__property_type',
        ]

class ApartmentViewSet(viewsets.ModelViewSet):
    queryset = Apartment.objects.select_related(
        'listing',
        'listing__location',
        'listing__sector',
        'listing__sale_type',
        'listing__property_type',
        'listing__user',
        'condition',
        'construction_type',
        'planning_type',
        'heating_type'
    ).prefetch_related('listing__images')
    serializer_class = ApartmentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ApartmentFilter

    ordering_fields = [
        'listing__price',
        'listing__created_at',
        'listing__modified_at',
        'listing__availability'
    ]
    ordering = ['-listing__created_at']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated(), IsOwnerOfListing()]
    
    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed('delete')

class LandFilter(FilterSet):
    land_surface = NumberFilter()
    min_land_surface = NumberFilter(field_name='land_surface', lookup_expr='gte')
    max_land_surface = NumberFilter(field_name='land_surface', lookup_expr='lte')
    surface_type = NumberFilter(field_name='surface_type')

    price_min = NumberFilter(field_name='listing__price', lookup_expr='gte')
    price_max = NumberFilter(field_name='listing__price', lookup_expr='lte')
    availability = BooleanFilter(field_name='listing__availability')
    location = NumberFilter(field_name='listing__location')
    sector = NumberFilter(field_name='listing__sector')
    sale_type = NumberFilter(field_name='listing__sale_type')
    property_type = NumberFilter(field_name='listing__property_type')

    class Meta:
        model = Land
        fields = [
            'land_surface', 'surface_type',

            'listing__price', 'listing__availability',
            'listing__location', 'listing__sector',
            'listing__sale_type', 'listing__property_type',
        ]

class LandViewSet(viewsets.ModelViewSet):
    queryset = Land.objects.select_related(
        'listing',
        'listing__location',
        'listing__sector',
        'listing__sale_type',
        'listing__property_type',
        'listing__user',
        'surface_type'
    ).prefetch_related('listing__images')
    serializer_class = LandSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = LandFilter

    ordering_fields = [
        'listing__price',
        'listing__created_at'
    ]
    ordering = ['-listing__created_at']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated(), IsOwnerOfListing()]
    
    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed('delete')
    
class CommercialSpaceFilter(FilterSet):
    surface = NumberFilter()
    min_surface = NumberFilter(field_name='surface', lookup_expr='gte')
    max_surface = NumberFilter(field_name='surface', lookup_expr='lte')
    condition = NumberFilter(field_name='condition')
    floor = NumberFilter()
    min_floor = NumberFilter(field_name='floor', lookup_expr='gte')
    max_floor = NumberFilter(field_name='floor', lookup_expr='lte')
    offices = NumberFilter()
    min_offices = NumberFilter(field_name='offices', lookup_expr='gte')
    max_offices = NumberFilter(field_name='offices', lookup_expr='lte')
    bathrooms = NumberFilter()

    price_min = NumberFilter(field_name='listing__price', lookup_expr='gte')
    price_max = NumberFilter(field_name='listing__price', lookup_expr='lte')
    availability = BooleanFilter(field_name='listing__availability')
    location = NumberFilter(field_name='listing__location')
    sector = NumberFilter(field_name='listing__sector')
    sale_type = NumberFilter(field_name='listing__sale_type')
    property_type = NumberFilter(field_name='listing__property_type')

    class Meta:
        model = CommercialSpace
        fields = [
            'surface', 'condition', 'floor', 'offices', 'bathrooms',

            'listing__price', 'listing__availability',
            'listing__location', 'listing__sector',
            'listing__sale_type', 'listing__property_type',
        ]

class CommercialSpaceViewSet(viewsets.ModelViewSet):
    queryset = CommercialSpace.objects.select_related(
        'listing',
        'listing__location',
        'listing__sector',
        'listing__sale_type',
        'listing__property_type',
        'listing__user',
        'condition'
    ).prefetch_related('listing__images')
    serializer_class = CommercialSpaceSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = CommercialSpaceFilter

    ordering_fields = [
        'listing__price',
        'listing__created_at',
        'listing__modified_at',
        'listing__availability'
    ]
    ordering = ['-listing__created_at']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated(), IsOwnerOfListing()]
    
    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed('delete')