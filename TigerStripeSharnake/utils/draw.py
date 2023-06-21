import cv2
import numpy as np

def draw_matrix_image(matrix, scale_factor, output_filename):
    def create_image(matrix):
        # 获取矩阵的尺寸
        rows, cols = matrix.shape

        # 计算绝对值的最大值
        max_abs_value = np.max(np.abs(matrix))

        # 创建图像
        image = np.zeros((rows, cols, 3), dtype=np.uint8)

        # 绘制图像
        for i in range(rows):
            for j in range(cols):
                value = matrix[i, j]
                intensity = int(255 * abs(value) / max_abs_value)
                if value < 0:
                    color = (0, 0, intensity)  # 红色 (B, G, R)
                else:
                    color = (0, intensity, 0)  # 绿色 (B, G, R)
                image[i, j] = color

        return image

    # 放大矩阵
    scaled_matrix = np.kron(matrix, np.ones((scale_factor, scale_factor)))

    # 创建图像
    image = create_image(scaled_matrix)

    # 保存图像
    cv2.imwrite(output_filename, image)

# # 示例矩阵
# matrix = np.array([[1, -2, 3], [-4, 5, -6], [7, -8, 9]])

# # 放大倍数
# scale_factor = 100

# # 保存图像为pic.jpg
# draw_matrix_image(matrix, scale_factor, 'pic.jpg')
