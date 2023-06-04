import sqlite3

class BotDB:

	def __init__(self, db_file):
		self.conn = sqlite3.connect(db_file)
		self.cursor = self.conn.cursor()

	def user_exists(self, user_id):
		result = self.cursor.execute("SELECT * FROM `users` WHERE `user_id` = ?", (user_id,))
		return result.fetchall()

	def add_user(self, user_id):
		self.cursor.execute("INSERT INTO `users` (`user_id`) VALUES (?)", (user_id,))
		return self.conn.commit()

	def get_user(self, user_id):
		result = self.cursor.execute("SELECT * FROM `users` WHERE `user_id` = ?", (user_id,))
		return result.fetchone()

	def get_users(self):
		return self.cursor.execute('SELECT * FROM users').fetchall()

	def ref_user(self, ref_id):
		self.cursor.execute("UPDATE `users` SET `invited` = invited + 1, `balance` = balance + 100 WHERE `user_id` = ?", (ref_id,))
		return self.conn.commit()

	def change_user_balance(self, operation, value, user_id):
		if operation == "+":
			self.cursor.execute("UPDATE `users` SET `balance` = `balance` + ? WHERE `user_id` = ?", (value, user_id))
		elif operation == "-":
			self.cursor.execute("UPDATE `users` SET `balance` = `balance` - ? WHERE `user_id` = ?", (value, user_id))
		return self.conn.commit()

	def update_user_last_bonus_date(self, date, user_id):
		self.cursor.execute("UPDATE `users` SET `bonus_date` = ? WHERE `user_id` = ?", (date, user_id,))
		return self.conn.commit()

	def add_channel(self, name, link, channel_id):
		self.cursor.execute(f'INSERT INTO channels (name, link, id) VALUES (?, ?, ?)', (name, link, channel_id,))
		return self.conn.commit()
	
	def delete_channel(self, channel_id):
		self.cursor.execute(f'DELETE FROM channels WHERE id = ?', (channel_id,))
		return self.conn.commit()

	def get_channels(self):
		result = self.cursor.execute("SELECT * FROM `channels`")
		return result.fetchall()


BotDB('database.db')