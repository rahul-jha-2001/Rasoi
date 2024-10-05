from django.db import models
from User.models import User
import uuid
class Store(models.Model):

    
    user = models.ForeignKey(User,on_delete=models.CASCADE,)
    StoreUuid = models.UUIDField(primary_key= True, default=uuid.uuid4, editable=False, unique=True)
    StoreName = models.CharField(max_length=255,null=True)
    IsOpen =  models.BooleanField(default=True)
    CreatedAt = models.DateTimeField(auto_now_add=True)
    UpdatedAt = models.DateTimeField(auto_now=True)


    def __str__(self) -> str:
        return str(self.StoreName)
    


