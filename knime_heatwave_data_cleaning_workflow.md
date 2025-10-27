☀️ Weather branch

# DB Connector → 
connects to heatwave_db database

# DB Table Selector → 
chooses heatwave_data table to read.

# DB Reader →
pulls the selected heatwave_data table results into KNIME.

# Missing Value → 
calculating meand for temperature and humidity.

# String Manipulation → 
removes Z from record_time and creates record_time_clean

# String to Date&Time → 
converts record_time_clean to date

# Date&Time Part Extractor → 
extracts only year, month, day from record_time_clean

# String Manipulation (2) → 
joins year, month, day

# GroupBy → 
groups by date_only_string

# Column Renamer → 
renames columns Mean(humidity) and Mean(temperature) to averagre_humidity and averagre_temperature

# Expression → 
creates temp_norm and humidity_norm

# Normalizer → 
scales temp_norm and humidity_norm numeric values into min–max normalization


🩺 Medical data branch

# DB Connector → 
connects to heatwave_db database

# DB Table Selector → 
chooses medical_data table to read.

# DB Reader → 
loads the data into KNIME.

# Date&Time to String → 
converts record_date column into string forma

# GroupBy → 
groups by record_date

# Column Renamer → 
renames columns Mean(stroke_cases) and Mean(asthma_cases) to stroke_cases and asthma_cases


🔗 Merged Branch:

# Joiner → 
joins heatwave_data and medical_data by record_date.

# Math Formula → 
calculates admissions_total.

# Number Rounder → 
rounds numeric outputs to 2 decimal digits.

# Row Filter → 
filters data to include only relevant records. average_temperature greater then or equal -20 and less than or equal 60. average_humidity greater then or equal 0 and less than or equal 100.

# DB Writer → 
writes the cleaned and processed data back into the database as cleaned_data table.

🤖 Predictions branch: 

# DB Connector → 
connects to heatwave_db database

# DB Table Selector → 
chooses cleaned_data table to read.

# DB Reader → 
loads the data into KNIME.

# Column filter → 
keeps only the required columns: date_only_str, temp_norm, humidity_norm and admissions_total

# Column Renamer → 
Renames column names:
date_only_str to ds
temp_norm to temperature
humidity_norm to humidity
admissions_total to y

# String to Date&Time → 
converts string-formatted ds column to date format

# Python Script →
script trains a Prophet model with temperature and humidity as regressors to forecast the target variable for the next 7 days and outputs the predictions back to KNIME

# Number Rounder →
rounds numeric outputs to 3 decimal digits.

# DB Writer → 
writes prediction results back into the database as predictions table.