
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
    
    def get_all_motherboards_by_manufacturer(self, manufacturer):
        sql = 'SELECT * FROM motherboard_items WHERE manufacturer = \'?\''
        sql = sql.replace('?', manufacturer)
        print(sql)
        rows = self.db.cursor.execute(sql)
        # fetch all rows from the database table like a list of associative arrays
        result = rows.fetchall()
        print(result)
        exit()
        motherboards = []
        for row in result:
            row_dict = dict(row)
            motherboards.append(MotherboardItem(row_dict['id'], row_dict['orig_id'], row_dict['title'], row_dict['price'], row_dict['link'], row_dict['description'], row_dict['category'], row_dict['manufacturer']))

        return motherboards