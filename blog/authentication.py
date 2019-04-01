from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailAuthBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        print(self.kwargs.get('username'))
        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None

    # def authenticate(self, username=None, password=None):
    #     print(User.objects.get(email=username))
    #     try:
    #         user = User.objects.get(email=username)
    #         print(user)
    #         if user.check_password(password):
    #             return user
    #     except User.DoesNotExist:
    #         print("yomf")
    #         return None
    #
    # def get_user(self, user_id):
    #     try:
    #         return User.objects.get(pk=user_id)
    #     except User.DoesNotExist:
    #         return None