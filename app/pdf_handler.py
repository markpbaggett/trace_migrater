from PyPDF2 import PdfFileWriter, PdfFileReader


class PdfManipulator:
    def __init__(self, filename, output_directory="output_pdfs"):
        self.filename = filename
        self.contents = PdfFileReader(filename, "rb")
        self.output_pdf = PdfFileWriter()
        self.output_directory = output_directory

    def has_a_cover_page(self):
        if self.contents.getPage(1).extractText().startswith("Accepted for the Council:"):
            return True
        elif self.contents.getPage(1).extractText().startswith("To the Graduate Council:"):
            return True
        else:
            print(f"No cover page: {self.contents.getPage(1).extractText()}\n "
                  f"\n{self.contents.getPage(1).extractText()}")
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
        with open(f"{self.output_directory}/{self.filename.split('/')[-1]}", "wb") as my_pdf:
            # print(f"Writing {self.filename.split('/', [-1])} to {self.output_directory}.\n")
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
    pdf_name = "utk.ir.td:117.pdf"
    x = PdfManipulator(f"/home/mark/PycharmProjects/islandora_to_digital_commons/for_dlshare/embargoed_files/"
                       f"{pdf_name}")
    x.process_pdf()
