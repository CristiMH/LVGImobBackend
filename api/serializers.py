from rest_framework import serializers, exceptions
from django.core.validators import RegexValidator
from .models import (
    User, UserType, SaleType, ListingImage, Message,
    Condition, PropertyType, Sector, Location, Request, Listing, ListingImage, 
    House, HeatingType, PlanningType, ConstructionType, SurfaceType,
    Apartment, Land, CommercialSpace
)
from django.db import transaction
from django.core.files.base import ContentFile
from urllib.request import urlopen
from urllib.parse import urlparse
import os

password_validator = RegexValidator(
    r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,}$',
    message="Parola trebuie să conțină cel puțin 8 caractere, o literă mare, o literă mică, un număr și un caracter special."
)

phone_validator = RegexValidator(
    regex=r'^\+?[\d\s()-]{7,15}$',
    message="Numărul de telefon nu este valid. Ex: +37369123456"
)

# User Serializers
class UserTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model=UserType
        fields='__all__'

class UserSerializer(serializers.ModelSerializer):

    first_name = serializers.CharField(
        error_messages={
            'blank': 'Acest câmp nu poate fi gol.'
        }
    )
    last_name = serializers.CharField(
        error_messages={
            'blank': 'Acest câmp nu poate fi gol.'
        }
    )
    password = serializers.CharField(
        write_only=True,
        validators=[password_validator]
    )

    user_type_id = serializers.PrimaryKeyRelatedField(
        source='user_type',
        queryset=UserType.objects.all(),
        write_only=True,
        error_messages={
            'does_not_exist': 'Tipul indicat specificat nu există.',
            'incorrect_type': 'Valoarea trimisă trebuie să fie un ID numeric.',
            'blank': 'Acest câmp nu poate fi gol.',
            'required': 'Acest câmp nu poate fi gol.',
            'null': 'Acest câmp nu poate fi gol.'
        }
    )

    user_type = UserTypeSerializer(read_only=True)

    class Meta:
        model=User
        fields=['id', 'first_name', 'last_name', 'username', 'email', 'phone', 'password', 'user_type_id', 'user_type', 'modified_at', 'date_joined', 'is_active']
        read_only_fields=['id', 'modified_at', 'date_joined']

    def validate_email(self, value):
        user_id = self.instance.id if self.instance else None
        if User.objects.filter(email=value).exclude(id=user_id).exists():
            raise serializers.ValidationError("Acest email este deja folosit de un alt utilizator.")
        return value
    
    
    def validate_phone(self, value):
        user_id = self.instance.id if self.instance else None
        if User.objects.filter(phone=value).exclude(id=user_id).exists():
            raise serializers.ValidationError("Acest număr de telefon este deja folosit de un alt utilizator.")
        return value

    def create(self, validated_data):
        validated_data.pop('is_active', None)
        pwd = validated_data.pop('password')
        
        user = User(**validated_data)
        user.is_active = True
        user.set_password(pwd)
        user.save()

        return user
    
    def update(self, instance, validated_data):
        pwd = validated_data.pop('password', None)
        if pwd:
            instance.set_password(pwd)

        return super().update(instance, validated_data)
    
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Acest email nu este asociat niciunui utilizator.")
        return value
    
class PasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        write_only=True,
        validators=[password_validator]        
    )

class ImageOrUrlField(serializers.Field):
    def to_internal_value(self, data):
        if hasattr(data, 'read'):
            return data  # it's a file
        elif isinstance(data, str):
            return data  # it's a URL
        raise serializers.ValidationError("Invalid image data")

    def to_representation(self, value):
        return value.url
# Request serializers
class ConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Condition
        fields='__all__'

class PropertyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model=PropertyType
        fields='__all__'

class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model=Sector
        fields="__all__"

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model=Location
        fields="__all__"

