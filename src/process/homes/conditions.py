from dataclasses import asdict, dataclass


@dataclass
class HomesConditions:
    name: str = ""
    prefecture: str = ""
    city: str = ""
    town: str = ""
    time_walk: str | int = ""

    def to_dict(self):
        return asdict(self)

    def linked_element_dict(self):
        return {
            "prefecture": {"tag": "a", "to_input": "/div/input"},
            "time_walk": {"tag": "label", "to_input": "/input"},
            "year_passed": {"tag": "label", "to_input": "/input"},
            "property_kind": {"tag": "text()", "to_input": "/input"},
        }

    def trans_raw_time_walk(self):
        w_t = self.time_walk
        if type(w_t) == "str":
            return

        # 名寄せデータ上のtimewalkが正確かわからないため、
        # w_tの適切な徒歩分数範囲(例：timewalk=3なら"7分以内")より１ランク上のものを適用している
        if w_t <= 1:
            self.time_walk = "5分以内"
        elif w_t <= 5:
            self.time_walk = "7分以内"
        elif w_t <= 7:
            self.time_walk = "10分以内"
        elif w_t <= 10:
            self.time_walk = "15分以内"
        elif w_t <= 20:
            self.time_walk = "20分以内"
        else:
            self.time_walk = ""
