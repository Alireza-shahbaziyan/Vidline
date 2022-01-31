from pyrogram.types import InputMediaDocument, InputMediaPhoto, InputMediaVideo
from tiktok_downloader import snaptik
from pyrogram import Client, filters
from tinydb import TinyDB, where
from pytube import YouTube
import subprocess
from . import var
import filetype
import glob, os
import shutil
import uuid
import re




def gallery_dl_filter(_, client, message):
	
	regex = [
		r"^http\S*instagram\.com\S*$",
		r"^http\S*twitter\.com\S*$",
		r"^http\S*reddit\.com\S*$"
	]

	try:
		res = re.findall("|".join(regex), message.text)
		if res != []:
			return True
		else:
			raise
	except:
		return False



def user_manager(uid):

	db  = TinyDB("databases/users.json")
	user = db.get(where("id") == uid)
	if user == None:
		db.insert({
			"id": uid,
			"username": None,
			"password": None,
			"status": None
		})


def file_type(path):
	
	# cwd = os.getcwd()
	kind  = filetype.guess(path)
	ftype = kind.mime.split("/")[0]
	return ftype


def channel_lock(client, message):
	
	uid = message.from_user.id

	# On/Off
	return True


	try:

		result =  client.get_chat_member(var.public_channel, uid)
		return True

	except:
		return False



@Client.on_message(filters.private & filters.command("start"))
def start(client, message):

	uid = message.from_user.id
	user_manager(uid)

	if not  channel_lock(client, message):
		client.send_message(uid, var.channel_lock_text)
		return

	message.reply_text(var.start_text)





# gallery_dl
@Client.on_message(filters.private & filters.create(gallery_dl_filter))
def gallery_dl(client, message):

	# print("run")
	# return

	url = message.text
	uid = message.from_user.id
	mid = message.message_id
	fid = str(uuid.uuid4())

	post =  message.reply_text("Fetching...", reply_to_message_id = mid)

	args = [
		"gallery-dl",
		"-c",
		"c.conf",
		"-D",
		f"downloads/{fid}",
		f"{url}"
	]


	# download
	try:
		post.edit("📤 downloading file...")
		subprocess.check_output(args)
	except Exception as e:
		# print(e)
		post.edit("An error occurred, it may be a private account.")
		return


	# upload
	post.edit("📤 uploading file...")

	files = []
	for file in glob.glob(f"./downloads/{fid}/*.*"):
		files.append(file)

	# print(files)

	try:
		
		if len(files) == 0: raise
		if len(files) == 1:

			path = files[0]
			client.send_document(uid, path)
			post.delete()

		else:
			
			docs = []
			for path in files:

				ftype = file_type(path)
				if ftype == "image":
					docs.append(InputMediaPhoto(path))
				else: 
					docs.append(InputMediaVideo(path))

			# print(docs)
			client.send_media_group(uid, docs)
			post.delete()

	except Exception as e:

		try:
			for path in files:
				client.send_document(uid, path)

			post.delete()
		except:
			# client.send_message(var.sudo, e)
			post.edit("❌ error, wait for bot owner to fix")

	# removing
	try:
		shutil.rmtree(f"downloads/{fid}")
	except Exception as e:
		# client.send_message(var.sudo, e)
		pass


	
# tiktok downloader
@Client.on_message(filters.private & filters.regex(r"^http\S*tiktok\.com\S*$"))
def tiktok(client, message):

	mid  = message.message_id
	post = message.reply_text("Fetching...", reply_to_message_id = mid)

	url = message.text
	uid = message.from_user.id
	fid = str(uuid.uuid4())

	# download
	try:
		post.edit("📤 downloading file...")
		snaptik(url).get_media()[0].download(f"downloads/{fid}.mp4")
	except Exception as e:
		# client.send_message(var.sudo, d)
		post.edit("I can't found this post!")
		return

	# upload
	try:
		post.edit("📤 uploading file...")
		client.send_document(uid, f"downloads/{fid}.mp4")
		post.delete()
	except:
		post.edit("❌ error, wait for bot owner to fix")


	try:
		os.remove(f"downloads/{fid}.mp4")
	except:
		pass














# youtube-dl
@Client.on_message(filters.private & filters.regex(r"^http\S*youtu\.be\S*$"))
def youtube_dl(client, message):
	
	mid  = message.message_id
	post = message.reply_text("Fetching...", reply_to_message_id = mid)

	url = message.text
	uid = message.from_user.id
	fid = str(uuid.uuid4())


	# download
	yt = YouTube(url)
	try:
		post.edit("📤 downloading file...")
		yt.streams.get_highest_resolution().download(filename = f"downloads/{fid}.mp4")

	except Exception as e:
		# print(e)
		post.edit("Not found!")
		return


	# extract audio
	# cwd = os.getcwd()
	args = [
		"ffmpeg",
		"-i",
		f"downloads/{fid}.mp4",
		"-f",
		"mp3",
		"-ab",
		"192000",
		"-vn",
		f"downloads/{fid}.mp3"
	]

	try:
		post.edit("extract audio...")
		subprocess.check_output(args)
	except:
		pass



	# upload
	try:

		post.edit("📤 uploading file...")
		vid = client.send_video(uid, f"downloads/{fid}.mp4")
		client.send_audio(uid, f"downloads/{fid}.mp3", title = yt.title, reply_to_message_id = vid.message_id)
		post.delete()

	except:
		post.edit("❌ error, wait for bot owner to fix")


	# delete
	try:
		os.remove(f"downloads/{fid}.mp4")
		os.remove(f"downloads/{fid}.mp3")
	except:
		pass

