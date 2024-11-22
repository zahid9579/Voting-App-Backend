from django.contrib import admin
from django.urls import path
from testapp.views import (
    UserAPIView,
    LoginCBV,
    ProfileCBV,
    ProfileUpdateCBV,
    CandidatePostCBV,
    CandidateUpdateCBV,
    CandidateDeleteCBV,
    VotingCBV,
    CountVotesCBV
)

urlpatterns = [
    # Admin Route
    path('admin/', admin.site.urls),

    # User Routes
    path('user/', UserAPIView.as_view(), name='user_api'),  
    path('login/', LoginCBV.as_view(), name='login_api'), 
    path('profile/', ProfileCBV.as_view(), name='profile_api'),  
    path('profile/update/', ProfileUpdateCBV.as_view(), name='profile_update_api'), 

    # Candidate Routes
    path('candidate/', CandidatePostCBV.as_view(), name='candidate_api'),  # Add a candidate
    path('candidate/update/<int:candidate_id>/', CandidateUpdateCBV.as_view(), name='candidate_update_api'),  # Update candidate
    path('candidate/delete/<int:candidate_id>/', CandidateDeleteCBV.as_view(), name='candidate_delete_api'),  # Delete candidate
    path('candidate/voting/<int:candidate_id>/', VotingCBV.as_view(), name='voting_api'),
    path('candidate/voteCnt', CountVotesCBV.as_view(), name='voteCnt'),
]
