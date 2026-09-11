
import secrets
from django.db import connection
from django.http import Http404
from django.shortcuts import redirect
from django.views import View
from django.conf import settings


class RestoreDatabaseView(View):
    def get(self, request, token):
        expected = settings.RESTORE_DB_TOKEN
        # 404 instead of 403: don't confirm the endpoint even exists
        if not expected or not secrets.compare_digest(token, expected):
            raise Http404

        with connection.cursor() as cursor:
            cursor.execute("EXEC dbo.sp_reset_logistics_data;")

        return redirect("home")