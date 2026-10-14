# NBA Player Props Predictor 

A Python tool that scrapes recent NBA player game logs, incorporates team pace and opponent defensive metrics, 
and utilizes machine learning (`scikit-learn`) to predict a player's points for upcoming matchups.

---

## Features

- **Automated Web Scraping:** Parses game log tables using `BeautifulSoup` and `requests` to pull metrics like points, rebounds, assists, and shooting splits.
- **Situational Splits:** Analyzes performance across last 5 games, last 10 games, home/away splits, and head-to-head (H2H) matchups.
- **Pace & Defense Adjustments:** Integrates team pace ratings and opponent allowed points to give realistic context to projections.
- **Machine Learning Projections:** Uses a `DecisionTreeRegressor` trained on Monte Carlo-simulated data distributions (`NumPy` and `Pandas`) derived from historical player variance.

---

## Tech Stack

- **Python**
- **BeautifulSoup & Requests** (Web scraping)
- **Scikit-Learn** (Decision Tree regression modeling)
- **Pandas & NumPy** (Data manipulation and simulation)

---

## Getting Started

### Prerequisites

Make sure you have Python installed, along with the required libraries:

```bash
pip install requests beautifulsoup4 scikit-learn numpy pandas
