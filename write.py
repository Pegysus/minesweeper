import pygame

def write(screen, text, text_col, filename, font_size, x, y,
          antialias=True, centered=True, rotation=0):
    """
    Writes text at (x, y) with font 'filename' (None if no filename),
    font size 'font_size',
    and with color text_col
    """
    font = pygame.font.Font(filename, font_size)
    fontBitmap = font.render(text, antialias, text_col)
    fontBitmap = pygame.transform.rotate(fontBitmap, rotation)
    if centered:
        screen.blit(fontBitmap,
                    [x-(fontBitmap.get_width()/2),
                     y-(fontBitmap.get_height()/2)])
    else:
        screen.blit(fontBitmap,
                    [x, y])

    pygame.event.pump()
    return fontBitmap
