from rest_framework import serializers

from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super(DocumentSerializer, self).__init__(*args, **kwargs)

        request = self.context.get("request")
        if request and request.user.is_staff:
            return

        # Remove sensitive fields for non-staff users
        self.fields.pop("faiss_store")

    class Meta:
        model = Document
        fields = "__all__"
