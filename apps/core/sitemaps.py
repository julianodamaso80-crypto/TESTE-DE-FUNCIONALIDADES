from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = 'weekly'
    protocol = 'https'

    def items(self):
        return ['core:home', 'account_login', 'account_signup']

    def location(self, item):
        return reverse(item)


class PricingSitemap(Sitemap):
    priority = 0.9
    changefreq = 'monthly'
    protocol = 'https'

    def items(self):
        return ['billing:pricing']

    def location(self, item):
        return reverse(item)
