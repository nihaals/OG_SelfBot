import discord
from discord.ext import commands
import time
import asyncio
import unicodedata
import cogs.emojis as Emojis
import inflect
import upsidedown

class Fun():
    def __init__(self, bot):
        self.bot = bot

    def texttoemoji(self, text: str = None):
        if not text:
            return
        text = text.lower()
        msg = ""
        p = inflect.engine()
        chars = list(text)

        for char in chars:
            Int = char.isdigit()

            if Int:
                msg += f":{p.number_to_words(int(char))}: "
            else:
                msg += f":regional_indicator_{char}: "
                # " ".join(["   " if x==" " else ":regional_indicator_{}:".format(x) for x in "hm hm"])

        return msg

    def upsidedown(self, text: str):
        return upsidedown.transform(text)

    @commands.command()
    async def ping(self, ctx):
        before = time.monotonic()
        await (await self.bot.ws.ping())
        after = time.monotonic()
        pingT = (after - before) * 1000

        await ctx.message.edit(content="Ping. :ping_pong:")
        await ctx.send(content="Pong. :ping_pong: **{0:.0f}ms**".format(pingT))

    @commands.command()
    async def status(self, ctx, *, status: str):
        status = status.strip("`")
        await self.bot.change_presence(game=discord.Game(name=status))
        await asyncio.sleep(1)
        await ctx.message.edit(content=f"**Playing** {ctx.guild.me.game}")

    @commands.command()
    async def stat_test(self, ctx):
        await self.bot.change_presence(game=None)
        await ctx.message.edit(content="Playing set to None")

    @commands.command()
    async def charinfo(self, ctx, *, characters: str):

        if len(characters) > 15:
            await ctx.send(self.bot.blank + f"Too many characters ({len(characters)}/15)")
            return

        fmt = "`\\U{0:>08}`: {1} - {2} \N{EM DASH} <http://www.fileformat.info/info/unicode/char/{0}>"

        def to_string(c):
            digit = format(ord(c), "x")
            name = unicodedata.name(c, "Name not found.")
            return fmt.format(digit, name, c)

        await ctx.message.edit("\n".join(map(to_string, characters)))

    @commands.command(aliases=["ustatus"])
    async def cstatus(self, ctx, id=None):
        if not id: await ctx.message.edit(content="Type the ID!"); return
        try: id = int(id)
        except: await ctx.message.edit(content="Type the ID!"); return
        member = discord.utils.get(self.bot.get_all_members(), id=id)
        if not member:
            await ctx.message.edit(content=f"Can't find a user with the ID of {id}")
            return
        await ctx.message.edit(content=f"{str(member)}'s status is: {str(member.status).title()}")

    @commands.command()
    async def profile(self, ctx, *, arg = None):
        if not arg: arg = str(ctx.author)

        Int = arg.isdigit()

        if Int:
            id = int(arg)
            member = discord.utils.get(ctx.guild.members, id=id)

            if not member:
                await ctx.message.edit(content=f"Could not find the user with the ID of `{arg}` "
                                               f"on the server `{ctx.guild.name}`")
                return
        elif not Int:
            # await ctx.send(self.bot.blank + "{0}, {1}".format(arg.split("#")[0], int(arg.split("#")[1])))
            member = discord.utils.get(ctx.guild.members, name = arg.split("#")[0], discriminator = arg.split("#")[1])

            if not member:
                await ctx.message.edit(content=f"Could not find the user `{arg.split('#')[0]}` "
                                               f"on the server `{ctx.guild.name}`")
                return
            id = member.id
        else:
            await ctx.send(self.bot.blank + "Type check not working or float given.")
            return

        embed = discord.Embed(description=f"Profile for {str(member)}", colour=member.colour)
        embed.add_field(name="Profile Link", value=f"<@{id}>")
        await ctx.message.edit(content="", embed=embed)

    @commands.command(aliases=["emojis", "emote", "emotes"])
    async def emoji(self, ctx, emoji: str = None, edit = True):
        if not emoji:
            allEmojis = "`"+"`, `".join(Emojis.emojis.keys())+"`"
            await ctx.message.edit(content=f"All available emotes are: {allEmojis}")
            return
        if not emoji.lower() in Emojis.emojis:
            await ctx.message.edit(content=f"Can't find the emoji `{emoji}`.")
            return
        emoji = emoji.lower()
        final = Emojis.emojis[emoji]
        if edit:
            await ctx.message.edit(content=final)
        else:
            await ctx.send(final)

    @commands.command()
    async def channels(self, ctx):
        channels = []
        for channel in ctx.guild.text_channels:
            channels.append(channel.name.title())
        await ctx.message.edit(content=self.bot.blank + f"All text channels on the server {ctx.guild.name}: `" + "`, `".join(channels) + "`")

    @commands.command()
    async def roles(self, ctx):
        roles = []
        for role in ctx.guild.roles:
            roles.append(role.name)
        await ctx.message.edit(content=self.bot.blank + f"All roles on the server `{ctx.guild.name}`: " + "`" + "`, `".join(roles)+"`")

    @commands.command()
    async def emojitext(self, ctx, *, text: str = None):

        msg = self.texttoemoji(text)

        if not msg:
            await ctx.send(self.bot.blank + "No Text!")
            return

        await ctx.message.edit(content=msg)

    @commands.command(enabled=False)
    async def react(self, ctx, channel: discord.TextChannel = None, id: int = None, *, text: str = None):
        if not channel:
            await ctx.send(self.bot.blank + "No Channel")
            return
        if not id:
            await ctx.send(self.bot.blank + "No Message ID")
            return
        if not text:
            await ctx.send(self.bot.blank + "Text?")

        message = channel.get_message(id)

        msg = self.texttoemoji(text)
        if not msg:
            await ctx.send(self.bot.blank + "No `msg` var")

        return

    @commands.command(name="upsidedown")
    async def _upsidedown(self, ctx, *, text: str):
        await ctx.send(self.upsidedown(text))

    @commands.command()
    async def quick(self, ctx, *, message = None):
        if not message: return
        message = message.strip("`")
        if "@" in message:
            pass
        msg = await ctx.send(message)
        await ctx.message.delete()
        await msg.delete()

    @commands.command()
    async def quick_mention(self, ctx, id = None):
        if not id or not id.isdigit():
            return
        id = int(id)
        user = self.bot.get_user(id)
        if not user:
            await ctx.message.edit(content="Can't find that user")
            return
        msg = await ctx.send(user.mention)
        await ctx.message.delete()
        await msg.delete()

    @commands.command(aliases=["picture", "photo"])
    async def pic(self, ctx, *, url):
        embed = discord.Embed(title="Picture", url=url)
        embed.set_image(url=url)

        try: await ctx.message.edit(content="", embed=embed)
        except: await ctx.send("Can't find that link.")

