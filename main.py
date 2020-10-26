import discord
from discord.ext import commands, tasks
import os
import time
from itertools import cycle
import praw
import random
import aiohttp
import json
from discord.utils import get
key = os.getenv('key')

wkey = os.getenv('wkey')

client = discord.Client()

client = commands.Bot(command_prefix='p!')
client.remove_command('help')


@client.command()
@commands.has_permissions(kick_members=True)
@commands.cooldown(1, 7, commands.BucketType.user)
async def kick(ctx, user: discord.Member, *, reason):
    await user.kick(reason=reason)
    embed = discord.Embed(
        title="Kick",
        description=f'{user} kicked for {reason}',
        color=0x90c4ff)
    await ctx.send(embed=embed)


@client.command()
@commands.has_permissions(ban_members=True)
@commands.cooldown(1, 7, commands.BucketType.user)
async def ban(ctx, user: discord.Member, *, reason):
    await user.ban(reason=reason)
    embed = discord.Embed(
        title="Ban",
        description=f'{user} was struck by the ban hammer for {reason}',
        color=0x90c4ff)
    await ctx.send(embed=embed)


@client.command()
async def server(ctx):
    await ctx.send('Our Developement Server: discord.gg/KNNSf9q')

@client.command(pass_context=True)
@commands.has_permissions(kick_members=True)
async def role(ctx, user: discord.Member, role: discord.Role):
    await user.add_roles(role)
    embed = discord.Embed(title="Role Granted", description=f'{user.mention} was given {role.mention} by {ctx.author.mention}', color=0x90c4ff)
    await ctx.send(embed=embed) 


@client.command()
async def about(ctx):
    embed = discord.Embed(Title="About:", description="Hello im Praxeus, a Discord Moderation bot. > I am currently under the works and using the `p!server` command will allow you to help me!", color=0x90c4ff)

    embed.add_field(name="Version:", value="Alpha V. 0.0.1", inline=False)

    embed.add_field(name="Github", value="[Github Repository](https://github.com/coleslaw12/PraxeusBot)", inline=False)

    embed.add_field(name="Creator", value="<@345321888806862858>", inline=False)

    embed.add_field(name="Source Code Creator", value="<@738604939957239930>", inline=False)

    await ctx.send(embed=embed)

@client.command()
async def mute(ctx, member: discord.Member = None, *, reason):
    guild = ctx.guild
    if not get(ctx.guild.roles, name="Muted"):
        role_perms = discord.Permissions(send_messages=False, speak=False)
        await guild.create_role(name="Muted", permissions=role_perms)
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    await member.add_roles(muted_role, reason=reason)

    await ctx.send(
        f"{member} was muted by {ctx.message.author}\n**Reason**: {reason}.")

@client.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def purge(ctx, limit: int):
  await ctx.channel.purge(limit=limit)
  await ctx.send('Cleared by {}'.format(ctx.author.mention))
  await ctx.message.delete()

@purge.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You cant do that!")

@client.command()
async def unmute(ctx, member: discord.Member = None, *, reason):
    guild = ctx.guild
    if not get(ctx.guild.roles, name="Muted"):
        role_perms = discord.Permissions(send_messages=False, speak=False)
        await guild.create_role(name="Muted", permissions=role_perms)
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    await member.remove_roles(muted_role, reason=reason)

    embed = discord.Embed(
        title="Unmute",
        description=
        f'{member.mention} was unmuted by {ctx.author.mention} for {reason}',
        color=0x90c4ff)
    await ctx.send(embed=embed)

with open('reports.json', encoding='utf-8') as f:
    try:
        report = json.load(f)
    except ValueError:
        report = {}
        report['users'] = []

@client.command(pass_context=True)
@commands.has_permissions(kick_members=True)
async def warn(ctx, user: discord.User, *reason: str):
    if not reason:
        await ctx.send("Please provide a reason")
        return
    reason = ' '.join(reason)
    for current_user in report['users']:
        if current_user['name'] == user.name:
            current_user['reasons'].append(reason)
            break
    else:
        report['users'].append({
            'name': user.name,
            'reasons': [
                reason,
            ]
        })
    with open('reports.json', 'w+') as f:
        json.dump(report, f)

        embed = discord.Embed(
            title="Warn",
            description=f"{user.name} has been warned for {reason}",
            color=0x90c4ff)
        await ctx.send(embed=embed)

