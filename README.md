# scrapy-mining
Temporary repository

## Usage
```
pip install -r requirements.txt
mkdir output
perceval github scrapy scrapy --category issue -t <token> --sleep-for-rate | python src/mergeJSON.py > output/scrapy-github.json
python src/main.py output/scrapy-github.json ./output/
```

## Results obtained

How many issues have been selected in each filtering steps:

| Steps                                  | Length |
|----------------------------------------|--------|
| Perceval issues                        | 5932   |
| Merged-pr or Closed-bug                | 2238   |
| With large interarrival && short burst | 624    |

Where:
- large interarrival is timedelta: `8 days, 11:52:51`
- short burst is timedelta: `2 days, 3:10:46`

Interarrivals parameter (computed on 2238 issues):
- `Q3 = 51.1795 hours (2.13 days)`
- `Q2 = 3.5885  hours`
- `Q1 = 0.279 hours`
