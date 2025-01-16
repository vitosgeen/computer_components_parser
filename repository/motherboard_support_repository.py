from models.motherboard_support import MotherboardSupport

class MotherboardSupportRepository:
    def __init__(self, db):
        self.db = db

    def add(self, motherboard_support):
        self.db.cursor.execute('INSERT INTO motherboard_supports (mb_item_id, type, data) VALUES (?, ?, ?)',
            (motherboard_support.mb_item_id, motherboard_support.type, motherboard_support.data))
        self.db.conn.commit()
        return self.db.cursor.lastrowid
    
    def update(self, motherboard_support):
        self.db.cursor.execute(
            'UPDATE motherboard_supports SET type = ?, data = ? WHERE id = ?',
            (motherboard_support.type, motherboard_support.data, motherboard_support.id))
        self.db.conn.commit()

    def delete(self, id):
        self.db.cursor.execute('DELETE FROM motherboard_supports WHERE id = ?', (id,))
        
    def getById(self, id):
        row = self.db.cursor.execute('SELECT * FROM motherboard_supports WHERE id = ?', (id,))
        result = row.fetchone()
        if result is None:
            return None
        result_dict = dict(result)
        return MotherboardSupport(result_dict['id'], result_dict['mb_item_id'], result_dict['type'], result_dict['data'], result_dict['updated_at'])
    
    def getByMbItemId(self, mb_item_id):
        row = self.db.cursor.execute('SELECT * FROM motherboard_supports WHERE mb_item_id = ?', (mb_item_id,))
        result = row.fetchone()
        if result is None:
            return None
        result_dict = dict(result)
        return MotherboardSupport(result_dict['id'], result_dict['mb_item_id'], result_dict['type'], result_dict['data'], result_dict['updated_at'])
    
    def getAllSupportsByMbItemId(self, mb_item_id):
        rows = self.db.cursor.execute('SELECT * FROM motherboard_supports WHERE mb_item_id = ?', (mb_item_id,))
        result = rows.fetchall()
        supports = []
        for row in result:
            row_dict = dict(row)
            supports.append(MotherboardSupport(row_dict['id'], row_dict['mb_item_id'], row_dict['type'], row_dict['data'], row_dict['updated_at']))

        return supports
    
    def getSupportsByMbItemIdTypeData(self, mb_item_id, type, data):
        row = self.db.cursor.execute('SELECT * FROM motherboard_supports WHERE mb_item_id = ? AND type = ? AND data = ?', (mb_item_id, type, data))
        result = row.fetchone()
        if result is None:
            return None
        
        result_dict = dict(result)
        return MotherboardSupport(result_dict['id'], result_dict['mb_item_id'], result_dict['type'], result_dict['data'], result_dict['updated_at'])
    
    def getSupportsByMbItemIdType(self, mb_item_id, type):
        rows = self.db.cursor.execute('SELECT * FROM motherboard_supports WHERE mb_item_id = ? AND type = ?', (mb_item_id, type))
        result = rows.fetchall()
        supports = []
        for row in result:
            row_dict = dict(row)
            supports.append(MotherboardSupport(row_dict['id'], row_dict['mb_item_id'], row_dict['type'], row_dict['data'], row_dict['updated_at']))

        return supports
    
    def getSupportsByMbItemId(self, mb_item_id):
        rows = self.db.cursor.execute('SELECT * FROM motherboard_supports WHERE mb_item_id = ?', (mb_item_id,))
        result = rows.fetchall()
        supports = []
        for row in result:
            row_dict = dict(row)
            supports.append(MotherboardSupport(row_dict['id'], row_dict['mb_item_id'], row_dict['type'], row_dict['data'], row_dict['updated_at']))

        return supports