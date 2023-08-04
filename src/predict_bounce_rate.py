import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import shap
import matplotlib.pyplot as plt

features = pd.read_csv("data/graph_feature_data.csv").drop(columns=["Unnamed: 0"])
bounce_rate = pd.read_csv("data/bounce_rates.csv").drop(columns=["Unnamed: 0"])

data = features.merge(bounce_rate, on="node")

# groups are not even so downsample
sample_size = len(data.loc[(data["bounce_rate"] != 0) & (data["bounce_rate"] != 1)])
mid_bounce_data = data.loc[(data["bounce_rate"] != 0) & (data["bounce_rate"] != 1)]
no_bounce_data = data.loc[data["bounce_rate"] == 0].sample(n=sample_size)
all_bounce_data = data.loc[data["bounce_rate"] == 1].sample(n=sample_size)

sampled_data = pd.concat([mid_bounce_data, no_bounce_data, all_bounce_data])
print(sampled_data)

labels = ["node"]
target = ["bounce_rate"]
features = [col for col in sampled_data.columns if col not in labels + target]

X = np.array(sampled_data[features])
y = np.array(sampled_data[target])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

forest = RandomForestRegressor()
forest.fit(X_train, y_train)

y_train_pred = forest.predict(X_train)
y_test_pred = forest.predict(X_test)

print("train error:", mean_squared_error(y_train, y_train_pred))
print("test error:", mean_squared_error(y_test, y_test_pred))
# train error is small, test error is only slighly larger. Not overfitting
# don't have baseline for this performance so hard to say if underfitting

feat_importance = forest.feature_importances_
for i,j in zip(features, feat_importance):
    print(i, j)

explainer = shap.TreeExplainer(forest, X_test)
shap_values = explainer(X_test, check_additivity=False)
shap_values.feature_names = features
shap.plots.beeswarm(shap_values, show=False)
plt.savefig("shap.png", bbox_inches="tight")
