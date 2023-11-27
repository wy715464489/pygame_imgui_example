
from fpdf import FPDF
from PIL import Image

def images_to_pdf(image_paths, output_pdf_path):
    """将一系列图像合并成PDF"""
    pdf = FPDF(unit="mm", format="A4")
    
    for image_path in image_paths:
        img = Image.open(image_path)
        img_width, img_height = img.size
        aspect_ratio = img_width / img_height

        # 将图像调整到A4尺寸
        a4_width_mm = 210
        a4_height_mm = 297
        if aspect_ratio > 1:
            # 横向图像
            pdf_width = a4_width_mm
            pdf_height = a4_width_mm / aspect_ratio
        else:
            # 纵向图像
            pdf_height = a4_height_mm
            pdf_width = a4_height_mm * aspect_ratio

        pdf.add_page()
        pdf.image(image_path, x=0, y=0, w=pdf_width, h=pdf_height)

    pdf.output(output_pdf_path)

# 示例使用
# image_paths = ["processed_image1.jpg", "processed_image2.jpg"]
# output_pdf_path = "output.pdf"
# images_to_pdf(image_paths, output_pdf_path)
