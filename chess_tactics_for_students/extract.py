import pymupdf

ZOOM_MATRIX = pymupdf.Matrix(5, 5)  # rect * 5 (px)

doc = pymupdf.open("chess_tactics_for_students.pdf")


def extract_solutions(first_page: int, last_page: int) -> list[str]:
    filenames = []

    for page_no in range(first_page, last_page):
        page = doc[page_no]

        max_x = page.rect.width
        max_y = page.rect.height
        column_width = int(max_x / 3)

        for i in range(3):
            rect = pymupdf.Rect(
                column_width * i, 60, column_width * (i + 1), max_y - 30
            )
            pix = page.get_pixmap(matrix=ZOOM_MATRIX, clip=(rect))
            filename = f"page_{page_no}_column_{i + 1}.png"
            filenames.append(filename)
            pix.save(filename)

    return filenames


def extract_diagrams():
    # RECT_SIZE = (175, 200)
    # RECT_COORDS = [(25, 90), (25, 425)]

    RECT_SIZE = (155, 150)
    RECT_COORDS = [(40, 105), (40, 440)]

    for page_number in range(15, len(doc)):
        print(page_number + 1)
        page = doc[page_number]
        for i, rect_coords in enumerate(RECT_COORDS):
            rect = pymupdf.Rect(
                rect_coords[0],
                rect_coords[1],
                rect_coords[0] + RECT_SIZE[0],
                rect_coords[1] + RECT_SIZE[1],
            )
            pix = page.get_pixmap(matrix=ZOOM_MATRIX, clip=rect)
            pix.save(f"diagrams/page_{(page_number + 1):03}_diagram_{i + 1}.png")


def create_pdf_from_images(image_filenames: list[str], output_pdf: str):
    pdf_doc = pymupdf.open()

    for image_file in image_filenames:
        img_doc = pymupdf.open(image_file)
        pdf_bytes = img_doc.convert_to_pdf()
        img_pdf = pymupdf.open("pdf", pdf_bytes)
        pdf_doc.insert_pdf(img_pdf)

    pdf_doc.save(output_pdf)
    pdf_doc.close()


if __name__ == "__main__":
    image_filenames = extract_solutions(241, 260)
    create_pdf_from_images(image_filenames, "solutions.pdf")
