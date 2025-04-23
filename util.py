def multiline_text(scr, s, f, r):
    """
    Blits multiline text onto the screen

    Args:
        scr (screen): The screen to be blitted to.
        s (str): Multiline string.
        f (font): The font that will be used to render the text
        r (rect): The location where the text is blitted
    """
    s = s.split("\n")
    line_height = f.get_linesize()
    total_height = len(s) * line_height
    start_y = (r[1] - total_height)//2

    for i, line in enumerate(s):
        rendered = f.render(line, True, (255 ,255, 255))
        rect = rendered.get_rect(center=(r[0], start_y + i * line_height))
        scr.blit(rendered, rect)

    