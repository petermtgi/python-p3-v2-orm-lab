from __init__ import CURSOR, CONN
from employee import Employee

class Review:
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.set_year(year)
        self.set_summary(summary)
        self.set_employee_id(employee_id)

    def __repr__(self):
        return f"<Review {self.id}: Year {self.year}, Summary: {self.summary}, Employee ID: {self.employee_id}>"

    # ---------- YEAR ----------
    def get_year(self):
        return self._year

    def set_year(self, value):
        if isinstance(value, int) and 2000 <= value <= 2100:
            self._year = value
        else:
            raise ValueError("Year must be an integer between 2000 and 2100")

    year = property(get_year, set_year)

    # ---------- SUMMARY ----------
    def get_summary(self):
        return self._summary

    def set_summary(self, value):
        if isinstance(value, str) and value.strip():
            self._summary = value
        else:
            raise ValueError("Summary must be a non-empty string")

    summary = property(get_summary, set_summary)

    # ---------- EMPLOYEE ID ----------
    def get_employee_id(self):
        return self._employee_id

    def set_employee_id(self, value):
        if isinstance(value, int) and Employee.find_by_id(value):
            self._employee_id = value
        else:
            raise ValueError("Employee ID must reference a valid employee")

    employee_id = property(get_employee_id, set_employee_id)

    # ---------- DATABASE ----------
    @classmethod
    def create_table(cls):
        CURSOR.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                year INTEGER,
                summary TEXT,
                employee_id INTEGER,
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
        """)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CURSOR.execute("DROP TABLE IF EXISTS reviews")
        CONN.commit()

    def save(self):
        if self.id is None:
            CURSOR.execute(
                "INSERT INTO reviews (year, summary, employee_id) VALUES (?, ?, ?)",
                (self.year, self.summary, self.employee_id)
            )
            self.id = CURSOR.lastrowid
            type(self).all[self.id] = self
            CONN.commit()

    def update(self):
        if self.id:
            CURSOR.execute(
                "UPDATE reviews SET year = ?, summary = ?, employee_id = ? WHERE id = ?",
                (self.year, self.summary, self.employee_id, self.id)
            )
            CONN.commit()

    def delete(self):
        if self.id:
            CURSOR.execute("DELETE FROM reviews WHERE id = ?", (self.id,))
            CONN.commit()
            del type(self).all[self.id]
            self.id = None

    # ---------- CLASS HELPERS ----------
    @classmethod
    def create(cls, year, summary, employee_id):
        review = cls(year, summary, employee_id)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        id, year, summary, employee_id = row
        review = cls.all.get(id)
        if review:
            review.set_year(year)
            review.set_summary(summary)
            review.set_employee_id(employee_id)
        else:
            review = cls(year, summary, employee_id, id=id)
            cls.all[id] = review
        return review

    @classmethod
    def get_all(cls):
        rows = CURSOR.execute("SELECT * FROM reviews").fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def find_by_id(cls, id):
        row = CURSOR.execute("SELECT * FROM reviews WHERE id = ?", (id,)).fetchone()
        return cls.instance_from_db(row) if row else None
