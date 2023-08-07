import discord
import json
from discord.ext import commands
from flask import Flask, jsonify, request
from threading import Thread

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

app = Flask(__name__)

def load_unverified_data():
    try:
        with open('unverified.json', 'r') as unverified_file:
            return json.load(unverified_file)
    except FileNotFoundError:
        return []

awaiting_verification = load_unverified_data()

def load_verified_data():
    try:
        with open('verified.json', 'r') as verified_file:
            return json.load(verified_file)
    except FileNotFoundError:
        return []

verified_data = load_verified_data()

def load_configurations():
    try:
        with open('configurations.json', 'r') as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        return {}

configurations = load_configurations()

@app.route('/verification/<roblox_username>', methods=['GET'])
def verify_user(roblox_username):
    for data in awaiting_verification:
        if data['roblox_username'] == roblox_username:
            awaiting_verification.remove(data)
            verified_data.append(data)
            with open('unverified.json', 'w') as unverified_file:
                json.dump(awaiting_verification, unverified_file)
            with open('verified.json', 'w') as verified_file:
                json.dump(verified_data, verified_file)
            return 'verified'
    return 'not_verified'

def run_flask():
    app.run(host='0.0.0.0', port=3000)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    # Start Flask server in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

@bot.command()
async def verify(ctx, roblox_username):
    data = {
        'discord_id': str(ctx.author.id),
        'roblox_username': roblox_username
    }
    awaiting_verification.append(data)
    with open('unverified.json', 'w') as unverified_file:
        json.dump(awaiting_verification, unverified_file)
    await ctx.send(f'Username {roblox_username} has been saved for verification.')


@bot.command()
async def checkverify(ctx):
    user_id = str(ctx.author.id)
    for data in verified_data:
        if data['discord_id'] == user_id:
            await ctx.send(f'You are verified as {data["roblox_username"]} on Roblox!')
            return
    await ctx.send('You are not verified.')




configurations = {}



@bot.command()
@commands.has_permissions(administrator=True)
async def config(ctx, option=None, value=None):
    if option is None:
        await ctx.send('Usage: !config <option> <value>')
    elif option == 'nickname':
        if value == 'true':
            configurations[str(ctx.guild.id)] = {'nickname': True, 'roles': False}
            await ctx.send('Configured to change nicknames for verified users.')
        elif value == 'false':
            configurations[str(ctx.guild.id)] = {'nickname': False, 'roles': False}
            await ctx.send('Configured to not change nicknames for verified users.')
    elif option == 'roles':
        if value == 'true':
            roles = [role.name for role in ctx.guild.roles]
            await ctx.send(f'Available roles: {", ".join(roles)}')
            await ctx.send('Usage: !config roles <role_name>')
        elif value == 'false':
            configurations[str(ctx.guild.id)] = {'nickname': False, 'roles': False}
            await ctx.send('Configured to not give roles to verified users.')

@bot.command()
@commands.has_permissions(administrator=True)
async def roles(ctx, role_name=None):
    if role_name is None:
        await ctx.send('Usage: !roles <role_name>')
    else:
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role:
            configurations[str(ctx.guild.id)]['roles'] = role_name
            await ctx.send(f'Configured to give the {role_name} role to verified users.')
        else:
            await ctx.send(f'Role {role_name} not found.')

@bot.command()
async def verifycheck(ctx):
    user_id = str(ctx.author.id)
    for data in verified_data:
        if data['discord_id'] == user_id:
            server_id = str(ctx.guild.id)
            if configurations.get(server_id, {}).get('roles'):
                role_name = configurations[server_id]['roles']
                role = discord.utils.get(ctx.guild.roles, name=role_name)
                if role:
                    await ctx.author.add_roles(role)
            if configurations.get(server_id, {}).get('nickname'):
                roblox_username = next((data['roblox_username'] for data in verified_data if data['discord_id'] == user_id), None)
                if roblox_username:
                    await ctx.author.edit(nick=f'{roblox_username}')
            await ctx.send(f'You have been verified as {data["roblox_username"]} on Roblox!')


@bot.event
async def on_member_join(member):
    user_id = str(member.id)
    for data in verified_data:
        if data['discord_id'] == user_id:
            server_id = str(member.guild.id)
            configurations[server_id] = configurations.get(server_id, {'nickname': False, 'roles': False})
            if configurations[server_id]['roles']:
                role_name = configurations[server_id]['roles']
                role = discord.utils.get(member.guild.roles, name=role_name)
                if role:
                    await member.add_roles(role)
            if configurations[server_id]['nickname']:
                roblox_username = next((data['roblox_username'] for data in verified_data if data['discord_id'] == user_id), None)
                if roblox_username:
                    await member.edit(nick=f'discord.user ({roblox_username})')

# Save configurations to configurations.json on bot shutdown
@bot.event
async def on_disconnect():
    with open('configurations.json', 'w') as config_file:
        json.dump(configurations, config_file)


@bot.command()
async def test(ctx):
  embed=discord.Embed()
  embed.set_author(name="Justin 😂",icon_url="https://cdn.discordapp.com/attachments/1005543274938912768/1066089443066396792/IMG_6778.jpg")
  embed.add_field(name="undefined", value="undefined", inline=True)
  await ctx.send(embed=embed)



# Replace 'YOUR_DISCORD_BOT_TOKEN' with your actual bot token
bot.run('MTEzNjY1MzYxNjg2NjkzODk3MA.Gv_-dl.o5IH6tFLExzUIdVRxZaE_heF0uZ_1IIO8ccHEw')
