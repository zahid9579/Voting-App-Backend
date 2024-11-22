from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from testapp.models import UserModel,CandidateModel
from testapp.serializers import userSerializer
import jwt  # Use PyJWT for token generation
from django.contrib.auth.hashers import make_password, check_password
from testapp.models import UserModel
from rest_framework.permissions import IsAuthenticated
from testapp.serializers import CandidateSerializer 


#----------------- User Creation or Voter ----------------------

# Your SECRET_KEY from settings.py
SECRET_KEY = 'django-insecure-0!#1d&0vyl%*5l+#&1p@^(h)4!ekp&-px(8^ox922e_1$8x@3t'

def generate_token(payload):
    # Generate JWT token using the SECRET_KEY
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


# User Creation
class UserAPIView(APIView):
    def post(self, request):
        serializer = userSerializer(data=request.data)  # Use the serializer
        if serializer.is_valid():  # Validate the data
            new_user = serializer.save()  # Save the data to the database

            # Generate a token
            payload = {"id": new_user.id}
            token = generate_token(payload)

            # Send success response
            return Response(
                {"response": serializer.data, "token": token},
                status=status.HTTP_201_CREATED,
            )
        else:
            # Handle validation errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Login User
class LoginCBV(APIView):
    def post(self, request):
        # Extract Aadhaar Card Number and Password from request data
        aadhaar_card_number = request.data.get("aadhaar_card_number")
        password = request.data.get("password")

        # Validate input
        if not aadhaar_card_number or not password:
            return Response(
                {"error": "Aadhaar Card Number and Password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Check if the user exists
            user = UserModel.objects.get(aadhaar_card_number=aadhaar_card_number)
        except UserModel.DoesNotExist:
            return Response(
                {"error": "Invalid Aadhaar Card Number or Password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Check if the password matches
        if user.password != password:
            return Response(
                {"error": "Invalid Aadhaar Card Number or Password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Generate a token
        payload = {"id": user.id}
        token = generate_token(payload)

        # Send success response
        return Response(
            {"message": "Login successful", "token": token},
            status=status.HTTP_200_OK,
        )
        
        
        
# Profile User
class ProfileCBV(APIView):
    def get(self, request):
        try:
            # Assuming user is authenticated and 'request.user' contains the current user object
            user_id = request.user.id  # Get the user ID from the request
            user = UserModel.objects.get(id=user_id)  # Query the user based on the ID

            # Serialize the user data
            serializer = userSerializer(user)

            # Return serialized user data in the response
            return Response(serializer.data, status=status.HTTP_200_OK)

        except UserModel.DoesNotExist:
            # Handle case where user does not exist
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            # Handle any other exceptions
            return Response(
                {"error": str(e)},  # Return the exception message in case of unexpected error
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
            
            
class ProfileUpdateCBV(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated
    
    def put(self, request):
        user = request.user  # Get the user object from the request (via the token)
        
        current_password = request.data.get('current_password')  # Extract the current password
        new_password = request.data.get('new_password')  # Extract the new password
        
        if not current_password or not new_password:
            return Response(
                {"error": "Both current password and new password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Check if the current password is correct
        if not check_password(current_password, user.password):
            return Response(
                {"error": "Invalid current password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Update the user's password (hashing it before saving)
        user.password = make_password(new_password)
        user.save()

        # Send success response
        return Response(
            {"message": "Password updated successfully."},
            status=status.HTTP_200_OK,
        )
        



#------------------ Candidates Creation or Parties ---------------------

# Checking if the user is an Admin
def checkAdmin(userId):
    try:
        user = UserModel.objects.get(id=userId)  # Ensure UserModel is your custom user model
        return user.role == 'admin'  # Return True if role is 'admin', else False
    except UserModel.DoesNotExist:
        return False  # Return False if the user does not exist


 # Assuming you have a serializer for candidates
class CandidatePostCBV(APIView):
    def post(self, request):
        # Check if the user has an 'admin' role
        if not checkAdmin(request.user.id):
            return Response({"message": "User does not have admin role"}, status=status.HTTP_403_FORBIDDEN)

        # Use the serializer to validate and create the candidate
        serializer = CandidateSerializer(data=request.data)  # Use the correct serializer
        if serializer.is_valid():  # Validate the data
            new_candidate = serializer.save()  # Save the candidate to the database
            # Send success response
            return Response({"response": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            # Handle validation errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
class CandidateUpdateCBV(APIView):
    def put(self, request, candidate_id):
        try:
            # Check if the user has admin privileges
            if not checkAdmin(request.user.id):
                return Response(
                    {"message": "User does not have admin role"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Fetch the candidate object by ID
            try:
                candidate = CandidateModel.objects.get(id=candidate_id)
            except CandidateModel.DoesNotExist:
                return Response(
                    {"message": "Candidate not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Update the candidate data using the serializer
            serializer = CandidateSerializer(candidate, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()  # Save the updated candidate data
                return Response(
                    {"message": "Candidate updated successfully", "data": serializer.data},
                    status=status.HTTP_200_OK,
                )

            # Return validation errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Catch unexpected errors
            return Response(
                {"message": "Internal server error", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
            
            
class CandidateDeleteCBV(APIView):
    def delete(self, request, candidate_id):
        # Check if the user has admin privileges
        if not checkAdmin(request.user.id):
            return Response(
                {"message": "User does not have admin role"},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        # Fetch the candidate object by ID
        try:
            candidate = CandidateModel.objects.get(id=candidate_id)
        except CandidateModel.DoesNotExist:
            return Response(
            {"message": "Candidate not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
        # delate the candidate data using the serializer
        serializer = CandidateSerializer(candidate, data=request.data, partial=True)
        if serializer.is_valid():
            
            serializer.delete()  # Save the delete candidate data
            return Response(
               {"message": "Candidate Deleted  successfully", "data": serializer.data},
               status=status.HTTP_200_OK,
            )

      
 
#------------------- Let's start voting ---------------------
# No admin can vote
# User can only vote once


class VotingCBV(APIView):
    def post(self, request, *args, **kwargs):
        candidate_id = self.kwargs.get('candidate_id')  # Accessing candidate_id from URL parameters
        user = request.user  # Assuming the user is authenticated
        
        try:
            candidate = CandidateModel.objects.get(id=candidate_id)
        except CandidateModel.DoesNotExist:
            return Response({"message": "Candidate not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if the user has already voted
        if user.is_voted:
            return Response({"message": "You have already voted."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user is an admin
        if user.role == 'admin':
            return Response({"message": "Admins are not allowed to vote."}, status=status.HTTP_403_FORBIDDEN)

        # Update candidate's vote count and user's voting status
        candidate.vote_count += 1
        candidate.save()

        user.is_voted = True
        user.save()

        return Response({"message": "Vote recorded successfully."}, status=status.HTTP_200_OK)




# Vote count
class CountVotesCBV(APIView):
    def get(self, request):
        try:
            # Find the candidates and sort them by voteCount in descending order
            candidates = CandidateModel.objects.all().order_by('-voteCount')  # Use Django ORM for sorting
            
            # Map the candidates to only return their name and vote count
            vote_record = [{'party': candidate.party, 'count': candidate.voteCount} for candidate in candidates]
            
            return Response(vote_record, status=status.HTTP_200_OK)
        
        except CandidateModel.DoesNotExist:
            return Response({"message": "Candidate not found"}, status=status.HTTP_404_NOT_FOUND)
        