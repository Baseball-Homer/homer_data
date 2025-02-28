# Homer

This repository contains data extraction code for Homer, a baseball simulation game. It retrieves player and team statistics using statsapi and processes them for in-game simulations.

`Homer` allows you to create a squad based on some of the players in the MLB and play against others.

The information about MLB players and teams is based on data from [MLB.com](https://www.mlb.com/).

This repository was used for `Database System` Course of Chungbuk National University.

### 🏗 Previous Project
The previous project collected player performance data and used a simple rule-based approach to calculate ratings. However, it lacked a proper mechanism to adjust for sample size reliability, leading to inaccuracies in evaluations.

### 🚀 Upgraded Project
The upgraded version introduces the following improvements:
- Machine Learning Model Implementation: Predicts ratings using batting average, on-base percentage, and slugging percentage.
- Weighted Adjustments Based on Sample Size: Accounts for lower reliability in smaller samples.
- Automated Data Collection: Uses the sportsdata.io API for real-time player statistics.
- 20/80 Scale Conversion: Machine learning models map raw statistics to the 20–80 rating scale.
  
### 📊 Data Processing Pipeline
- Data Collection: Retrieve player season statistics via the sportsdata.io API.
- Data Preprocessing: Handle missing values, adjust for sample size, and extract key metrics.
- Rating Calculation: Use machine learning models to predict Contact, Power, and Discipline.
- Reliability Adjustment: Apply weighting based on the number of games played.
- Result Storage: Save outputs as CSV files or to a database.
