from django.db import models

class UserModel(models.Model):
    name = models.CharField(max_length=80)
    age = models.IntegerField()
    email = models.EmailField(max_length=90)
    mobile = models.CharField(max_length=15)
    address = models.TextField()
    aadhaar_card_number = models.CharField(max_length=12)
    password = models.CharField(max_length=50)
    ROLE_CHOICES = [
        ('voter', 'Voter'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=80, choices=ROLE_CHOICES, default='voter')
    is_voted = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class CandidateModel(models.Model):
    name = models.CharField(max_length=50)
    party = models.CharField(max_length=90)
    age = models.IntegerField()
    votes = models.ManyToManyField(UserModel, through='Vote', related_name='voted_candidates')
    vote_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Vote(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='votes_cast')
    candidate = models.ForeignKey(CandidateModel, on_delete=models.CASCADE, related_name='vote_records')
    voted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} -> {self.candidate.name}"




