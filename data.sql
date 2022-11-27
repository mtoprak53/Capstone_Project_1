\echo 'Delete and recreate calorie_db db?'
\prompt 'Return for yes or control-C to cancel > ' foo

DROP DATABASE calorie_db;
CREATE DATABASE calorie_db;