import os

from h2o_wave import main, app, Q, ui, on, handle_on
from loguru import logger

from .tree import Trees
from .user import AppUser


@app('/')
async def serve(q: Q):
    logger.debug(q.args)

    if not q.client.initialized:
        initialize_client(q)
    else:
        await handle_on(q)

    await q.page.save()


def initialize_client(q: Q):

    if not q.user.initialized:
        initialize_user(q)

    logger.debug('Initializing client')
    q.client.trees = Trees()

    create_main_ui(q)
    render_tree_cards(q)

    q.client.initialized = True


def initialize_user(q: Q):

    if not q.app.initialized:
        initialize_app(q)

    logger.debug(f'Initializing {q.user}')

    user_id = q.auth.subject

    # Create a new user
    new_user = AppUser(
        user_id=user_id, email=q.auth.username, users_dir=q.app.users_dir
    )

    # Set newly created user as current user
    q.user.user = new_user

    # Add user to the list of app Users
    q.app.users[user_id] = new_user

    q.user.trees = Trees()
    q.user.initialized = True


def initialize_app(q: Q):
    logger.debug('Initializing app')

    # Setup the directory structure for the app in the local file system
    q.app.users = {}
    create_app_dirs(q)

    q.app.trees = Trees()
    q.app.initialized = True


@on()
async def increment_tree_count(q: Q):
    common_name = q.args.increment_tree_count
    logger.debug(f'Incrementing {common_name}')

    client_tree = next((x for x in q.client.trees.trees if x.common_name == common_name), None)
    user_tree = next((x for x in q.user.trees.trees if x.common_name == common_name), None)
    app_tree = next((x for x in q.app.trees.trees if x.common_name == common_name), None)

    client_tree.increment_count()
    user_tree.increment_count()
    app_tree.increment_count()

    q.page[common_name].items[1].text_m.content = f'Sightings this session: {client_tree.count}'
    q.page[common_name].items[2].text_m.content = f'Total sightings by you: {user_tree.count}'
    q.page[common_name].items[3].text_m.content = f'Total sightings by all users: {app_tree.count}'

    q.page['title'].title = f'Trees you\'ve seen: {q.user.trees.get_total_trees()}'
    q.page['title'].subtitle = f'Trees we\'ve seen: {q.app.trees.get_total_trees()}'


@on()
async def refresh_counts(q: Q):
    q.page['title'].title = f'Trees you\'ve seen: {q.user.trees.get_total_trees()}'
    q.page['title'].subtitle = f'Trees we\'ve seen: {q.app.trees.get_total_trees()}'

    render_tree_cards(q)


def create_main_ui(q: Q):
    logger.debug('Creating page layout')
    q.page['meta'] = ui.meta_card(box='', title='Conifer Counter')

    q.page['meta'] = ui.meta_card(
        box='',
        title='Conifer Counter',
        layouts=[
            ui.layout(
                breakpoint='xs',
                zones=[
                    ui.zone('header'),
                    ui.zone('title'),
                    ui.zone('body'),
                    ui.zone('footer'),
                ],
            ),
            ui.layout(
                breakpoint='m',
                zones=[
                    ui.zone('header'),
                    ui.zone('title'),
                    ui.zone('body', direction=ui.ZoneDirection.COLUMN, zones=[
                        ui.zone('top', direction=ui.ZoneDirection.ROW),
                        ui.zone('middle', direction=ui.ZoneDirection.ROW),
                        ui.zone('bottom', direction=ui.ZoneDirection.ROW),
                    ]),
                    ui.zone('footer'),
                ],
            ),
            ui.layout(
                breakpoint='xl',
                width='1200px',
                zones=[
                    ui.zone('header'),
                    ui.zone('title'),
                    ui.zone('body', direction=ui.ZoneDirection.COLUMN, zones=[
                        ui.zone('top', direction=ui.ZoneDirection.ROW),
                        ui.zone('bottom', direction=ui.ZoneDirection.ROW),
                    ]),
                    ui.zone('footer'),
                ],
            ),
        ]
    )

    q.page['header'] = ui.header_card(
        box='header',
        title='Conifer Counter',
        subtitle='Counting the trees you sees!',
        icon='Street',
        icon_color='green'
    )
    q.page['title'] = ui.section_card(
        box='title',
        title=f'Trees you\'ve seen: {q.user.trees.get_total_trees()}',
        subtitle=f'Trees we\'ve all seen: {q.app.trees.get_total_trees()}',
        items=[
            ui.button(name='refresh_counts', label='Get Latest Counts')
        ]
    )
    q.page['footer'] = ui.footer_card(
        box='footer',
        caption='Made with 💛️ using [Wave](https://h2oai.github.io/wave/) by [@mtanco](https://github.com/mtanco)',
    )


def render_tree_cards(q):
    logger.debug('Creating content cards')

    length = len(q.client.trees.trees)
    for i in range(length):

        client_tree = q.client.trees.trees[i]

        if i < length/2:
            xl_box = 'top'
        else:
            xl_box = 'bottom'

        if i < length/3:
            m_box = 'top'
        elif i < (length/3 * 2):
            m_box = 'middle'
        else:
            m_box = 'bottom'

        q.page[client_tree.common_name] = ui.form_card(
            box=ui.boxes(
                ui.box('body', width='400px'),
                ui.box(m_box, width='400px'),
                ui.box(xl_box, width='400px')
            ),
            items=[
                ui.text_xl(f'{client_tree.common_name.title()}: {client_tree.family}'),
                ui.text_m(f'Sightings this session: {client_tree.count}'),
                ui.text_m(f'Total sightings by you: {q.user.trees.trees[i].count}'),
                ui.text_m(f'Total sightings by all users: {q.app.trees.trees[i].count}'),
                ui.button(name='increment_tree_count', label='Tree spotted!', value=client_tree.common_name)
            ]
        )


# TODO currently never doing anything with this
def create_app_dirs(q: Q):
    # A directory for all users data
    q.app.users_dir = os.path.abspath('./app-data/users')
    os.makedirs(q.app.users_dir, exist_ok=True)