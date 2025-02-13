class MotherboardTechSpec:
    # type constants
    TYPE_IMAGE = "image"
    TYPE_NAME = "name"
    TYPE_MODEL = "model"
    TYPE_CPU = "cpu"
    TYPE_CPU_SOCKET = "cpu_socket"
    TYPE_CHIPSET = "chipset"
    TYPE_MEMORY = "memory"
    TYPE_GRAPHICS = "graphics"
    TYPE_STORAGE = "storage"
    TYPE_EXPANSION_SLOTS = "expansion_slots"
    TYPE_LAN = "lan"
    TYPE_USB = "usb"
    TYPE_AUDIO = "audio"
    TYPE_SPECIAL_FEATURES = "special_features"
    TYPE_OPERATING_SYSTEM = "operating_system"
    TYPE_BACK_PANEL_PORTS = "back_panel_ports"
    TYPE_INTERNAL_I_O_PORTS = "internal_i_o_ports"
    TYPE_ACCESSORIES = "accessories"
    TYPE_BIOS = "bios"
    TYPE_MANAGEABILITY = "manageability"
    TYPE_FORM_FACTOR = "form_factor"
    TYPE_NOTE = "note"
    TYPE_SOFTWARE = "software"
    TYPE_OTHER = "other"

    # fields for MotherboardTechSpec
    def __init__(self, id, mb_item_id, type, text, updated_at=None):
        self.id = id
        self.mb_item_id = mb_item_id
        self.type = type
        self.text = text
        self.updated_at = updated_at

    @classmethod
    def from_dict(self, data):
        return MotherboardTechSpec(
            id=data["id"],
            mb_item_id=data["mb_item_id"],
            type=data["type"],
            text=data["text"],
            updated_at=data["updated_at"]
        )
    
    def to_dict(self):
        return {
            "id": self.id,
            "mb_item_id": self.mb_item_id,
            "type": self.type,
            "text": self.text,
            "updated_at": self.updated_at
        }
    
    def names_of_types():
        return {
            MotherboardTechSpec.TYPE_IMAGE: "Image",
            MotherboardTechSpec.TYPE_MODEL: "Model",
            MotherboardTechSpec.TYPE_SOFTWARE: "Software",
            MotherboardTechSpec.TYPE_CPU: "CPU",
            MotherboardTechSpec.TYPE_CPU_SOCKET: "CPU Socket",
            MotherboardTechSpec.TYPE_CHIPSET: "Chipset",
            MotherboardTechSpec.TYPE_MEMORY: "Memory",
            MotherboardTechSpec.TYPE_GRAPHICS: "Graphics",
            MotherboardTechSpec.TYPE_STORAGE: "Storage",
            MotherboardTechSpec.TYPE_EXPANSION_SLOTS: "Expansion Slots",
            MotherboardTechSpec.TYPE_LAN: "LAN",
            MotherboardTechSpec.TYPE_USB: "USB",
            MotherboardTechSpec.TYPE_SPECIAL_FEATURES: "Special Features",
            MotherboardTechSpec.TYPE_OPERATING_SYSTEM: "Operating System",
            MotherboardTechSpec.TYPE_BACK_PANEL_PORTS: "Back Panel Ports",
            MotherboardTechSpec.TYPE_INTERNAL_I_O_PORTS: "Internal I/O Ports",
            MotherboardTechSpec.TYPE_ACCESSORIES: "Accessories",
            MotherboardTechSpec.TYPE_BIOS: "BIOS",
            MotherboardTechSpec.TYPE_MANAGEABILITY: "Manageability",
            MotherboardTechSpec.TYPE_FORM_FACTOR: "Form Factor",
            MotherboardTechSpec.TYPE_NOTE: "Note",
            MotherboardTechSpec.TYPE_OTHER: "Other"
        }