def setup(bot):
    bot.add_cog(Fun(bot))

# import discord
# user = discord.utils.get(ctx.guild.members, id=80088516616269824)
# if not user:
#     await ctx.send(self.bot.blank + f"Can't find a user with the ID of {id}")
#     return
# await ctx.send(self.bot.blank + f"{str(user)}'s status is: {str(user.status).title()}")

# blacklist = [
#     "bots",
#     "orangutan",
#     "role troll",
#     "v alliance leader",
#     "itrust",
#     "moderator",
#     "server admin"
# ]
# roles = []
# for role in ctx.guild.roles:
#     if role.hoist and role.name.lower() not in blacklist:
#         roles.append(role.name)
#
# rolesS = "\n".join(roles)
# await ctx.send(f"```{rolesS}```")
#
# for member in ctx.guild.members:
#     for role in member.roles:
#         if role.name in roles:
#             await member.add_roles(discord.utils.get(ctx.guild.roles, name = "Clan Member"))
#
# await ctx.send("Done")
#
# counter = 0
# for server in bot.guilds:
#     try:
#         await server.default_channel("Just to remind you, we have a Discord server: https://discord.gg/duRB6Qg")
#     except discord.Forbidden:
#         counter += 1
# await ctx.send(f"Done. Failed {counter} times.")
#
# for server in bot.guilds:
#     try:
#         async for message in server.default_channel.history(limit=200):
#                 if "Just to remind you, we have a Discord server" in message.content and message.id != ctx.message.id and ctx.author.id == 150750980097441792:
#                     try: await message.delete()
#                     except: continue
#     except:
#         continue