@client.command(pass_context=True)
@commands.has_permissions(kick_members=True)
async def warns(ctx, user: discord.User):
    for current_user in report['users']:
        if user.name == current_user['name']:
            await ctx.send(
                f"{user.name} has been reported {len(current_user['reasons'])} times : {','.join(current_user['reasons'])}"
            )
            embed = discord.Embed(
                title="Warnings",
                description=
                f"{user.name} has been reported {len  (current_user['reasons'])} times : {','.join(current_user['reasons'])}",
                color=0x90c4ff)
            await ctx.send(embed=embed)
            break
    else:
        await ctx.send(f"{user.name} has never been reported")

@client.command()
async def invite(ctx):
    embed = discord.Embed(
        title="Invite Me!",
        description=
        f'Add me to your server! Here: https://discord.com/api/oauth2/authorize?client_id=769003566773567519&permissions=470150342&scope=bot',
        color=0x90c4ff)
    await ctx.send(embed=embed)

@client.command()
@commands.cooldown(1, 7, commands.BucketType.user)
async def help(ctx):
    embed = discord.Embed(
        title="Help", description="Help menu", color=0x90c4ff, Inline=True)

    embed.add_field(name="Version", value="0.0.1 Alpha", inline=False)

    embed.add_field(name="Moderation", value="Displays Moderation commands. **Command:** `p!moderation` or `p!m`", inline=False)

    embed.add_field(name="Utility", value="Displays Utility Commands. **Command:** `p!utility` or `p!u`", inline=False)

    await ctx.send(embed=embed)

@client.command(aliases=["m"])
@commands.cooldown(1, 7, commands.BucketType.user)
async def moderation(ctx):
    embed = discord.Embed(
        title="Moderation Commands",
        description="The following commands are used for Moderation.", color=0x90c4ff)

    embed.add_field(name="Kick", value="Kicks a user from the server. **Command:** `p!kick`", inline=False)

    embed.add_field(name="Ban", value="Bans a user from the server. **Command:** `p!ban`", inline=False)

    embed.add_field(
        name="Mute",
        value="Mutes the user for 2 hours(This is not currently editable) **Command:** `p!mute`.", inline=False)

    embed.add_field(name="Unmute", value="Unmutes a specified user. **Command:** `p!unmute`", inline=False)

    embed.add_field(
        name="Warn", value="Warns the specified user for a specified reason. **Command:** `p!warn`", inline=False)

    embed.add_field(name="Warns", value="Shows all the warnings for a user. **Command:** `p!warns`", inline=False)

    await ctx.send(embed=embed)

@client.command(aliases=["u"])
@commands.cooldown(1, 7, commands.BucketType.user)
async def utility(ctx):
    embed = discord.Embed(
        title="Utility Commands",
        description="The following commands are used for Utility Options.", color=0x90c4ff)

    embed.add_field(name="Help", value="Displays this menu.", inline=False)

    embed.add_field(
        name="Invite",
        value="Sends the invite to the Praxeus Developement server. **Command:** `p!invite`", inline=False)

    embed.add_field(name="Role", value="Gives a specified role to a user. **Command:** `p!role`", inline=False)

    embed.add_field(name="Server", value="Gives the dev server invite. **Command:** `p!role`", inline=False)

    embed.add_field(name="About", value="Shows the about menu for the bot! **Command:** `p!role`", inline=False)

    await ctx.send(embed=embed)

@client.event
async def on_command_error(ctx, error):
    embed = discord.Embed(
        title=f'A{random.randint(0, 200)}, An ERROR has occured.',
        description=
        f'```#An error has occured, if you think this is a mistake, try `!!help or !!server to speak with our support team!``` ```Console Log: {error}```', color=0xff4040)
    await ctx.send(embed=embed)




client.run(os.getenv('TOKEN'))