class RequestSerializer(serializers.ModelSerializer):
    condition_id = serializers.PrimaryKeyRelatedField(
        source='condition',
        queryset=Condition.objects.all(),
        write_only=True,
        error_messages={
            'does_not_exist': 'Condiția specificată nu există.',
            'incorrect_type': 'Valoarea trimisă trebuie să fie un ID numeric.',
            'blank': 'Acest câmp nu poate fi gol.',
            'required': 'Acest câmp nu poate fi gol.',
            'null': 'Acest câmp nu poate fi gol.'
        }
    )
    condition = ConditionSerializer(read_only=True)

    property_type_id = serializers.PrimaryKeyRelatedField(
        source='property_type',
        queryset=PropertyType.objects.all(),
        write_only=True,
        error_messages={
            'does_not_exist': 'Tipul de proprietate specificat nu există.',
            'incorrect_type': 'Valoarea trimisă trebuie să fie un ID numeric.',
            'blank': 'Acest câmp nu poate fi gol.',
            'required': 'Acest câmp nu poate fi gol.',
            'null': 'Acest câmp nu poate fi gol.'
        }
    )
    property_type = PropertyTypeSerializer(read_only=True)

    sector_id = serializers.PrimaryKeyRelatedField(
        source='sector',
        queryset=Sector.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
        error_messages={
            'does_not_exist': 'Sectorul specificat nu există.',
            'incorrect_type': 'Valoarea trimisă trebuie să fie un ID numeric.',
            'null': 'Sectorul este obligatoriu dacă locația este Chișinău.'
        }
    )
    sector = SectorSerializer(read_only=True)

    location_id = serializers.PrimaryKeyRelatedField(
        source='location',
        queryset=Location.objects.all(),
        write_only=True,
        error_messages={
            'does_not_exist': 'Locația specificată nu există.',
            'incorrect_type': 'Valoarea trimisă trebuie să fie un ID numeric.',
            'blank': 'Acest câmp nu poate fi gol.',
            'required': 'Acest câmp nu poate fi gol.',
            'null': 'Acest câmp nu poate fi gol.'
        }
    )
    location = LocationSerializer(read_only=True)

    first_name = serializers.CharField(
        error_messages={
            'blank': 'Acest câmp nu poate fi gol.'
        }
    )
    last_name = serializers.CharField(
        error_messages={
            'blank': 'Acest câmp nu poate fi gol.'
        }
    )
    phone = serializers.CharField(
        validators=[phone_validator],
        error_messages={'blank': 'Acest câmp nu poate fi gol.'}
    )
    email = serializers.EmailField(
        error_messages={
            'invalid': 'Adresa de email nu este validă.',
            'blank': 'Acest câmp nu poate fi gol.'
        }
    )

    estimated_price = serializers.IntegerField(
        error_messages={
            'required': 'Acest câmp nu poate fi gol.',
            'invalid': 'Valoarea trebuie să fie un număr întreg valid.'
        }
    )

    def validate_estimated_price(self, value):
        if value <= 0:
            raise serializers.ValidationError('Introduceți o valoare mai mare ca 0')
        return value

    class Meta:
        model=Request
        fields = [
            'id', 'first_name', 'last_name', 'phone', 'email', 'location_id', 'location', 'sector_id', 'sector',
            'property_type_id', 'property_type', 'condition_id', 'condition', 'estimated_price', 'note', 
            'approved', 'created_at'
        ]
        read_only_fields = ['created_at']

    def validate_sector_id(self, value):
        location_id = self.initial_data.get("location_id")
        location = Location.objects.filter(id=location_id).first()

        if location:
            if location.location == 'Chișinău' and not value:
                raise serializers.ValidationError('Sectorul este obligatoriu când locația este Chișinău.')
            if location.location != 'Chișinău' and value:
                raise serializers.ValidationError('Sectorul trebuie să fie necompletat când locația nu este Chișinău.')

        return value
        
    def create(self, validated_data):
        validated_data.pop('approved', None)

        request = Request(**validated_data)
        request.approved = False
        request.save()

        return request
    
class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model=Message
        fields='__all__'
        read_only_fields=['created_at']

# Listing serializers
class SaleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model=SaleType
        fields='__all__'

class ListingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model=ListingImage
        fields='__all__'

class ListingSerializer(serializers.ModelSerializer):
    sector_id = serializers.PrimaryKeyRelatedField(
        source='sector',
        queryset=Sector.objects.all(),
        write_only=True,
        required=False,
        allow_null=True, 
        error_messages={
            'does_not_exist': 'Sectorul specificat nu există.',
            'incorrect_type': 'Valoarea trimisă trebuie să fie un ID numeric.',
            'null': 'Sectorul este obligatoriu dacă locația este Chișinău.'
        }
    )
    sector = SectorSerializer(read_only=True)

    location_id = serializers.PrimaryKeyRelatedField(
        source='location',
        queryset=Location.objects.all(),
        write_only=True,
        error_messages={
            'does_not_exist': 'Locația specificată nu există.',
            'incorrect_type': 'Acest câmp nu poate fi gol.',
            'blank': 'Acest câmp nu poate fi gol.',
            'required': 'Acest câmp nu poate fi gol.',
            'null': 'Acest câmp nu poate fi gol.'
        }
    )
    location = LocationSerializer(read_only=True)

    user_id = serializers.PrimaryKeyRelatedField(
        source='user',
        queryset=User.objects.all(),
        write_only=True,
        error_messages={
            'does_not_exist': 'Agentul specificat nu există.',
            'incorrect_type': 'Valoarea trimisă trebuie să fie un ID numeric.',
            'blank': 'Acest câmp nu poate fi gol.',
            'required': 'Acest câmp nu poate fi gol.',
            'null': 'Acest câmp nu poate fi gol.'
        }
    )
    user = UserSerializer(read_only=True)

    sale_type_id = serializers.PrimaryKeyRelatedField(
        source='sale_type',
        queryset=SaleType.objects.all(),
        write_only=True,
        error_messages={
            'does_not_exist': 'Tipul specificat nu există.',
            'incorrect_type': 'Acest câmp nu poate fi gol.',
            'blank': 'Acest câmp nu poate fi gol.',
            'required': 'Acest câmp nu poate fi gol.',
            'null': 'Acest câmp nu poate fi gol.'
        }
    )
    sale_type = SaleTypeSerializer(read_only=True)

    property_type_id = serializers.PrimaryKeyRelatedField(
        source='property_type',
        queryset=PropertyType.objects.all(),
        write_only=True,
        error_messages={
            'does_not_exist': 'Tipul de proprietate specificat nu există.',
            'incorrect_type': 'Valoarea trimisă trebuie să fie un ID numeric.',
            'blank': 'Acest câmp nu poate fi gol.',
            'required': 'Acest câmp nu poate fi gol.',
            'null': 'Acest câmp nu poate fi gol.'
        }
    )
    property_type = PropertyTypeSerializer(read_only=True)

    images_input = serializers.ListField(
        child=ImageOrUrlField(),
        write_only=True,
        required=False
    )
    images = serializers.SerializerMethodField(read_only=True)

    street = serializers.CharField(
        error_messages={
            'blank': 'Acest câmp nu poate fi gol.',
            'required': 'Acest câmp nu poate fi gol.',
            'null': 'Acest câmp nu poate fi gol.'
        }
    )
    description = serializers.CharField(
        error_messages={
            'blank': 'Acest câmp nu poate fi gol.'
        }
    )

    availability = serializers.BooleanField(
        required=True,
        allow_null=False,
        error_messages={
            'required': 'Acest câmp nu poate fi gol.',
            'invalid': 'Acest câmp nu poate fi gol.'
        }
    )

    class Meta:
        model=Listing
        fields = [
            'id', 'street', 'description', 'price', 'availability', 'location_id', 'location',
            'sector_id', 'sector', 'user_id', 'user', 'sale_type_id', 'sale_type',
            'property_type_id', 'property_type', 'images', 'images_input', 'created_at', 'modified_at'
        ]
        read_only_fields=['created_at', 'modified_at']

    def get_images(self, obj):
        request = self.context.get('request')
        return [
            request.build_absolute_uri(img.image.url)
            for img in obj.images.all()
            if img.image and hasattr(img.image, 'path') and os.path.isfile(img.image.path)
        ]
    
    def validate(self, attrs):
        location = attrs.get("location")
        sector = attrs.get("sector")

        if location and location.location == "Chișinău" and not sector:
            raise serializers.ValidationError({
                "sector_id": "Sectorul este obligatoriu când locația este Chișinău."
            })

        if location and location.location != "Chișinău" and sector:
            raise serializers.ValidationError({
                "sector_id": "Sectorul trebuie să fie necompletat când locația nu este Chișinău."
            })

        return attrs
    
    def create(self, validated_data):
        images_data = validated_data.pop('images_input', [])

        with transaction.atomic():
            listing = Listing.objects.create(**validated_data)

            for i, image_file in enumerate(images_data):
                ListingImage.objects.create(
                    listing=listing,
                    image=image_file
                )

        return listing
    
    def update(self, instance, validated_data):
        validated_data.pop('images_input', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance   

class HouseSerializer(serializers.ModelSerializer):
    listing_data = ListingSerializer(write_only=True)
    listing = ListingSerializer(read_only=True)

    water_installation = serializers.BooleanField(
        required=True,
        allow_null=False,
        error_messages={
            'required': 'Acest câmp nu poate fi gol.',
            'invalid': 'Acest câmp nu poate fi gol.'
        }
    )

    gas_installation = serializers.BooleanField(
        required=True,
        allow_null=False,
        error_messages={
            'required': 'Acest câmp nu poate fi gol.',
            'invalid': 'Acest câmp nu poate fi gol.'
        }
    )

    sewerage_installation = serializers.BooleanField(
        required=True,
        allow_null=False,
        error_messages={
            'required': 'Acest câmp nu poate fi gol.',
            'invalid': 'Acest câmp nu poate fi gol.'
        }
    )

    class Meta:
        model=House
        fields=['id', 'listing', 'listing_data', 'surface', 'land_surface', 'rooms', 'total_floors',
                'bathrooms', 'water_installation', 'gas_installation', 'sewerage_installation']
        
    def create(self, validated_data):
        listing_data = validated_data.pop('listing_data')
        images_data = listing_data.pop('images_input', [])

        with transaction.atomic():
            listing = Listing.objects.create(**listing_data)

            for image in images_data:
                ListingImage.objects.create(listing=listing, image=image)

            house = House.objects.create(listing=listing, **validated_data)

        return house
    
    def update(self, instance, validated_data):
        listing_data = validated_data.pop('listing_data', None)

        with transaction.atomic():
            if listing_data:
                images_data = listing_data.pop('images_input', None)
                listing = instance.listing

                for attr, value in listing_data.items():
                    setattr(listing, attr, value)
                listing.save()

                if images_data is not None:
                    existing_image_names = set()
                    new_images = []

                    for image in images_data:
                        if hasattr(image, 'read'):
                            new_images.append(image)
                        elif isinstance(image, str):
                            filename = os.path.basename(urlparse(image).path)
                            existing_image_names.add(f"imagini_anunturi/{filename}")

                    for img in listing.images.all():
                        if img.image.name not in existing_image_names:
                            img.delete()

                for image in new_images:
                    ListingImage.objects.create(listing=listing, image=image)

            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

        return instance
        
class HeatingTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model=HeatingType
        fields='__all__'

class PlanningTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model=PlanningType
        fields='__all__'

class ConstructionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model=ConstructionType
        fields='__all__'

class SurfaceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model=SurfaceType
        fields='__all__'

class ApartmentSerializer(serializers.ModelSerializer):
    listing_data = ListingSerializer(write_only=True)
    listing = ListingSerializer(read_only=True)

    condition_id = serializers.PrimaryKeyRelatedField(
        source='condition',
        queryset=Condition.objects.all(),
        write_only=True,
        error_messages={
            'does_not_exist': 'Condiția specificată nu există.',
            'incorrect_type': 'Valoarea trimisă trebuie să fie un ID numeric.',
            'blank': 'Acest câmp nu poate fi gol.',
            'required': 'Acest câmp nu poate fi gol.',
            'null': 'Acest câmp nu poate fi gol.'
        }
    )
    condition = ConditionSerializer(read_only=True)

    construction_type_id = serializers.PrimaryKeyRelatedField(
        source='construction_type',
        queryset=ConstructionType.objects.all(),
        write_only=True,
        error_messages={
            'does_not_exist': 'Tipul specificat nu există.',
            'incorrect_type': 'Valoarea trimisă trebuie să fie un ID numeric.',
            'blank': 'Acest câmp nu poate fi gol.',
            'required': 'Acest câmp nu poate fi gol.',
            'null': 'Acest câmp nu poate fi gol.'
        }
    )
    construction_type = ConstructionTypeSerializer(read_only=True)

    planning_type_id = serializers.PrimaryKeyRelatedField(
        source='planning_type',
        queryset=PlanningType.objects.all(),
        write_only=True,
        error_messages={
            'does_not_exist': 'Tipul specificat nu există.',
            'incorrect_type': 'Valoarea trimisă trebuie să fie un ID numeric.',
            'blank': 'Acest câmp nu poate fi gol.',
            'required': 'Acest câmp nu poate fi gol.',
            'null': 'Acest câmp nu poate fi gol.'
        }
    )
    planning_type = PlanningTypeSerializer(read_only=True)

    heating_type_id = serializers.PrimaryKeyRelatedField(
        source='heating_type',
        queryset=HeatingType.objects.all(),
        write_only=True,
        error_messages={
            'does_not_exist': 'Tipul specificat nu există.',
            'incorrect_type': 'Valoarea trimisă trebuie să fie un ID numeric.',
            'blank': 'Acest câmp nu poate fi gol.',
            'required': 'Acest câmp nu poate fi gol.',
            'null': 'Acest câmp nu poate fi gol.'
        }
    )
    heating_type = HeatingTypeSerializer(read_only=True)

    class Meta:
        model=Apartment
        fields=['id', 'listing_data', 'listing', 'surface', 'condition_id', 'condition', 'construction_type_id',
                'construction_type', 'planning_type_id', 'planning_type', 'rooms', 'floor', 'total_floors',
                'bathrooms', 'heating_type', 'heating_type_id']
        
    def create(self, validated_data):
        listing_data = validated_data.pop('listing_data')
        images_data = listing_data.pop('images_input', [])

        with transaction.atomic():
            listing = Listing.objects.create(**listing_data)

            for image in images_data:
                ListingImage.objects.create(listing=listing, image=image)

            apart = Apartment.objects.create(listing=listing, **validated_data)

        return apart
    
    def update(self, instance, validated_data):
        listing_data = validated_data.pop('listing_data', None)

        with transaction.atomic():
            if listing_data:
                images_data = listing_data.pop('images_input', None)
                listing = instance.listing

                for attr, value in listing_data.items():
                    setattr(listing, attr, value)
                listing.save()

                if images_data is not None:
                    existing_image_names = set()
                    new_images = []

                    for image in images_data:
                        if hasattr(image, 'read'):
                            new_images.append(image)
                        elif isinstance(image, str):
                            filename = os.path.basename(urlparse(image).path)
                            existing_image_names.add(f"imagini_anunturi/{filename}")

                    for img in listing.images.all():
                        if img.image.name not in existing_image_names:
                            img.delete()

                for image in new_images:
                    ListingImage.objects.create(listing=listing, image=image)

            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

        return instance
        
class LandSerializer(serializers.ModelSerializer):
    listing_data = ListingSerializer(write_only=True)
    listing = ListingSerializer(read_only=True)

    surface_type_id = serializers.PrimaryKeyRelatedField(
        source='surface_type',
        queryset=SurfaceType.objects.all(),
        write_only=True,
        error_messages={
            'does_not_exist': 'Tipul specificat nu există.',
            'incorrect_type': 'Valoarea trimisă trebuie să fie un ID numeric.',
            'blank': 'Acest câmp nu poate fi gol.',
            'required': 'Acest câmp nu poate fi gol.',
            'null': 'Acest câmp nu poate fi gol.'
        }
    )
    surface_type = SurfaceTypeSerializer(read_only=True)

    class Meta:
        model = Land
        fields = [
            'id', 'land_surface', 'surface_type_id', 'surface_type',
            'listing_data', 'listing'
        ]
        
    def create(self, validated_data):
        listing_data = validated_data.pop('listing_data')
        images_data = listing_data.pop('images_input', [])

        with transaction.atomic():
            listing = Listing.objects.create(**listing_data)

            for image in images_data:
                ListingImage.objects.create(listing=listing, image=image)

            land = Land.objects.create(listing=listing, **validated_data)

        return land

    def update(self, instance, validated_data):
        listing_data = validated_data.pop('listing_data', None)

        with transaction.atomic():
            if listing_data:
                images_data = listing_data.pop('images_input', None)
                listing = instance.listing

                # Update listing fields
                for attr, value in listing_data.items():
                    setattr(listing, attr, value)
                listing.save()

                # Replace all images
                if images_data is not None:
                    existing_image_names = set()
                    new_images = []

                    for image in images_data:
                        if hasattr(image, 'read'):
                            new_images.append(image)
                        elif isinstance(image, str):
                            # Extract file name from URL and build relative path
                            filename = os.path.basename(urlparse(image).path)
                            existing_image_names.add(f"imagini_anunturi/{filename}")

                    # Delete only removed images
                    for img in listing.images.all():
                        if img.image.name not in existing_image_names:
                            img.delete()

                # Add new images
                for image in new_images:
                    ListingImage.objects.create(listing=listing, image=image)

            # Update Land fields
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

        return instance

class CommercialSpaceSerializer(serializers.ModelSerializer):
    listing_data = ListingSerializer(write_only=True)
    listing = ListingSerializer(read_only=True)

    condition_id = serializers.PrimaryKeyRelatedField(
        source='condition',
        queryset=Condition.objects.all(),
        write_only=True,
        error_messages={
            'does_not_exist': 'Condiția specificată nu există.',
            'incorrect_type': 'Valoarea trimisă trebuie să fie un ID numeric.',
            'blank': 'Acest câmp nu poate fi gol.',
            'required': 'Acest câmp nu poate fi gol.',
            'null': 'Acest câmp nu poate fi gol.'
        }
    )
    condition = ConditionSerializer(read_only=True)

    class Meta:
        model=CommercialSpace
        fields=['id', 'listing_data', 'listing', 'surface', 'condition_id', 'condition','floor', 'offices', 'bathrooms']

    def create(self, validated_data):
        listing_data = validated_data.pop('listing_data')
        images_data = listing_data.pop('images_input', [])

        with transaction.atomic():
            listing = Listing.objects.create(**listing_data)

            for image in images_data:
                ListingImage.objects.create(listing=listing, image=image)

            com = CommercialSpace.objects.create(listing=listing, **validated_data)

        return com
    
    def update(self, instance, validated_data):
        listing_data = validated_data.pop('listing_data', None)

        with transaction.atomic():
            if listing_data:
                images_data = listing_data.pop('images_input', None)
                listing = instance.listing

                for attr, value in listing_data.items():
                    setattr(listing, attr, value)
                listing.save()

                if images_data is not None:
                    existing_image_names = set()
                    new_images = []

                    for image in images_data:
                        if hasattr(image, 'read'):
                            new_images.append(image)
                        elif isinstance(image, str):
                            filename = os.path.basename(urlparse(image).path)
                            existing_image_names.add(f"imagini_anunturi/{filename}")

                    for img in listing.images.all():
                        if img.image.name not in existing_image_names:
                            img.delete()

                for image in new_images:
                    ListingImage.objects.create(listing=listing, image=image)

            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

        return instance