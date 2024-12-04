class Motherboard:
    def __init__(self, brand, model, socket, chipset, form_factor, updated_at=None):
        self.brand = brand
        self.model = model
        self.socket = socket
        self.chipset = chipset
        self.form_factor = form_factor
        self.updated_at = updated_at

    @classmethod
    def from_dict(self, data):
        return Motherboard(
            brand=data["brand"],
            model=data["model"],
            socket=data["socket"],
            chipset=data["chipset"],
            form_factor=data["form_factor"],
            updated_at=data["updated_at"]
        )