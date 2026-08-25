from django.test import TestCase

from web.models import SiteText


class HealthCheckTest(TestCase):
    """Health-check endpoint used for uptime/container monitoring."""

    def test_health_check_returns_ok(self):
        response = self.client.get("/health/")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "ok"})


class SiteTextModelTest(TestCase):
    """Multilingual site text with language fallback logic."""

    def setUp(self):
        SiteText.objects.create(
            key="welcome",
            en="Welcome",
            ru="Добро пожаловать",
            az="Xoş gəlmisiniz",
        )

    def test_str_returns_key(self):
        obj = SiteText.objects.get(key="welcome")
        self.assertEqual(str(obj), "welcome")

    def test_get_value_returns_correct_language(self):
        self.assertEqual(SiteText.get_value("welcome", "az"), "Xoş gəlmisiniz")

    def test_get_value_falls_back_to_english(self):
        # 'de' has no field -> falls back to English
        self.assertEqual(SiteText.get_value("welcome", "de"), "Welcome")

    def test_get_value_returns_key_when_missing(self):
        # unknown key returns the key itself, not an error
        self.assertEqual(SiteText.get_value("nonexistent", "en"), "nonexistent")


class PublicPagesTest(TestCase):
    """Root should redirect to a localized URL."""

    def test_root_redirects_to_locale(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
