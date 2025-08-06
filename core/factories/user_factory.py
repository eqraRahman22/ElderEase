# core/factories/user_factory.py
from core.models import CustomUser

class UserFactory:
    """
    Factory Pattern: Creates a user based on role
    """
    @staticmethod
    def create_user(username, email, password, role):
        user = CustomUser.objects.create_user(
            username=username, email=email, password=password, role=role
        )
        return user
