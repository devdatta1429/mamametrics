import pandas as pd
from db import get_connection
from sklearn.ensemble import RandomForestClassifier
import joblib

conn = get_connection()

df = pd.read_sql("SELECT * FROM past_data", conn)

df = df.dropna(subset=['risk_result'])
df['risk_result'] = df['risk_result'].astype(str).str.strip()

df['risk_result'] = df['risk_result'].replace({
    'Low': 0,
    'Medium': 1,
    'High': 2
})

df = df.drop(['id', 'created_at'], axis=1)

features = [
    'age_mother','weight_before_preg','weight_during_preg','height_cm','bmi','hemoglobin',
    'pcos_status','age_father','yrs_of_mrg','no_of_misscarg',
    'exercise_t','exercise_b','exercise_p',
    'screen_t','screen_b','screen_p',
    'sleep_t','sleep_b','sleep_p',
    'outside_food_t','outside_food_b','outside_food_p',
    'tea_coffee_t','tea_coffee_b','tea_coffee_p',
    'smoking_t','smoking_b','smoking_p',
    'alcohol_t','alcohol_b','alcohol_p',
    'happiness_status','intercourse_freq'
]

X = df[features].fillna(0)
y = df['risk_result']

model = RandomForestClassifier()
model.fit(X, y)

# 🔥 CREATE FOLDER FIRST: models/
joblib.dump(model, 'models/model.pkl')

print("✅ Model saved successfully")