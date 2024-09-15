from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.contrib.auth.models import User


class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None):
        if not email:
            raise ValueError('The Email field is required')
        if not first_name or not last_name:
            raise ValueError('First and Last names are required')

        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None):
        user = self.create_user(email, first_name, last_name, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    friends = models.ManyToManyField('self', symmetrical=False, through='FriendRequest', related_name='friend_set', blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    def __str__(self):
        return self.email

    def send_friend_request(self, to_user):
        """Send a friend request to another user"""
        if not FriendRequest.objects.filter(from_user=self, to_user=to_user).exists():
            friend_request = FriendRequest(from_user=self, to_user=to_user)
            friend_request.save()
            return True
        return False

    def remove_friend(self, friend):
        """Remove a friend relationship between users"""
        self.friends.remove(friend)

    def get_friends(self):
        """Get all accepted friends"""
        return self.friends.filter(friend_requests__status='accepted')


class FriendRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    from_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')  # Prevent duplicate friend requests

    def __str__(self):
        return f"FriendRequest from {self.from_user.email} to {self.to_user.email} ({self.status})"
