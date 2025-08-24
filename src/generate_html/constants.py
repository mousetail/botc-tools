a4_width = 2480  # A4 width in pixels
a4_height = 3508  # A4 height in pixels
svg_width = 200  # Width of each character SVG
svg_height = 200  # Height of each character SVG
circle_radius = 80  # Radius of the circular image
font_size = 20  # Font size for the character name
description_max_width = 250
reminder_token_width = 70

horizontal_margin = 20
verrtical_margin = 20

svgs_per_page = 21

vertical_squish = 47

horizontal_space_between_tokens = 25

scale = a4_width / (
    svg_width * 4 + horizontal_space_between_tokens * 3 + 2 * horizontal_margin
)
