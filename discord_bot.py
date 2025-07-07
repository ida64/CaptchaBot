import os
from loguru import logger
import discord

from captcha_utils import CaptchaGenerator
captcha_generator = CaptchaGenerator()

bot = discord.Bot()

@bot.event
async def on_ready():
    logger.info(f'application_id({bot.application_id}) is ready.')

@bot.event
async def on_member_join(member: discord.Member):
    log_channel_id = int(os.getenv("LOG_CHANNEL_ID", "0"))
    if log_channel_id == 0:
        return
    
    log_channel = bot.get_channel(log_channel_id)
    if log_channel:
        await log_channel.send(
            f"{member.global_name} joined the guild.\n"
            f"Account Age: {member.created_at}\n"
        )


@bot.command(name="verify", description="Complete the verification process.")
async def verify(ctx: discord.ApplicationContext):
    verified_role_id = int(os.getenv("VERIFIED_ROLE_ID", "0"))
    if verified_role_id == 0:
        await ctx.respond("Verification role is not set up. Please contact the administrator.")
        return
    
    member = ctx.author
    if not isinstance(member, discord.Member):
        await ctx.respond("This command can only be used in a server.")
        return

    if any(role.id == verified_role_id for role in member.roles):
        await ctx.respond("You are already verified.")
        return
    
    file_name, challenge = captcha_generator.generate_captcha()

    file = discord.File(file_name, filename="captcha.png")
    embed = discord.Embed(
        title="Captcha Verification",
        description="Please solve the captcha below and submit your answer using the `/submit_captcha` command.",
        color=discord.Color.random()
    ) \
    .set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url if ctx.guild.icon else None) \
    .set_image(url="attachment://captcha.png")

    await ctx.respond(
        embed=embed,
        file=file,
        ephemeral=True
    )

    if not hasattr(bot, "captcha_challenges"):
        bot.captcha_challenges = {}
    bot.captcha_challenges[member.id] = (challenge, verified_role_id)

    log_channel_id = int(os.getenv("LOG_CHANNEL_ID", "0"))
    if log_channel_id == 0:
        return
    
    log_channel = bot.get_channel(log_channel_id)
    if log_channel:
        file = discord.File(file_name, filename="captcha.png")
        
        embed = discord.Embed(
            title="Captcha Challenge Issued",
            description=f"Captcha challenge issued to {member.mention}.",
            color=discord.Color.random()
        ) \
        .set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url if ctx.guild.icon else None)\
        .add_field(name="Challenge", value=challenge, inline=False) \
        .set_image(url="attachment://captcha.png")

        await log_channel.send(
            embed=embed,
            file=file
        )

@bot.command(name="submit_captcha", description="Submit your captcha solution.")
async def submit_captcha(ctx: discord.ApplicationContext, solution: str):
    member = ctx.author
    if not hasattr(bot, "captcha_challenges") or member.id not in bot.captcha_challenges:
        await ctx.respond("No captcha challenge found. Please use /verify first.", ephemeral=True)
        return

    challenge, verified_role_id = bot.captcha_challenges[member.id]
    if solution.strip() == challenge:
        role = ctx.guild.get_role(verified_role_id)
        if role:
            await member.add_roles(role)
            await ctx.respond(f"Verification successful! You have been given the '{role.name}' role.", ephemeral=True)
        else:
            await ctx.respond("Verification role not found. Please contact the administrator.", ephemeral=True)
        del bot.captcha_challenges[member.id]
    else:
        await ctx.respond("Incorrect captcha. Please try again.", ephemeral=True)

async def run_bot():
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        logger.error("DISCORD_BOT_TOKEN is not set in environment variables.")
        return
    
    await bot.start(token)

async def run_bot():
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        logger.error("DISCORD_BOT_TOKEN is not set in environment variables.")
        return
    
    await bot.start(token)