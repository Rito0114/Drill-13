"""실제 pico2d 캔버스에서 모드 전환과 아이템 동작을 검증한다."""
import os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pico2d as p
import game_framework as framework
import game_world
import logo_mode
import title_mode
import play_mode
import pause_mode
import item_mode
from ball import Ball


def press(mode, key, repeat=0):
    event = SimpleNamespace(type=p.SDL_KEYDOWN, key=key, repeat=repeat)
    with patch.object(mode, 'get_events', return_value=[event]):
        mode.handle_events()


def balls():
    return [obj for layer in game_world.world for obj in layer if isinstance(obj, Ball)]


def main():
    os.chdir(Path(__file__).resolve().parent)
    p.open_canvas()
    framework.running = True
    framework.stack = [logo_mode]
    try:
        logo_mode.init()
        logo_mode.render()
        with patch.object(logo_mode, 'get_time', return_value=logo_mode.logo_start_time + 2.1):
            logo_mode.update()
        assert framework.stack == [title_mode]
        press(title_mode, p.SDLK_SPACE)
        assert framework.stack == [play_mode]
        boy = play_mode.boy
        press(play_mode, p.SDLK_i)
        assert framework.stack == [play_mode, item_mode]

        press(item_mode, p.SDLK_RIGHT)
        x, frame = boy.x, boy.frame
        item_mode.update()
        assert boy.x > x and boy.frame != frame
        press(item_mode, p.SDLK_1)
        press(item_mode, p.SDLK_SPACE)
        assert balls()[-1].size == 21
        small = balls()[-1]
        small_x = small.x
        item_mode.update()
        assert small.x != small_x
        press(item_mode, p.SDLK_2)
        press(item_mode, p.SDLK_SPACE)
        assert balls()[-1].size == 41 and small.size == 21
        assert balls()[-1].image is not small.image
        assert small.image.w < balls()[-1].image.w
        with patch.object(small.image, 'draw') as draw:
            small.draw()
            draw.assert_called_once_with(small.x, small.y, 21, 21)
        with patch.object(balls()[-1].image, 'draw') as draw:
            balls()[-1].draw()
            draw.assert_called_once_with(balls()[-1].x, balls()[-1].y, 41, 41)
        press(item_mode, p.SDLK_0)
        count = len(balls())
        press(item_mode, p.SDLK_SPACE)
        assert boy.ball_size is None and len(balls()) == count
        item_mode.render()

        with patch.object(pause_mode, 'get_time', return_value=100):
            press(item_mode, p.SDLK_p)
        assert framework.stack == [play_mode, item_mode, pause_mode]
        positions = [(obj.x, obj.y) for obj in [boy, *balls()]]
        pause_mode.update()
        pause_mode.render()
        assert positions == [(obj.x, obj.y) for obj in [boy, *balls()]]
        press(pause_mode, p.SDLK_p, repeat=1)
        assert framework.stack[-1] is pause_mode
        release = SimpleNamespace(type=p.SDL_KEYUP, key=p.SDLK_RIGHT)
        with patch.object(pause_mode, 'get_events', return_value=[release]):
            pause_mode.handle_events()
        with patch.object(pause_mode, 'get_time', return_value=110):
            press(pause_mode, p.SDLK_p)
        assert framework.stack == [play_mode, item_mode]
        assert not boy.pressed_keys and boy.state == 'IDLE'
        press(item_mode, p.SDLK_i)
        assert framework.stack == [play_mode] and play_mode.boy is boy

        press(play_mode, p.SDLK_i)
        press(item_mode, p.SDLK_i, repeat=1)
        assert framework.stack == [play_mode, item_mode]
        press(item_mode, p.SDLK_ESCAPE)
        assert framework.stack == [play_mode]
        press(play_mode, p.SDLK_i)
        press(item_mode, p.SDLK_p)
        press(pause_mode, p.SDLK_ESCAPE)
        assert framework.stack == [title_mode] and not any(game_world.world)
        press(title_mode, p.SDLK_SPACE)
        assert sum(map(len, game_world.world)) == 2
        press(play_mode, p.SDLK_p)
        assert framework.stack == [play_mode, pause_mode]
        idle_started_at = play_mode.boy.idle_started_at
        with patch.object(pause_mode, 'get_time', return_value=pause_mode.pause_started_at + 10):
            press(pause_mode, p.SDLK_p)
        assert abs(play_mode.boy.idle_started_at - idle_started_at - 10) < 0.001
        press(play_mode, p.SDLK_ESCAPE)
        press(title_mode, p.SDLK_ESCAPE)
        assert not framework.running
        framework.running = True
        press(title_mode, p.SDLK_SPACE)
        press(play_mode, p.SDLK_i)
        with patch.object(item_mode, 'get_events', return_value=[SimpleNamespace(type=p.SDL_QUIT)]):
            item_mode.handle_events()
        assert not framework.running
        print('PASS: logo/title/play transitions; live item window; 0/1/2 selection; ball sizes; pause/resume; cleanup')
    finally:
        while framework.stack:
            framework.stack.pop().finish()
        p.close_canvas()


if __name__ == '__main__':
    main()
