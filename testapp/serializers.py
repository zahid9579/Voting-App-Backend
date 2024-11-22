from rest_framework import serializers
from testapp.models import UserModel,CandidateModel

class userSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = '__all__'
        
class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateModel
        fields = '__all__'