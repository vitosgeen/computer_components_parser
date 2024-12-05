
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
        result_dict = dict(result)
        return MotherboardItem(result_dict['id'], result_dict['orig_id'], result_dict['title'], result_dict['price'], result_dict['link'], result_dict['description'], result_dict['category'], result_dict['manufacturer'])
    
    def getByLink(self, link):
        row = self.db.cursor.execute('SELECT * FROM motherboard_items WHERE link = ?', (link,))
        result = row.fetchone()
        if result is None:
            return None
        result_dict = dict(result)
        return MotherboardItem(result_dict['id'], result_dict['orig_id'], result_dict['title'], result_dict['price'], result_dict['link'], result_dict['description'], result_dict['category'], result_dict['manufacturer'])
        
    
    def getAllMotherboardsByManufacturer(self, manufacturer):
        rows = self.db.cursor.execute('SELECT * FROM motherboard_items WHERE manufacturer = ?', (manufacturer,))
        result = rows.fetchall()
        motherboards = []
        for row in result:
            row_dict = dict(row)
            motherboards.append(MotherboardItem(row_dict['id'], row_dict['orig_id'], row_dict['title'], row_dict['price'], row_dict['link'], row_dict['description'], row_dict['category'], row_dict['manufacturer']))

        return motherboards