from dataclasses import asdict, dataclass


@dataclass
class SuumoConditions:
    property_name: str = ""
    prefecture: str = ""
    time_walk: str = ""
    year_passed: str = ""
    property_kind: str = ""

    def to_dict(self):
        return asdict(self)

    def linked_element_dict(self):
        return {
            "prefecture": {"tag": "a", "to_input": "/div/input"},
            "time_walk": {"tag": "label", "to_input": "/input"},
            "year_passed": {"tag": "label", "to_input": "/input"},
            "property_kind": {"tag": "text()", "to_input": "/input"},
        }
