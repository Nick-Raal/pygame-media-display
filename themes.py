import pygame_menu

custom_theme = pygame_menu.themes.THEME_SOLARIZED.copy()
custom_theme.title_font = pygame_menu.font.FONT_FRANCHISE
custom_theme.title_font_size= 60
custom_theme.widget_background_inflate_to_selection=True
bgimage = pygame_menu.baseimage.BaseImage(
    image_path=(".\graphics\bg.svg"),
    drawing_mode=pygame_menu.baseimage.IMAGE_MODE_CENTER,
    offset=(0,0)
)
custom_theme.background_color = bgimage
#custom_theme.locals.ALIGN_CENTER
custom_theme.widget_font = pygame_menu.font.FONT_NEVIS
