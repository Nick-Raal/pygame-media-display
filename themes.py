import pygame_menu
import pygame_menu.widgets

custom_theme = pygame_menu.themes.THEME_SOLARIZED.copy()
custom_theme.title_font = pygame_menu.font.FONT_NEVIS
custom_theme.title_font_size= 60
custom_theme.title_font_color=(255, 255, 255)
custom_theme.title_bar_style=pygame_menu.widgets.MENUBAR_STYLE_NONE
custom_theme.widget_selection_color=pygame_menu.widgets.NoneSelection
#custom_theme.widget_background_inflate_to_selection=True
bgimage = pygame_menu.baseimage.BaseImage(
    image_path="./graphics/bg.svg",
    drawing_mode=pygame_menu.baseimage.IMAGE_MODE_FILL
)
custom_theme.background_color = bgimage
#custom_theme.locals.ALIGN_CENTER
custom_theme.widget_font = pygame_menu.font.FONT_NEVIS
custom_theme.widget_font_color =(240, 240, 240)