class MotherboardItem:
    def __init__(self, id, orig_id, title, price, link, description, category, manufacturer):
        self.id = id
        self.orig_id = orig_id
        self.title = title
        self.price = price
        self.link = link
        self.description = description
        self.category = category
        self.manufacturer = manufacturer

    @classmethod
    def from_dict(self, data):
        return MotherboardItem(
            id=data["id"],
            orig_id=data["orig_id"],
            title=data["title"],
            price=data["price"],
            link=data["link"],
            description=data["description"],
            category=data["category"],
            manufacturer=data["manufacturer"]
        )
    
    def to_dict(self):
        return {
            "id": self.id,
            "orig_id": self.orig_id,
            "title": self.title,
            "price": self.price,
            "link": self.link,
            "description": self.description,
            "category": self.category,
            "manufacturer": self.manufacturer
        }