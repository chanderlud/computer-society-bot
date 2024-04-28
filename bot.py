import hikari
import lightbulb
from hikari.impl import MessageActionRowBuilder, TextSelectMenuBuilder

# hard coded role names / ids
OPTIONS = [
    ("Software Engineer", 1132167815323979787),
    ("Data Engineer", 1132168209378852915),
    ("Cybersecurity", 1132167470548008970),
    ("STEM", 1174943163002130502),
    ("Network Engineer", 1132168482650341507)
]
BOT_CHANNEL = 1174945756034117652
TOKEN = ""

# initialize bot
bot = lightbulb.BotApp(token=TOKEN)


# the main roles command
@bot.command()
@lightbulb.command("roles", "Assign yourself the roles you want")
@lightbulb.implements(lightbulb.SlashCommand)
async def roles(ctx: lightbulb.Context) -> None:
    action_row = MessageActionRowBuilder()  # need an action row to hold the select

    # the role selector menu
    role_menu = TextSelectMenuBuilder(
        custom_id="role_select",
        parent=action_row,
        min_values=1,  # must select at least 1 role
        max_values=len(OPTIONS)  # let the user select all roles if they want
    )

    # populate the menu with roles
    for (role, role_id) in OPTIONS:
        role_menu.add_option(role, role_id)

    action_row.add_component(role_menu)  # add the menu to the row

    await ctx.respond(component=action_row)  # send it


# this is the callback which handles interactions with the menu
@bot.listen(hikari.InteractionCreateEvent)
async def on_select_menu_interaction(event: hikari.InteractionCreateEvent) -> None:
    # make sure it's the right kind of interaction
    if isinstance(event.interaction, hikari.ComponentInteraction):
        # check which menu the interaction is for
        if event.interaction.custom_id == "role_select":
            try:
                guild = event.interaction.get_guild()  # get the guild
                member = guild.get_member(event.interaction.user)  # try to fetch the member from cache

                # if the member is not cached fetch from api
                if member is None:
                    member = await bot.rest.fetch_member(event.interaction.guild_id, event.interaction.user.id)

                # add each selected role to the user
                for role_id in event.interaction.values:
                    role = guild.get_role(int(role_id))
                    await member.add_role(role, reason="user selected role")

                # let the user know it was successful
                await event.interaction.create_initial_response(
                    hikari.ResponseType.MESSAGE_UPDATE,  # edit the original response
                    content="Successfully added your roles!",
                    component=None  # remove the original menu to prevent double submission
                )
            except Exception as ex:
                # just in case something goes wrong
                await event.interaction.create_initial_response(
                    hikari.ResponseType.MESSAGE_UPDATE,
                    content=f"Uh oh! Something went wrong: {ex}",
                    component=None,
                )


# handles member join events
# why is it a member create event?
# idk
@bot.listen(hikari.MemberCreateEvent)
async def on_user_join(event: hikari.MemberCreateEvent):
    welcome_message = (f"{event.user.mention} Welcome to the server! Please pick your"
                       f" roles in this channel by using /roles")

    try:
        await bot.rest.create_message(BOT_CHANNEL, content=welcome_message)
    except Exception as ex:
        print(f"Error sending welcome message: {ex}")


bot.run()
