from django.db import models
from django.utils.encoding import python_2_unicode_compatible # python2와 호환되는지 체크
from minstagram.users import models as user_models

# 하고 싶은 것
# model이 언제 생성되었는가?
# model이 언제 업데이트 되었는가?

# model의 종류 like, comment, image
# 각각에 create date, update date 변수를 줄 수 있다.
# 이 작업을 abstract base class로 작업할 것이다.

# abstract base class는 다른 model이 상속 받는 기본 class로 실제 DB에는 생성되지 않는다.
# abstract base classses are useful when you want to put some common information into a number of other models.

# abstract base class인 TimeStampedModel
# inner class로 Meta 클래스를 생성하고 abstract = True를 변수로 선언하면 abstract base class가 된다.
# model metadata is "anything that's not a field"
@python_2_unicode_compatible
class TimeStampedModel(models.Model):
    # 다른 model이 상속 받을 변수
    created_at = models.DateTimeField(auto_now_add=True) # model이 생성되면 자동으로 생성시간 추가
    updated_at = models.DateTimeField(auto_now=True) # model이 변경되면 자동으로 새로고침

    class Meta:
        abstract = True # abstract base class 선언 -> This model will then not be used to create any database table.
        # abstract가 Meta에 있지 않고 TimeStampedModel에 있으면, created_at, updated_at이 생성되지 않는다.

# image 모델
@python_2_unicode_compatible
class Image(TimeStampedModel):

    """ Image Model """

    file = models.ImageField()
    location = models.CharField(max_length=140)
    caption = models.TextField()
    creator = models.ForeignKey(user_models.User, null=True)

    # string representation
    def __str__(self):
        return '{} - {}'.format(self.location, self.caption)

# comment 모델
@python_2_unicode_compatible
class Comment(TimeStampedModel):
    
    """ Comment Model """
    
    message = models.TextField()
    creator = models.ForeignKey(user_models.User, null=True)
    image = models.ForeignKey(Image, null=True)

    # string representation
    def __str__(self):
        return self.message

# like 모델
@python_2_unicode_compatible
class Like(TimeStampedModel):

    """ Like Model """

    creator = models.ForeignKey(user_models.User, null=True)
    image = models.ForeignKey(Image)

    # string representation
    def __str__(self):
        return '[User] {} / [img Caption] {}'.format(self.creator.username, self.image.caption) # creator, image는 foreign key