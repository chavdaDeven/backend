from uuid import uuid4

from django.conf import settings
from django.db.models import CASCADE, CharField, DateTimeField, ForeignKey, Model
from django.db.models import PositiveSmallIntegerField as PSIF
from django.db.models import TextField, UUIDField

from .choices import UploadKind, UploadStatus
from .storage import generate_presigned_url_get, generate_presigned_url_put


class BaseModel(Model):
    """
    TODO:
    In future, make use of DEFAULT_AUTO_FIELD = "django.db.models.UUIDAutoField"
    blocker: https://code.djangoproject.com/ticket/32577
    """

    id = UUIDField(default=uuid4, primary_key=True, editable=False)
    created_at = DateTimeField(auto_now_add=True, editable=False)
    updated_at = DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.id}"


class User(BaseModel):
    email = CharField(max_length=250)
    first_name = CharField(max_length=250)
    last_name = CharField(max_length=250)

    def __str__(self):
        return f"{self.email} [{self.id}]"


class Upload(BaseModel):
    error_message = TextField(null=True, blank=True)
    filename = CharField(max_length=250)
    kind = PSIF(choices=UploadKind.choices, default=UploadKind.PROFILE_PICTURE)
    mimetype = CharField(max_length=100)
    status = PSIF(choices=UploadStatus.choices, default=UploadStatus.UPLOADING)
    user = ForeignKey(User, on_delete=CASCADE, related_name="uploads")

    @property
    def key(self):
        """storage bucket key / object path"""
        return f"{settings.UPLOADS_PREFIX}/{self.kind}/{self.id}"

    def __str__(self):
        return f"[{self.user}] {self.filename}"

    @property
    def presigned_url_get(self):
        return generate_presigned_url_get(self.key)

    @property
    def presigned_url_put(self):
        return generate_presigned_url_put(self.key)
