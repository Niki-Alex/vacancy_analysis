# Parsing and analysis python vacancies

The first thing the project does is parse "djinni.co" 
website for Python developer vacancies and then 
conduct analytics on these vacancies

## Getting Started

### - Using Git

Clone the repo:

```
git clone https://github.com/Niki-Alex/vacancy_analysis.git
cd vacancy_analysis
python -m venv venv
venv\Scripts\activate (on Windows)
source venv/bin/activate (on macOS and Linux)
pip install -r requirements.txt
```

## Run Scrapy

```
scrapy crawl vacancies -O vacancies.csv
```

## Run Analysis

1. Input ```jupyter notebook``` via terminal

2. Open ```vacancy_analysis.ipynb```

3. Go to ```Run``` > ```Run All Cells```
