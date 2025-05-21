from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


# Create your tests here.
class RegistrationTestCase(TestCase):
    def setUp(self) -> None:
        self.data = {
            "username": "someusername",
            "password1": "ComplexPassword123!",
            "password2": "ComplexPassword123!",
        }

    def tests_form_registration_get(self) -> None:
        path = reverse("users:register")
        response = self.client.get(path)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/register.html")

    def tests_user_registration_success(self) -> None:
        user_model = get_user_model()

        path = reverse("users:register")
        response = self.client.post(path, self.data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("index"))
        self.assertTrue(
            user_model.objects.filter(username=self.data["username"]).exists()
        )

    def tests_user_registration_password_error(self) -> None:
        self.data["password2"] = "ComlexPasword13!"

        path = reverse("users:register")
        response = self.client.post(path, self.data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The two password fields didn’t match.")

    def tests_user_registration_duplicate_username(self) -> None:
        user_model = get_user_model()
        user_model.objects.create(username=self.data["username"])

        path = reverse("users:register")
        response = self.client.post(path, self.data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A user with that username already exists.")


class AuthRedirectTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(  # type: ignore
            username="testuser",
            password="pass123",
        )
        self.client.login(username="testuser", password="pass123")

    def test_authenticated_user_redirected_from_login(self) -> None:
        response = self.client.get(reverse("users:login"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("index"))

    def test_authenticated_user_redirected_from_register(self) -> None:
        response = self.client.get(reverse("users:register"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("index"))

    def tests_user_login_password_error(self) -> None:
        self.client.logout()

        path = reverse("users:login")
        response = self.client.post(
            path, {"username": "testuser", "password": "pass121"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Please enter a correct username and password. Note that both fields may be case-sensitive.",
        )
