import os
from loguru import logger
import discord

from captcha_utils import CaptchaGenerator
captcha_generator = CaptchaGenerator()

bot = discord.Bot()

class VerificationView(discord.ui.View):
    """A Discord UI view containing the verification button."""

    def __init__(self):
        """Initializes the verification view with a persistent button."""
        super().__init__(timeout=None)

    @discord.ui.button(label="🤖 Start Verification", style=discord.ButtonStyle.primary, custom_id="start_verification")
    async def start_verification(self, button: discord.ui.Button, interaction: discord.Interaction):
        """Callback function triggered when the verification button is clicked.

        Args:
            button (discord.ui.Button): The button that was clicked.
            interaction (discord.Interaction): The interaction that triggered the callback.
        """
        await verify(interaction)

@bot.event
async def on_ready():
    """Event handler triggered when the bot is ready.

    Sets up the verification prompt message in the configured channel.
    """
    logger.info(f'application_id({bot.application_id}) is ready.')

    view = VerificationView()
    embed = discord.Embed(
        title="Captcha Verification",
        description=f"Click the button below to complete a captcha challenge.\n"
        "If the challenge is too difficult to read, click the button again to get a new one.",
        color=discord.Color.blurple()
    )

    guild_id = int(os.getenv("GUILD_ID", "0"))
    if guild_id == 0:
        logger.error("GUILD_ID is not set in environment variables.")
        return
        
    prompt_channel_id = int(os.getenv("PROMPT_CHANNEL_ID", "0"))
    if prompt_channel_id == 0:
        logger.error("PROMPT_CHANNEL_ID is not set in environment variables.")
        return
    
    prompt_channel = bot.get_channel(prompt_channel_id)
    if prompt_channel:
        async for message in prompt_channel.history(limit=None):
            await message.delete()
        await prompt_channel.send(embed=embed, view=view)

@bot.event
async def on_message(message: discord.Message):
    """Event handler triggered on every message.

    Deletes messages in the verification prompt channel to keep it clean.

    Args:
        message (discord.Message): The message object received.
    """
    if message.author == bot.user:
        return

    prompt_channel_id = int(os.getenv("PROMPT_CHANNEL_ID", "0"))
    if prompt_channel_id == 0:
        return
    
    if message.channel.id == prompt_channel_id:
        await message.delete()

@bot.command(name="send_verification_button", description="Send a verification button for users to start verification.")
@discord.default_permissions(administrator=True)
async def send_verification_button(ctx: discord.ApplicationContext):
    """Admin command to send the verification prompt with the button.

    Args:
        ctx (discord.ApplicationContext): The context of the command.
    """
    view = VerificationView()
    embed = discord.Embed(
        title="Captcha Verification",
        description=f"Click the button below to complete a captcha challenge.\n"
        "If the challenge is too difficult to read, click the button again to get a new one.",
        color=discord.Color.blurple()
    )\
    .set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url if ctx.guild.icon else None)

    await ctx.respond(embed=embed, view=view)

@bot.command(name="verify", description="Complete the verification process.")
async def verify(ctx: discord.ApplicationContext):
    """Starts the captcha verification process for the user.

    Args:
        ctx (discord.ApplicationContext): The context of the command or interaction.
    """
    verified_role_id = int(os.getenv("VERIFIED_ROLE_ID", "0"))
    if verified_role_id == 0:
        await ctx.respond("Verification role is not set up. Please contact the administrator.", ephemeral=True)
        return
    
    member = ctx.author if hasattr(ctx, "author") else ctx.user
    if not isinstance(member, discord.Member):
        await ctx.respond("This command can only be used in a server.", ephemeral=True)
        return

    if any(role.id == verified_role_id for role in member.roles):
        await ctx.respond("You are already verified.", ephemeral=True)
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
    """Submits and validates the user's captcha response.

    Args:
        ctx (discord.ApplicationContext): The context of the command.
        solution (str): The solution input by the user.
    """
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
    """Starts the bot using the token from the environment variables."""
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        logger.error("DISCORD_BOT_TOKEN is not set in environment variables.")
        return
    
    await bot.start(token)
