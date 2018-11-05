from PyPDF2 import PdfFileWriter, PdfFileReader


class PdfManipulator:
    def __init__(self, filename):
        self.filename = filename
        self.contents = PdfFileReader(filename, "rb")
        self.output_file_name = ""
        self.output_pdf = PdfFileWriter()

    def has_a_cover_page(self):
        if self.contents.getPage(1).extractText().startswith("Accepted for the Council:"):
            return True
        else:
            return False

    def delete_cover_pages(self):
        excluded_pages = [0, 1]
        for page in range(self.contents.getNumPages()):
            if page not in excluded_pages:
                new_page = self.contents.getPage(page)
                self.output_pdf.addPage(new_page)
        return

    def copy_pdf_as_is(self):
        for page in range(self.contents.getNumPages()):
            new_page = self.contents.getPage(page)
            self.output_pdf.addPage(new_page)
        return

    def write_output_to_disk(self):
        with open(f"output_pdfs/{self.filename.split('/')[-1]}", "wb") as my_pdf:
            self.output_pdf.write(my_pdf)
        return

    def process_pdf(self):
        if self.has_a_cover_page() is True:
            self.delete_cover_pages()
        else:
            self.copy_pdf_as_is()
        self.write_output_to_disk()
        return


if __name__ == "__main__":
    pdf_name = "PDF.pdf"
    x = PdfManipulator(f"/home/mark/PycharmProjects/islandora_to_digital_commons/test_files/{pdf_name}")
    x.process_pdf()
