from pyrogram import Client


# app
bot = Client("sessions/api")

if __name__ == "__main__":
	
	print("=================== ON ===================\n")
	bot.run()
	print("\n=================== OFF ===================")