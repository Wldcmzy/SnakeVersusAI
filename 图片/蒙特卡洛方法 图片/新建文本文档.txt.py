import random
import math
import matplotlib.pyplot as plt

def estimate_pi(num_samples):
    inside_circle = 0

    x_values_inside = []
    y_values_inside = []

    x_values_outside = []
    y_values_outside = []

    for _ in range(num_samples):
        x = random.uniform(0, 1)
        y = random.uniform(0, 1)

        distance = math.sqrt(x ** 2 + y ** 2)

        if distance <= 1:
            inside_circle += 1
            x_values_inside.append(x)
            y_values_inside.append(y)
        else:
            x_values_outside.append(x)
            y_values_outside.append(y)

    pi_estimate = 4 * inside_circle / num_samples

    return pi_estimate, x_values_inside, y_values_inside, x_values_outside, y_values_outside

# 设定抽样数量
num_samples = 10000

# 估计圆周率并获取样本点
pi_estimate, x_inside, y_inside, x_outside, y_outside = estimate_pi(num_samples)

# 绘制散点图
plt.figure(figsize=(6, 6))
plt.scatter(x_inside, y_inside, color='blue', marker='.', alpha=0.5, label='Inside Circle')
plt.scatter(x_outside, y_outside, color='red', marker='.', alpha=0.5, label='Outside Circle')

# 绘制圆
circle = plt.Circle((0, 0), 1, color='red', fill=False)
plt.gca().add_patch(circle)

# 设置坐标轴
plt.axis('equal')
plt.xlim(-1, 1)
plt.ylim(0, 1)

# 显示红、蓝点的数目
plt.text(-0.9, 0.9, f'Blue Points: {len(x_inside)}', fontsize=10)
plt.text(-0.9, 0.8, f'Red Points: {len(x_outside)}', fontsize=10)

# 显示估计值和计算公式
plt.text(-0.9, 1.1, f'Estimated Pi: {pi_estimate:.5f}', fontsize=10)
plt.text(-0.9, 1.2, 'Pi = 4 * (Points Inside Circle) / (Total Points)', fontsize=10)

# 添加图例
plt.legend()

# 保存图片
plt.savefig('mctmethod.jpg')

# 显示图像
plt.show()
