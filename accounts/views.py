from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User


class LoginView(APIView):

    def post(self, request):
        email_or_username = request.data.get('email')
        password = request.data.get('password')

        if not email_or_username or not password:
            return Response({"detail": "Email and password required"}, status=400)

        # Try username login
        user = authenticate(username=email_or_username, password=password)

        # Try email login
        if user is None:
            try:
                user_obj = User.objects.get(email=email_or_username)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                return Response({"detail": "Invalid credentials"}, status=401)

        if not user.is_active:
            return Response({"detail": "Account inactive"}, status=403)

        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }, status=200)