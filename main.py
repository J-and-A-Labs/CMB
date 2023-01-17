import os
import discord
from discord.ext import commands
from quart import Quart, redirect, url_for, render_template, request
from quart_discord import DiscordOAuth2Session, requires_authorization, Unauthorized
import pymongo
from pymongo import MongoClient



cluster = MongoClient(
    "mongodb+srv://re-ed:1234@cluster0.67c89.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

db = cluster["Score"]
collection = db["Score"]  




#Quart
app = Quart(__name__)

token = os.environ['TOKEN']


app.secret_key = "E5R21800"  
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"
app.config["DISCORD_CLIENT_ID"] = 941836303031492659
app.config["DISCORD_CLIENT_SECRET"] = os.environ['CLIENT_SECRET']
app.config["DISCORD_REDIRECT_URI"] = "https://cmb-website-1.gangsterbirdo.repl.co/callback"
app.config["DISCORD_BOT_TOKEN"] = token


discord_session = DiscordOAuth2Session(app)





client = commands.Bot(command_prefix="!")









@app.route("/")
@app.route("/home")
async def home():
  return await render_template("index.html", authorized = await discord_session.authorized,active = "home")

@app.route("/login")
async def login():
	return await discord_session.create_session()

@app.route("/logout")
async def logout():
  discord_session.revoke()
  return redirect(url_for("home"))

@app.route("/disclaimer")
async def disclaimer():
  return await render_template("disclaimer.html", authorized = await discord_session.authorized,active = "disclaimer")

@app.route("/about")
async def about():
  return await render_template("about.html", authorized = await discord_session.authorized,active = "about")

@app.route("/commands")
async def commands():
  return await render_template("commands.html", authorized = await discord_session.authorized,active = "commands")


@app.route("/callback")
async def callback():
	try:
		await discord_session.callback()
	except:
		return redirect(url_for("login"))

	return redirect(url_for("home"))





@app.route("/dashboard")
async def dashboard():
  user = await discord_session.fetch_user()
  user_guilds = await discord_session.fetch_guilds()
  guilds = []
  for x in user_guilds:
    if x.permissions.administrator:
      guilds.append(x)
  stats =collection.find_one({"_id": user.id})
  credit = (stats["xp"])
  salary = stats["salary"]
  bonus = stats["bonus"]
  credit = "{:,}".format(credit)
  job = stats["job"]
  s = str(salary*bonus)
  return await render_template("dashboard.html", username=user.name,guilds = guilds, job = job, credit = credit, salary = s, authorized = await discord_session.authorized ,active = "dashboard")

@app.route("/dashboard/<int:guild_id>")
async def dashboard_server(guild_id):
    if not await discord_session.authorized:
        return redirect(url_for("login")) 
    guild = client.get_guild(guild_id)
    if guild is None:
        return "add the bot to the server dumb fuck"
    else:
      return await render_template("server.html", guild_name = guild.name)

@app.errorhandler(Unauthorized)
async def redirect_unauthorized(e):
  client.url = request.url
  return redirect(url_for("login"))






#dpy
@client.event
async def on_ready():
  print("Bot is Ready")

@client.command()
async def hi(ctx):
  await ctx.send(f"Hello, {ctx.message.author}")

def run():
  client.loop.create_task(app.run_task('0.0.0.0'))
  client.run(token)
  

if __name__ == "__main__":
  run()














#dpy

if __name__ == "__main__":
    	app.run(host='0.0.0.0', port= 8080)