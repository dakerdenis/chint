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




class ViewsTest(TestCase):
    """HTTP-level tests for public views and routing."""

    databases = {"default", "catalog"}

    def test_static_pages_return_200(self):
        # simple pages that render without requiring DB data
        for url in ["/en/about/", "/en/contacts/", "/en/tech-consult/"]:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_policy_pages_return_200(self):
        for url in [
            "/en/politics/privacy-policy/",
            "/en/politics/cookie/",
            "/en/politics/user-agreement/",
        ]:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_catalog_returns_404_when_root_missing(self):
        # catalog root is looked up by a fixed UUID; absent in a fresh test DB,
        # so the view correctly returns 404 via get_object_or_404
        response = self.client.get("/en/catalog/")
        self.assertEqual(response.status_code, 404)

    def test_unknown_page_returns_404(self):
        response = self.client.get("/en/this-page-does-not-exist/")
        self.assertEqual(response.status_code, 404)


class LocaleRedirectTest(TestCase):
    """Root URL should redirect to the default localized prefix."""

    def test_root_redirects_to_english(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/en", response.url)

    def test_localized_root_is_reachable(self):
        # /en/ should not 404 or 500 — it's the localized home
        response = self.client.get("/en/")
        self.assertNotEqual(response.status_code, 404)
