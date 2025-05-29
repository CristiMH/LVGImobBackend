from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

phone_validator = RegexValidator(
    regex=r'^\+?[\d\s()-]{7,15}$',
    message="Numărul de telefon nu este valid. Ex: +37369123456"
)

# Lookup Tables
class PropertyType(models.Model): #done
    type = models.CharField(max_length=100)

    def __str__(self):
        return self.type

class Condition(models.Model): #done
    condition = models.CharField(max_length=100)

    def __str__(self):
        return self.condition

class SaleType(models.Model): #done
    type = models.CharField(max_length=100)

    def __str__(self):
        return self.type

class UserType(models.Model): #done
    type = models.CharField(max_length=100)

    def __str__(self):
        return self.type

class Sector(models.Model): #done
    sector = models.CharField(max_length=100)

    class Meta:
        ordering = ['sector']

    def __str__(self):
        return self.sector

class Location(models.Model): #done
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.location

class HeatingType(models.Model): #done
    type = models.CharField(max_length=100)

    def __str__(self):
        return self.type

class PlanningType(models.Model): #done
    type = models.CharField(max_length=100)

    def __str__(self):
        return self.type

class ConstructionType(models.Model): #done
    type = models.CharField(max_length=100)

    def __str__(self):
        return self.type

class SurfaceType(models.Model): #done
    type = models.CharField(max_length=100)

    def __str__(self):
        return self.type

# Core Tables
class User(AbstractUser): #done
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, validators=[phone_validator])
    user_type = models.ForeignKey(UserType, on_delete=models.CASCADE, related_name='users')
    modified_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.username

class Listing(models.Model): #done
    street = models.CharField(max_length=255)
    description = models.TextField()
    location = models.ForeignKey(Location, on_delete=models.RESTRICT, related_name='listings', db_index=True)
    sector = models.ForeignKey(Sector, on_delete=models.RESTRICT, null=True, blank=True, related_name='listings', db_index=True)
    user = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='listings', db_index=True)
    sale_type = models.ForeignKey(SaleType, on_delete=models.RESTRICT, related_name='listings')
    price = models.IntegerField(db_index=True)
    availability = models.BooleanField()
    property_type = models.ForeignKey(PropertyType, on_delete=models.RESTRICT, related_name='listings')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.street} - {self.price}€"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.location.location == "Chișinău" and not self.sector:
            raise ValidationError("Sectorul este obligatoriu când locația este Chișinău.")
        if self.location.location != "Chișinău" and self.sector:
            raise ValidationError("Sectorul trebuie să fie necompletat când locația nu este Chișinău.")

class ListingImage(models.Model): #done
    listing = models.ForeignKey(Listing, on_delete=models.RESTRICT, related_name='images')
    image = models.ImageField(upload_to='imagini_anunturi/')

    def __str__(self):
        return f"Image for {self.listing.street}"
    
    def delete(self, *args, **kwargs):
        self.image.delete(save=False)
        super().delete(*args, **kwargs)

# Detail Tables by Property Type
class Apartment(models.Model): #done
    listing = models.OneToOneField(Listing, on_delete=models.RESTRICT, related_name='apartment')
    surface = models.IntegerField()
    condition = models.ForeignKey(Condition, on_delete=models.RESTRICT, related_name='apartments')
    construction_type = models.ForeignKey(ConstructionType, on_delete=models.RESTRICT, related_name='apartments')
    planning_type = models.ForeignKey(PlanningType, on_delete=models.RESTRICT, related_name='apartments')
    rooms = models.IntegerField()
    floor = models.IntegerField()
    total_floors = models.IntegerField()
    bathrooms = models.IntegerField()
    heating_type = models.ForeignKey(HeatingType, on_delete=models.CASCADE, related_name='apartments')

    def __str__(self):
        return f"Apartament {self.surface} m² • {self.listing.street}"

class House(models.Model): #done
    listing = models.OneToOneField(Listing, on_delete=models.RESTRICT, related_name='house')
    surface = models.IntegerField()
    land_surface = models.DecimalField(max_digits=10, decimal_places=1)
    rooms = models.IntegerField()
    total_floors = models.IntegerField()
    bathrooms = models.IntegerField()
    water_installation = models.BooleanField()
    gas_installation = models.BooleanField()
    sewerage_installation = models.BooleanField()

    def __str__(self):
        return f"Casă {self.surface} m² • {self.listing.street}"

class Land(models.Model): #done
    listing = models.OneToOneField(Listing, on_delete=models.RESTRICT, related_name='land')
    land_surface = models.DecimalField(max_digits=10, decimal_places=1)
    surface_type = models.ForeignKey(SurfaceType, on_delete=models.RESTRICT, related_name='lands')

    def __str__(self):
        return f"Teren {self.land_surface} m² • {self.surface_type}"

class CommercialSpace(models.Model): #done
    listing = models.OneToOneField(Listing, on_delete=models.RESTRICT, related_name='commercial_space')
    surface = models.IntegerField()
    condition = models.ForeignKey(Condition, on_delete=models.RESTRICT, related_name='commercial_spaces')
    floor = models.IntegerField()
    offices = models.IntegerField()
    bathrooms = models.IntegerField()

    def __str__(self):
        return f"Spațiu Comercial {self.surface} m² • {self.listing.street}"

# Messaging and Requests
class Message(models.Model): #done
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15, validators=[phone_validator])
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} • {self.subject}"

class Request(models.Model): #done
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, validators=[phone_validator])
    email = models.EmailField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='requests', db_index=True)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, null=True, blank=True, related_name='requests')
    property_type = models.ForeignKey(PropertyType, on_delete=models.CASCADE, related_name='requests')
    estimated_price = models.IntegerField(default=0)
    condition = models.ForeignKey(Condition, on_delete=models.CASCADE, related_name='requests')
    note = models.TextField(blank=True, null=True)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} • {self.location}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.location.location == "Chișinău" and not self.sector:
            raise ValidationError("Sectorul este obligatoriu când locația este Chișinău.")
        if self.location.location != "Chișinău" and self.sector:
            raise ValidationError("Sectorul trebuie să fie necompletat când locația nu este Chișinău.")