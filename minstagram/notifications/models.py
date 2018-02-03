from django.db import models
from django.utils.encoding import python_2_unicode_compatible  # python2와 호환되는지 체크
from minstagram.users import models as user_models
from minstagram.images import models as image_models


class Notification(image_models.TimeStampedModel):

    TYPE_CHOICES = (
        ('like', 'Like'), # 첫번째는 admin, 두번째는 db에서 사용
        ('comment', 'Comment'),
        ('follow', 'Follow'),
    )

    creator = models.ForeignKey(user_models.User, related_name="creator")
    to = models.ForeignKey(user_models.User, related_name="to")
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    image = models.ForeignKey(image_models.Image, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return 'From: {} - To: {}'.format(self.creator, self.to)