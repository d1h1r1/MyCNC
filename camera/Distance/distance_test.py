import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

# 示例数据（你自己采集）
data = [
    (317, 233, 0),
    (300, 234, 10),
    (280, 234, 20),
    (260, 234, 30),
    (240, 234, 40),
]
X = np.array([[x, y] for x, y, _ in data])
y = np.array([d for _, _, d in data])

# 多项式拟合（2次）
poly = PolynomialFeatures(degree=2)
X_poly = poly.fit_transform(X)

model = LinearRegression()
model.fit(X_poly, y)


# 预测一个新点的距离
def predict_distance(x, y):
    input_poly = poly.transform([[x, y]])
    return model.predict(input_poly)[0]


# 测试
print(f"预测 (280, 234) 的距离: {predict_distance(270, 234):.2f} cm")
