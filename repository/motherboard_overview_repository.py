from models.motherboard_overview import MotherboardOverview

class MotherboardOverviewRepository:
    def __init__(self, db):
        self.db = db

    def add(self, motherboard_overview):
        self.db.cursor.execute('INSERT INTO motherboard_overviews (mb_item_id, type, text) VALUES (?, ?, ?)',
            (motherboard_overview.mb_item_id, motherboard_overview.type, motherboard_overview.text))
        self.db.conn.commit()
        return self.db.cursor.lastrowid
        
    def update(self, motherboard_overview):
        self.db.cursor.execute(
            'UPDATE motherboard_overviews SET type = ?, text = ? WHERE id = ?',
            (motherboard_overview.type, motherboard_overview.text, motherboard_overview.id))
        self.db.conn.commit()
        
    def delete(self, id):
        self.db.cursor.execute('DELETE FROM motherboard_overviews WHERE id = ?', (id,))

    def getById(self, id):
        row = self.db.cursor.execute('SELECT * FROM motherboard_overviews WHERE id = ?', (id,))
        result = row.fetchone()
        if result is None:
            return None
        result_dict = dict(result)
        return MotherboardOverview(result_dict['id'], result_dict['mb_item_id'], result_dict['type'], result_dict['text'], result_dict['updated_at'])
    
    def getByMbItemId(self, mb_item_id):
        row = self.db.cursor.execute('SELECT * FROM motherboard_overviews WHERE mb_item_id = ?', (mb_item_id,))
        result = row.fetchone()
        if result is None:
            return None
        result_dict = dict(result)
        return MotherboardOverview(result_dict['id'], result_dict['mb_item_id'], result_dict['type'], result_dict['text'], result_dict['updated_at'])
        
    def getAllOverviewsByMbItemId(self, mb_item_id):
        rows = self.db.cursor.execute('SELECT * FROM motherboard_overviews WHERE mb_item_id = ?', (mb_item_id,))
        result = rows.fetchall()
        overviews = []
        for row in result:
            row_dict = dict(row)
            overviews.append(MotherboardOverview(row_dict['id'], row_dict['mb_item_id'], row_dict['type'], row_dict['text'], row_dict['updated_at']))

        return overviews
    
    def getOverviewsByMbItemIdTypeText(self, mb_item_id, type, text):
        row = self.db.cursor.execute('SELECT * FROM motherboard_overviews WHERE mb_item_id = ? AND type = ? AND text = ?', (mb_item_id, type, text))
        result = row.fetchone()
        if result is None:
            return None
        result_dict = dict(result)
        return MotherboardOverview(result_dict['id'], result_dict['mb_item_id'], result_dict['type'], result_dict['text'], result_dict['updated_at'])
    
    def getOverviewsByMbItemIdType(self, mb_item_id, type):
        rows = self.db.cursor.execute('SELECT * FROM motherboard_overviews WHERE mb_item_id = ? AND type = ?', (mb_item_id, type))
        result = rows.fetchall()
        overviews = []
        for row in result:
            row_dict = dict(row)
            overviews.append(MotherboardOverview(row_dict['id'], row_dict['mb_item_id'], row_dict['type'], row_dict['text'], row_dict['updated_at']))

        return overviews
    
    def getAllByType(self, type, manufacture):
        rows = self.db.cursor.execute('SELECT * FROM motherboard_overviews WHERE type = ? AND manufacture = ?', (type, manufacture))
        result = rows.fetchall()
        overviews = []
        for row in result:
            row_dict = dict(row)
            overviews.append(MotherboardOverview(row_dict['id'], row_dict['mb_item_id'], row_dict['type'], row_dict['text'], row_dict['updated_at']))

        return overviews