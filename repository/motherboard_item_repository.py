
from models.motherboard_item import MotherboardItem


class MotherboardItemRepository:
    def __init__(self, db):
        self.db = db

    def add(self, motherboard_item):
        self.db.cursor.execute('INSERT INTO motherboard_items (orig_id, title, price, link, description, category, manufacturer) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (motherboard_item.orig_id, motherboard_item.title, motherboard_item.price, motherboard_item.link, motherboard_item.description, motherboard_item.category, motherboard_item.manufacturer))
        self.db.conn.commit()
        return self.db.cursor.lastrowid
        
    def update(self, motherboard_item):
        self.db.cursor.execute(
            'UPDATE motherboard_items SET title = ?, price = ?, link = ?, description = ?, category = ?, manufacturer = ? WHERE id = ?',
            (motherboard_item.title, motherboard_item.price, motherboard_item.link, motherboard_item.description, motherboard_item.category, motherboard_item.manufacturer, motherboard_item.id))
        self.db.conn.commit()
        
    def delete(self, id):
        self.db.cursor.execute('DELETE FROM motherboard_items WHERE id = ?', (id,))

    def getById(self, id):
        row = self.db.cursor.execute('SELECT * FROM motherboard_items WHERE id = ?', (id,))
        result = row.fetchone()
        if result is None:
            return None
        return MotherboardItem(result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7])
    
    def getByLink(self, link):
        row = self.db.cursor.execute('SELECT * FROM motherboard_items WHERE link = ?', (link,))
        result = row.fetchone()
        if result is None:
            return None
        return MotherboardItem(result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7])