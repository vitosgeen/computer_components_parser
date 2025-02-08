class MotherboardSupport:
    TYPE_CPU = "cpu"
    TYPE_MEMORY = "memory"
    TYPE_DEVICE = "device"
    TYPE_VGA = "vga"
    TYPE_STORAGE = "storage"
    
    def __init__(self, id, mb_item_id, type, data, updated_at=None):
        self.id = id
        self.mb_item_id = mb_item_id
        self.type = type
        self.data = data
        self.updated_at = updated_at

    @classmethod
    def from_dict(self, data):
        return MotherboardSupport(
            id=data["id"],
            mb_item_id=data["mb_item_id"],
            type=data["type"],
            data=data["data"],
            updated_at=data["updated_at"]
        )
    
    def to_dict(self):
        return {
            "id": self.id,
            "mb_item_id": self.mb_item_id,
            "type": self.type,
            "data": self.data,
            "updated_at": self.updated_at
        }
    
    def names_of_types():
        return {
            MotherboardSupport.TYPE_CPU: "CPU",
            MotherboardSupport.TYPE_MEMORY: "Memory",
            MotherboardSupport.TYPE_DEVICE: "Device"
        }