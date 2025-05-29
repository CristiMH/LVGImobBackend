from django.contrib import admin
from .models import (
    PropertyType, Condition, SaleType, UserType, Sector, Location,
    HeatingType, PlanningType, ConstructionType, SurfaceType,
    User, Listing, ListingImage, Apartment, House, Land, CommercialSpace,
    Message, Request
)

class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1

class ApartmentInline(admin.StackedInline):
    model = Apartment
    extra = 0

class HouseInline(admin.StackedInline):
    model = House
    extra = 0

class LandInline(admin.StackedInline):
    model = Land
    extra = 0

class CommercialSpaceInline(admin.StackedInline):
    model = CommercialSpace
    extra = 0

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    inlines = [ListingImageInline, ApartmentInline, HouseInline, LandInline, CommercialSpaceInline]
    list_display = ('street', 'price', 'location', 'sector', 'user', 'availability')
    list_filter = ('location', 'sector', 'property_type', 'availability')
    search_fields = ('street', 'description', 'user__username')

admin.site.register(PropertyType)
admin.site.register(Condition)
admin.site.register(SaleType)
admin.site.register(UserType)
admin.site.register(Sector)
admin.site.register(Location)
admin.site.register(HeatingType)
admin.site.register(PlanningType)
admin.site.register(ConstructionType)
admin.site.register(SurfaceType)
admin.site.register(User)
admin.site.register(ListingImage)
admin.site.register(Apartment)
admin.site.register(House)
admin.site.register(Land)
admin.site.register(CommercialSpace)
admin.site.register(Message)
admin.site.register(Request)