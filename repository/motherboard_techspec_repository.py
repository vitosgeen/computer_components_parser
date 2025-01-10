from models.motherboard_techspec import MotherboardTechSpec

class MotherboardTechSpecRepository:
    def __init__(self, db):
        self.db = db

    def add(self, motherboard_techspec):
        self.db.cursor.execute('INSERT INTO motherboard_techspecs (mb_item_id, type, text) VALUES (?, ?, ?)',
            (motherboard_techspec.mb_item_id, motherboard_techspec.type, motherboard_techspec.text))
        self.db.conn.commit()
        return self.db.cursor.lastrowid
    
    def update(self, motherboard_techspec):
        self.db.cursor.execute(
            'UPDATE motherboard_techspecs SET type = ?, text = ? WHERE id = ?',
            (motherboard_techspec.type, motherboard_techspec.text, motherboard_techspec.id))
        self.db.conn.commit()

    def delete(self, id):
        self.db.cursor.execute('DELETE FROM motherboard_techspecs WHERE id = ?', (id,))
        
    def getById(self, id):
        row = self.db.cursor.execute('SELECT * FROM motherboard_techspecs WHERE id = ?', (id,))
        result = row.fetchone()
        if result is None:
            return None
        result_dict = dict(result)
        return MotherboardTechSpec(result_dict['id'], result_dict['mb_item_id'], result_dict['type'], result_dict['text'], result_dict['updated_at'])
    
    def getByMbItemId(self, mb_item_id):
        row = self.db.cursor.execute('SELECT * FROM motherboard_techspecs WHERE mb_item_id = ?', (mb_item_id,))
        result = row.fetchone()
        if result is None:
            return None
        result_dict = dict(result)
        return MotherboardTechSpec(result_dict['id'], result_dict['mb_item_id'], result_dict['type'], result_dict['text'], result_dict['updated_at'])
    
    def getAllTechSpecsByMbItemId(self, mb_item_id):
        rows = self.db.cursor.execute('SELECT * FROM motherboard_techspecs WHERE mb_item_id = ?', (mb_item_id,))
        result = rows.fetchall()
        techspecs = []
        for row in result:
            row_dict = dict(row)
            techspecs.append(MotherboardTechSpec(row_dict['id'], row_dict['mb_item_id'], row_dict['type'], row_dict['text'], row_dict['updated_at']))

        return techspecs
    
    def getTechSpecsByMbItemIdTypeText(self, mb_item_id, type, text):
        row = self.db.cursor.execute('SELECT * FROM motherboard_techspecs WHERE mb_item_id = ? AND type = ? AND text = ?', (mb_item_id, type, text))
        result = row.fetchone()
        if result is None:
            return None
        result_dict = dict(result)
        return MotherboardTechSpec(result_dict['id'], result_dict['mb_item_id'], result_dict['type'], result_dict['text'], result_dict['updated_at'])
    
    def getTechSpecsByMbItemIdType(self, mb_item_id, type):
        rows = self.db.cursor.execute('SELECT * FROM motherboard_techspecs WHERE mb_item_id = ? AND type = ?', (mb_item_id, type))
        result = rows.fetchall()
        techspecs = []
        for row in result:
            row_dict = dict(row)
            techspecs.append(MotherboardTechSpec(row_dict['id'], row_dict['mb_item_id'], row_dict['type'], row_dict['text'], row_dict['updated_at']))

        return techspecs