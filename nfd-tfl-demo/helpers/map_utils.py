"""
Utility functions to convert latitude and longitude to screen X and Y coordinates
"""
import math

# (x, y, lat, long) for two reference points defining an area covering the London
# tube map.
p0 = (0, 0, 51.6880, -0.5754)
p1 = (15000, 13000, 51.37601, 0.24967)

# Earth radius in KM
radius = 6372


def lat_long_to_global_x_y(lat, lng):
    """
    Converts lat and lng coordinates to GLOBAL X and Y positions
    """
    x = radius * lng * math.cos((p0[2] + p1[2])/2)
    y = radius * lat
    return int(x), int(y)


# Calculate global x and y for the two reference points. Doing it here since this
# is a one-off operation and we can reuse these values for each point we later want
# to place on screen
p0_gx, p0_gy = lat_long_to_global_x_y(p0[2], p0[3])
p1_gx, p1_gy = lat_long_to_global_x_y(p1[2], p1[3])


def lat_long_to_screen_x_y(lat, lng):
    """
    Converts lat and lng coordinates to SCREEN X and Y positions
    """
    # now calculate x and y for the current point
    gx, gy = lat_long_to_global_x_y(lat, lng)

    # percentage of global X position in relation to total global width/height
    per_x = (gx - p0_gx) / (p1_gx - p0_gx)
    per_y = (gy - p0_gy) / (p1_gy - p0_gy)

    # screen position based on reference points
    scr_x = p0[0] + (p1[0] - p0[0]) * per_x
    scr_y = p0[1] + (p1[1] - p0[1]) * per_y
    return int(scr_x), int(scr_y)



