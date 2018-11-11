from dataclasses import dataclass
import arrow
import yaml


@dataclass()
class ErrorLog:
    filename: str

    def write_error(self, message: str):
        with open(self.filename, "a+") as our_error_log:
            our_error_log.write(f"{arrow.utcnow().to('US/Eastern')}: {message}\n")
        return


settings = yaml.load(open("config/config.yml", "r"))
error_log = ErrorLog(settings["error_log"])
