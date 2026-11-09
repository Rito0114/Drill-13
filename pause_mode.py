import os
from pathlib import Path

from pico2d import *
import game_framework
import game_world


def init():
    global released_events, title_font, guide_font
    released_events = []
    font_path = str(Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts' / 'arial.ttf')
    title_font = load_font(font_path, 48)
    guide_font = load_font(font_path, 24)


def finish():
    global title_font, guide_font
    del title_font
    del guide_font


def handle_events():
    for event in get_events():
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_p:
            if not getattr(event, 'repeat', 0):
                game_framework.pop_mode()
                return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            import title_mode
            game_framework.pop_mode()
            game_framework.change_mode(title_mode)
            return
        elif event.type == SDL_KEYUP:
            released_events.append(event)


def update():
    pass


def render():
    clear_canvas()
    game_world.render()
    x, y = get_canvas_width() / 2, get_canvas_height() / 2
    title_font.draw(x - 100 + 2, y + 30 - 2, 'PAUSED', (0, 0, 0))
    title_font.draw(x - 100, y + 30, 'PAUSED', (255, 255, 255))
    guide_font.draw(x - 65 + 2, y - 20 - 2, 'P: Resume', (0, 0, 0))
    guide_font.draw(x - 65, y - 20, 'P: Resume', (255, 255, 0))
    update_canvas()
