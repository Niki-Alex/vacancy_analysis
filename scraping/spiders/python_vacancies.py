import re
import scrapy
from datetime import date
from typing import Generator, Optional
from scrapy.http import Response

from support import months_convector, technologies_list


class PythonVacanciesSpider(scrapy.Spider):
    name = "python_vacancies"
    allowed_domains = ["djinni.co"]
    start_urls = ["https://djinni.co/jobs/?primary_keyword=Python"]

    def parse(self, response: Response, **kwargs: Optional) -> Generator:
        vacancies = response.css(".job-list-item__link::attr(href)").getall()

        for vacancy in vacancies:
            yield scrapy.Request(
                url=response.urljoin(vacancy),
                callback=self._get_detail_vacancy,
            )

        next_page = response.css(
            ".pagination > li:last-child > a::attr(href)"
        ).get()

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def _get_detail_vacancy(self, response: Response) -> Generator:

        yield {
            "title": response.css("h1::text").get().strip(),
            "salary": self.get_salary(response),
            "company": response.css(".job-details--title::text").get().strip(),
            "english_level": self.get_english_skill(response),
            "experience_years": self.get_experience_years(response),
            "domain": self.get_domain(response),
            "job_type": response.css(".bi-building + div::text").get(),
            "company_type": self.get_company_type(response),
            "country": self.get_country(response),
            "test_task_exists": bool(
                response.css(".bi-pencil-square + div::text").get()
            ),
            "publication_date": self.get_publication_date(response),
            "views_count": int(response.css(".text-muted").re_first(r"(\d+) перегляд")),
            "applicant_count": int(
                response.css(".text-muted").re_first(r"(\d+) відгук")
            ),
            "technologies": self.get_technologies(response),
        }

    @staticmethod
    def get_salary(response: Response) -> list[int] | None:
        salary = response.css(".public-salary-item::text").get()

        if salary is not None:
            return [int(cash) for cash in re.findall(r"\d+", salary)]

    @staticmethod
    def get_english_skill(response: Response) -> str:
        english_skill = response.xpath(
            "//div[contains(text(), 'Англійська:')]/text()"
        ).get()

        if english_skill is not None:
            return english_skill.split(":")[1].strip()
        return "Не вказано"

    @staticmethod
    def get_experience_years(response: Response) -> int:
        experience_years = response.xpath(
            "//div[contains(text(), 'досвіду')]/text()"
        ).get()

        return int(experience_years.split()[0].replace("Без", "0"))

    @staticmethod
    def get_domain(response: Response) -> str | None:
        domain = response.xpath("//div[contains(text(), 'Домен:')]/text()").get()

        if domain is not None:
            return domain.split(":")[1].strip()

    @staticmethod
    def get_company_type(response: Response) -> str:
        company_type_1 = response.css(".bi-exclude + div::text").get()
        company_type_2 = response.css(".bi-basket3-fill + div::text").get()

        return company_type_1 if company_type_1 is not None else company_type_2

    @staticmethod
    def get_country(response: Response) -> list[str]:
        countries = response.css(".location-text::text").get().strip()
        cities = response.css(".location-text > span::text").get()
        more_cities = response.css(
            ".location-text > span > span[data-original-title]::text"
        ).get()

        countries_list = [country.strip() for country in countries.split(",")]

        if cities is not None:
            if more_cities is not None:
                countries_list[-1] = f"{countries_list[-1]} {cities + more_cities}"
            countries_list[-1] = f"{countries_list[-1]} {cities}"

        return countries_list

    @staticmethod
    def get_publication_date(response: Response) -> date:
        date_str = response.css(".text-muted::text").re_first(
            r"\d{1,2} [а-яіїє]+ \d{4}"
        )
        day, month, year = date_str.split()

        return date(day=int(day), month=months_convector(month), year=int(year))

    @staticmethod
    def get_technologies(response: Response) -> list[str]:
        technologies = response.css(".row-mobile-order-2 > .mb-4").get().lower()

        return [
            technology
            for technology in technologies_list
            if technology.lower() in technologies
        ]
