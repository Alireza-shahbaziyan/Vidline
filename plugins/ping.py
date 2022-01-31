from pyrogram import Client, filters
from ping3 import ping
from . import var
import time


@Client.on_message(filters.user(var.sudo) & filters.private & filters.command("ping"))
def pong(client, message):

	post = message.reply_text("...")

	get_ping = int(float(ping("www.google.com")) * 1000)
	time.sleep(0.5)

	post.edit(f"**{str(get_ping)}** ms", parse_mode = "markdown")