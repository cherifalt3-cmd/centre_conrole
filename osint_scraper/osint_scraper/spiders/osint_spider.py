import re
import scrapy


EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')

SOCIAL_DOMAINS = ['twitter.com', 'x.com', 'linkedin.com', 'github.com', 'facebook.com', 'instagram.com']


class OsintSpider(scrapy.Spider):
    name = 'osint'

    custom_settings = {
        'DEPTH_LIMIT': 2,
        'CLOSESPIDER_PAGECOUNT': 30,
    }

    def __init__(self, target=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not target:
            raise ValueError("Le paramètre 'target' (domaine) est requis")
        self.target_domain = target.replace('http://', '').replace('https://', '').strip('/')
        self.allowed_domains = [self.target_domain]
        self.start_urls = [f'https://{self.target_domain}']

    def parse(self, response):
        text = ' '.join(response.css('*::text').getall())
        emails = set(EMAIL_PATTERN.findall(text))

        social_links = set()
        for href in response.css('a::attr(href)').getall():
            for domain in SOCIAL_DOMAINS:
                if domain in href:
                    social_links.add(href)

        if emails or social_links:
            yield {
                'url': response.url,
                'emails': list(emails),
                'social_links': list(social_links),
            }

        for href in response.css('a::attr(href)').getall():
            yield response.follow(href, callback=self.parse)
