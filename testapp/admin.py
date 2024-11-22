from django.contrib import admin
from testapp.models import UserModel, CandidateModel, Vote

# Register your models here.
admin.site.register(UserModel)
admin.site.register(CandidateModel)
admin.site.register(Vote)
