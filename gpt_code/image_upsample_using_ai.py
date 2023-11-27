
import cv2

def upsample_image(image_path):
    """ 使用OpenCV的超分辨率模型进行升采样 """
    # 读取图像
    img = cv2.imread(image_path)

    # 加载预训练的超分辨率模型，例如使用 EDSR 模型
    sr = cv2.dnn_superres.DnnSuperResImpl_create()
    path_to_model = "EDSR_x4.pb"  # 模型文件路径，需要提前下载
    sr.readModel(path_to_model)
    sr.setModel('edsr', 4)  # 设置模型和放大因子

    # 应用超分辨率模型
    result = sr.upsample(img)

    return result

# 示例使用
# image_path = "path_to_image.jpg"
# upsampled_image = upsample_image(image_path)
# cv2.imshow("Upsampled Image", upsampled_image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
