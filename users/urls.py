from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from users import views

app_name = 'users'

urlpatterns = [
    # join the membership
    path("signup", views.SignupView.as_view(), name="signup"),
    path("seller-signup", views.SellerSignup.as_view(), name="seller_google_signup"),
    # Email Authentication
    path("send-email", views.SendEmail.as_view(), name="send_email"),
    path("check-email", views.CheckEmailView.as_view(), name="check_email"),
    # social login
    path("social", views.SocialUrlView.as_view(), name="social_login"),
    path("google", views.GoogleLoginView.as_view(), name="google_login"),
    # log in
    path("signin", views.LoginView.as_view(), name="signin"),
    path("check-token", views.CheckToken.as_view(), name="CheckToken"),
    # User information related
    path("my-page", views.UserView.as_view(), name="my_page"),
    path("my-page/profile", views.ChangeUserProfile.as_view(), name="ChangeUserProfile"),
]
