from django.contrib import admin
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist



# models.py
from django.db import models

# class Upload(models.Model):
#     file = models.FileField(upload_to='uploads/')
#     uploaded_at = models.DateTimeField(auto_now_add=True)
#     title = models.CharField(max_length=255, blank=True)
#     description = models.TextField(blank=True)
#     event_types = models.CharField(max_length=50, blank=True)

class Upload(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='uploads', null=True, blank=True)
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "uploads", default=None)
    file_type = models.CharField(max_length=50, blank=True, default="unknown")


class Event(models.Model):
    title = models.CharField(max_length = 100)
    description = models.TextField()
    date = models.DateTimeField()
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "events")
    rsvps = models.ManyToManyField(User)
    def __str__(self):
        return self.title

class CommonUser(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    friends = models.ManyToManyField('self', symmetrical=True, blank=True)
    def __str__(self):
        return self.user.email

class Message(models.Model):
    event = models.ForeignKey(Event, related_name='messages', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_messages', blank=True)
    def __str__(self):
        return f'Message by {self.author.username} on {self.event.title}'

admin.site.register(Upload)
admin.site.register(Event)
admin.site.register(CommonUser)
admin.site.register(Message)
