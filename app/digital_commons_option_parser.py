from lxml import etree


class OptionWriter:
    def __init__(self, options_file, output_file):
        self.contents = self._read_options(options_file)
        self.output_file = output_file

    @staticmethod
    def _read_options(file):
        contents = etree.parse(file)
        options = contents.findall(".//option")
        return [option.text for option in options]

    def write_options(self):
        with open(f"option_output/{self.output_file}", "w") as output_file:
            for option in self.contents:
                output_file.write(f"{option}\n")


if __name__ == "__main__":
    OptionWriter(
        "/home/mark/PycharmProjects/islandora_to_digital_commons/data/trace_majors.xml",
        "majors.txt",
    ).write_options()
