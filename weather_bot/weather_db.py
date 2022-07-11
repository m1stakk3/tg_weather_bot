import psycopg2

class WeatherDB:

    def __init__(self):
        """Инициализация соединения с БД"""
        self.conn = psycopg2.connect(database="tg_weather_test",
                                    user="postgres",
                                    password="1",
                                    host="127.0.0.1",
                                    port="5432")
        self.cursor = self.conn.cursor()

    def user_exists(self, user_id):
        """Проверка, есть ли юзер в БД"""
        self.cursor.execute(f"SELECT id FROM users WHERE user_id = {user_id}")
        result = bool(len(self.cursor.fetchall()))
        return result

    def get_user_id(self, user_id):
        """Получение id юзера по его user_id телеграма"""
        self.cursor.execute(f"SELECT id FROM users WHERE user_id = {user_id}")
        result = self.cursor.fetchone()[0]
        return result

    def add_user(self, user_id,city,lat,lon):
        """Создание записи о новом юзере"""
        self.cursor.execute(f"INSERT INTO users(user_id, city, lat, lon) VALUES ({user_id},'{city}',{lat},{lon})")
        return self.conn.commit()

    def current_city(self, user_id):
        self.cursor.execute(f"SELECT city FROM users WHERE user_id = {user_id}")
        result = self.cursor.fetchone()[0]
        return result

    def update_city(self, user_id, new_city):
        self.cursor.execute(f"UPDATE users SET city = '{new_city}' WHERE user_id = {user_id}")
        return self.conn.commit()

    def del_user(self, user_id):
        self.cursor.execute(f"DELETE FROM users WHERE user_id = {user_id}")
        return self.conn.commit()

    def close(self):
        """Закрытие соединения с БД"""
        self.conn.close()