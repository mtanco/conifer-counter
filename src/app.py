import datetime
import os

from h2o_wave import Q, app, handle_on, main, on, ui
from loguru import logger

from .tree import Trees
from .user import AppUser


@app("/")
async def serve(q: Q):
    logger.debug(q.args)

    if not q.client.initialized:
        initialize_client(q)
    else:
        await handle_on(q)

    await q.page.save()


def initialize_client(q: Q):

    if not q.user.initialized:
        initialize_user(q)  # User needs to be setup before the client can be

    logger.debug("Initializing client")

    q.client.trees = Trees()

    create_main_ui(q)  # setup the page layout
    q.client.cards = (
        []
    )  # used to hold reference to cards to delete when changing the page
    render_tree_cards(q)  # setup the home page

    q.client.theme = "light"

    q.client.initialized = True


def initialize_user(q: Q):

    if not q.app.initialized:
        initialize_app(q)  # app needs to be setup before the user can be

    logger.debug(f"Initializing {q.user}")

    # Create a user and save reference to them in tha pp
    user_id = q.auth.subject
    new_user = AppUser(
        user_id=user_id, email=q.auth.username, users_dir=q.app.users_dir
    )
    q.user.user = new_user
    q.app.users[user_id] = new_user

    q.user.initialized = True


def initialize_app(q: Q):
    logger.debug("Initializing app")

    q.app.users = {}  # reference of all users of this app
    create_app_dirs(q)  # local disk to save user data (not currently used)

    q.app.initialized = True


@on()
async def increment_tree_count(q: Q):
    common_name = q.args.increment_tree_count
    logger.debug(f"Incrementing {common_name} for {q.user.user.name}")

    client_tree = next(
        (x for x in q.client.trees.trees if x.common_name == common_name), None
    )
    client_tree.increment_count()
    q.page[common_name].items[
        1
    ].text_m.content = f"Sightings this session: {client_tree.count}"

    q.page[
        "title"
    ].title = f"Total trees this session: {q.client.trees.get_total_trees()}"


@on()
async def view_counts(q: Q):
    logger.debug("Getting latest counts")

    q.page[
        "title"
    ].title = f"Total trees this session: {q.client.trees.get_total_trees()}"

    q.page["title"].items[0].button.label = "View Leaderboard"
    q.page["title"].items[1].button.label = "Refresh Counts"

    render_tree_cards(q)


@on()
async def view_historic_counts(q: Q):
    logger.debug("Processing historic information")

    q.page["title"].items[0].button.label = "Refresh Leaderboard"
    q.page["title"].items[1].button.label = "View Counts"

    render_leaderboard(q)


@on()
async def save_counts(q: Q):
    logger.debug("Saving data and restarting app for client")
    q.client.trees.save_to_disk(
        f"{q.user.user.user_dir}/{str(datetime.datetime.now())}.pkl"
    )
    initialize_client(q)


@on()
async def change_mode(q: Q):

    if q.client.theme == "light":
        q.page["meta"].theme = "neon"
        q.page["header"].commands[0].label = "Light Mode"
        q.client.theme = "neon"

    elif q.client.theme == "neon":
        q.page["meta"].theme = "light"
        q.page["header"].commands[0].label = "Dark Mode"
        q.client.theme = "light"


