from django.db import models
from django.contrib.auth.models import User
from PIL import Image


# Create Profile for User
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dob = models.DateField(null=True, blank=True)
    image = models.ImageField(default='default.jpg', upload_to='profile_img')
    profession = models.CharField(max_length=100)
    about = models.TextField()

    def __str__(self):
        return f'{self.user.username} Profile'

    # override the save function to change image size
    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)
        if self.image:
            img = Image.open(self.image.path)

            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.image.path)
