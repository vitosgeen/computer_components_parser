class MotherboardOverview:
    TYPE_MODEL = "model"
    TYPE_DESCRIPTION = "description"
    TYPE_NAME = "name"
    def __init__(self, id, mb_item_id, type, text, updated_at=None):
        self.id = id
        self.mb_item_id = mb_item_id
        self.type = type
        self.text = text
        self.updated_at = updated_at

    @classmethod
    def from_dict(self, data):
        return MotherboardOverview(
            id=data["id"],
            mb_item_id=data["mb_item_id"],
            type=data["type"],
            text=data["text"],
            updated_at=data["updated_at"]
        )