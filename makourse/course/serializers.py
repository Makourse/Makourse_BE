from rest_framework import serializers
from .models import *
from account.models import *

class CreateMyPlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyPlace
        fields = '__all__'

        

class ListMyPlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyPlace
        fields = '__all__'