import os
import discord
import pandas
from discord.ext import commands
from discord.ext import tasks
from dotenv import load_dotenv

# Set intents - see: https://discordpy.readthedocs.io/en/stable/intents.html
intents = discord.Intents.default()
intents.members = True

# Loads the .env file on the same level folder as this script which stores your bot token and server ID.
load_dotenv()

# Grab the bot API token and server ID from the .env file
TOKEN = os.getenv("BOT_TOKEN")
SERVER_ID = os.getenv("SERVER_ID")

#Set the prefix for your bot command, this is what you'll type to activate the bot
prefix = "?"

#Create the bot
bot = commands.Bot(command_prefix=prefix, intents=intents)

#Create a guild based on your server's ID
GUILD = bot.get_guild(SERVER_ID)

#Load the CSV so we can query the member list
colnames = ['name']
data = pandas.read_csv('mintlist.csv', names=colnames, converters={i: str for i in range(0, 100)})

# removing null values to avoid errors 
data.dropna(inplace = True) 
  
# storing dtype before operation
dtype_before = type(data["name"])
  
# converting to list
mintlist_lookup_list = data["name"].tolist()

# Convert to lowercase for better string matching
for i in range(len(mintlist_lookup_list)):
    mintlist_lookup_list[i] = mintlist_lookup_list[i].lower()
#print(mintlist_lookup_list)


@tasks.loop(seconds = 30) #this is the auto loop, control the freq using the seconds variable
async def myLoop():
    print("｡･::･ﾟ★,｡･:Scheduled Mintlist verification starting:･｡★ ﾟ･::･｡") 
    for guild in bot.guilds:

        #Counter for confirmation output
        newMintListCounter = 0

        for member in guild.members:
            #print(f"{member.name}#{member.discriminator}") #Debug display which member we are checking

            #Rebuild member name to match string in csv 
            lookupName = member.name + '#' + member.discriminator

            #Rebuild member name to match string in csv 
            lookupID = "<@" + str(member.id) + ">"

            #Check against csv list
            if (lookupName in mintlist_lookup_list) or (lookupID in mintlist_lookup_list):
                #TODO Check if user already has mint list role then ignore
                #Fetch the mintlist role and assign it
                MLRole = guild.get_role(0000000000000) #this is the role ID for allowlist from your server 
                
                if MLRole not in member.roles:
                    await member.add_roles(MLRole)
                    print(lookupID + " Added to Mint List")
                    newMintListCounter+=1
        
        print("｡･::･ﾟ★,｡･:Scheduled Mintlist verification complete:･｡★ ﾟ･::･｡") 


@bot.event
async def on_ready(): #Runs on bot start-up
    print("Everything is all ready to go~")

    # Will show all the servers (guilds) your bot is connected to
    for guild in bot.guilds:
            if guild.name == GUILD:
                break
            
            print(
                f'{bot.user} is connected to the following guild:\n'
                f'{guild.name}  → id: {guild.id}'
            )

    if not myLoop.is_running():
        myLoop.start() 


@bot.command()
async def csv(ctx):
    '''
    Loops through all server members and checks match against mintlist csv by username then assigns role
    '''

    await ctx.send("｡･::･ﾟ★,｡･:Running mintlist verification:･｡★ ﾟ･::･｡")

    #Debug to print all rows in csv
    #print(mintlist_lookup_list)

    for guild in bot.guilds:

        #Counter for confirmation output
        newMintListCounter = 0

        for member in guild.members:
            #print(f"{member.name}#{member.discriminator}") #Debug display which member we are checking

            #Rebuild member name to match string in csv 
            lookupName = member.name + '#' + member.discriminator
            lookupName = lookupName.lower()

            #Rebuild member name to match string in csv 
            lookupID = "<@" + str(member.id) + ">"
            lookupID = lookupID.lower()


            #Check against csv list
            if (lookupName in mintlist_lookup_list) or (lookupID in mintlist_lookup_list):
                #TODO Check if user already has mint list role then ignore
                #Fetch the mintlist role and assign it
                MLRole = guild.get_role(0000000000000) #this is the role ID for allowlist from your server
                
                if MLRole not in member.roles:
                    await member.add_roles(MLRole)
                    await ctx.send(lookupID + " Added to Mint List") #this is sent to the channel as a message
                    newMintListCounter+=1
                
        #Send confirmation to the channel
        await ctx.send("｡･::･ﾟ★,｡･:Mintlist verification complete:･｡★ ﾟ･::･｡") 
        if (newMintListCounter == 0) or (newMintListCounter > 1):
            await ctx.send("｡･::･ﾟ★,｡･:" + str(newMintListCounter) + " new mintlist member added!" + ":･｡★ ﾟ･::･｡")
        else:                
            await ctx.send("｡･::･ﾟ★,｡･:" + str(newMintListCounter) + " new mintlist members added!" + ":･｡★ ﾟ･::･｡")


bot.run(TOKEN)