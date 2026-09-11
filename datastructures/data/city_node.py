class CityNode:
    SORT_KEYS = {"id", "city_name"}  # add "longitude", etc. here later

    def __init__(self, id, city_name, state, latitude, longitude, listed, sort_key="id"):
        self.id = id
        self.city_name = city_name
        self.state = state
        self.latitude = latitude
        self.longitude = longitude
        self.listed = listed

        if sort_key not in self.SORT_KEYS:
            raise ValueError(f"Invalid sort_key '{sort_key}'")
        self.sort_key = sort_key

    def _key(self):
        return getattr(self, self.sort_key)

    def __lt__(self, other):
        return self._key() < other._key()

    def __gt__(self, other):
        return self._key() > other._key()

    def __eq__(self, other):          # identity stays id-based, always
        if not isinstance(other, CityNode):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def to_dict(self):
        return {
            "id": self.id, "city_name": self.city_name, "state": self.state,
            "latitude": self.latitude, "longitude": self.longitude, "listed": self.listed,
        }

    def __str__(self):
        return f"{self.id} - {self.city_name}"

    def __repr__(self):
        return f"CityNode({self.id!r}, {self.city_name!r})"