def create_main_ui(q: Q):
    logger.debug("Creating page layout")

    q.page["meta"] = ui.meta_card(
        box="",
        title="Conifer Counter",
        theme="light",
        layouts=[
            ui.layout(
                breakpoint="xs",
                zones=[
                    ui.zone("header"),
                    ui.zone("title"),
                    ui.zone("body"),
                    ui.zone("footer"),
                ],
            ),
            ui.layout(
                breakpoint="m",
                zones=[
                    ui.zone("header"),
                    ui.zone("title"),
                    ui.zone(
                        "body",
                        direction=ui.ZoneDirection.COLUMN,
                        zones=[
                            ui.zone("top", direction=ui.ZoneDirection.ROW),
                            ui.zone("middle", direction=ui.ZoneDirection.ROW),
                            ui.zone("bottom", direction=ui.ZoneDirection.ROW),
                        ],
                    ),
                    ui.zone("footer"),
                ],
            ),
            ui.layout(
                breakpoint="xl",
                width="1200px",
                zones=[
                    ui.zone("header"),
                    ui.zone("title"),
                    ui.zone(
                        "body",
                        direction=ui.ZoneDirection.COLUMN,
                        zones=[
                            ui.zone("top", direction=ui.ZoneDirection.ROW),
                            ui.zone("bottom", direction=ui.ZoneDirection.ROW),
                        ],
                    ),
                    ui.zone("footer"),
                ],
            ),
        ],
    )

    q.page["header"] = ui.header_card(
        box="header",
        title="Conifer Counter",
        subtitle="Counting the trees you sees!",
        icon="Street",
        icon_color="green",
        commands=[ui.command(name="change_mode", label="Dark Mode")],
    )
    q.page["title"] = ui.section_card(
        box="title",
        title=f"Total trees this session: {q.client.trees.get_total_trees()}",
        subtitle="",
        items=[
            ui.button(name="view_historic_counts", label="View Past Sessions"),
            ui.button(name="view_counts", label="Refresh Counts"),
            ui.button(
                name="save_counts",
                label="End Session",
                tooltip="Save this session's counts and reset to 0.",
            ),
        ],
    )
    q.page["footer"] = ui.footer_card(
        box="footer",
        caption="Made with 💛️ using [Wave](https://h2oai.github.io/wave/) by [@mtanco](https://github.com/mtanco)",
    )


def render_tree_cards(q):
    logger.debug("Creating tree cards")

    for c in q.client.cards:
        del q.page[c]

    length = len(q.client.trees.trees)
    for i in range(length):

        client_tree = q.client.trees.trees[i]

        # for xl layouts should the card be on the first or second row
        if i < length / 2:
            xl_box = "top"
        else:
            xl_box = "bottom"

        # for medium layouts should the card be on the first, second, or third row
        if i < length / 3:
            m_box = "top"
        elif i < (length / 3 * 2):
            m_box = "middle"
        else:
            m_box = "bottom"

        q.page[client_tree.common_name] = ui.form_card(
            box=ui.boxes(
                ui.box("body", width="400px"),
                ui.box(m_box, width="400px"),
                ui.box(xl_box, width="400px"),
            ),
            items=[
                ui.text_xl(f"{client_tree.common_name.title()}: {client_tree.family}"),
                ui.text_m(f"Sightings this session: {client_tree.count}"),
                ui.button(
                    name="increment_tree_count",
                    label="Tree spotted!",
                    value=client_tree.common_name,
                ),
            ],
        )

        q.client.cards.append(client_tree.common_name)


def render_leaderboard(q: Q):
    logger.debug("Creating leaderboard")

    for c in q.client.cards:
        del q.page[c]

    # Create columns for our issue table.
    columns = [
        ui.table_column(name="user", label="User"),
        ui.table_column(
            name="total", label="Total Count", sortable=True, data_type="number"
        ),
    ] + [
        ui.table_column(
            name=t.common_name,
            label=t.common_name.title(),
            sortable=True,
            data_type="number",
        )
        for t in q.client.trees.trees
    ]

    rows = []
    for filename in os.listdir(q.user.user.user_dir):
        trees = Trees(file=os.path.join(q.user.user.user_dir, filename))
        rows += [
            ui.table_row(
                name="row",
                cells=[q.user.user.name, str(trees.get_total_trees())]
                + [str(t.count) for t in trees.trees],
            )
        ]

    table = ui.table(
        name="tree_table",
        columns=columns,
        rows=rows,
        downloadable=True,
    )

    q.page["leaderboard"] = ui.form_card(
        box=ui.boxes(ui.box("body"), ui.box("top"), ui.box("top")), items=[table]
    )
    q.client.cards.append("leaderboard")


def create_app_dirs(q: Q):
    logger.debug("Creating app directory")

    # A directory for all users data
    q.app.users_dir = os.path.abspath("./app-data/users")
    os.makedirs(q.app.users_dir, exist_ok=True)
