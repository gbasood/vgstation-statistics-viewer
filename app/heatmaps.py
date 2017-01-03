from __future__ import division
from app import models, db
from sqlalchemy import and_
import datetime
from PIL import Image
import decimal
import numpy as np
import scipy.stats as st

#Attempts to create a 1:1 scale ghetto 2dhistogram, then shits it out as a png
#The whole thing is abominable spaghetti code the now since I've literally never used python before or programmed much, most likely left over variables all over the place

def gen_heatmap():
    xymax = 500
    heatplots = np.zeros((xymax,xymax))
            
    maxz = 0	#Highest death value for a tile, not used

    #All matches with [mapname] within last [days]
    mapmatch = models.Match.query.filter(and_(models.Match.mapname == "Box Station",models.Match.date > (datetime.datetime.now() + datetime.timedelta(-30)))).all()
    for match in mapmatch:
        #All deaths in the match, controlled by a player, not a spook and within the station z level
        for death in models.Death.query.filter(and_(models.Death.match_id == match.id, models.Death.mindkey != 'null', models.Death.mindname != 'Manifested Ghost', models.Death.death_z == 1)):
            if death.death_y > (xymax-1) or death.death_x > (xymax-1):
                logging.debug('Invalid Death')
            else:
	        heatplots[death.death_x][-(death.death_y - xymax)] += 1
                if heatplots[death.death_x][-(death.death_y - xymax)] > maxz:
                    maxz = heatplots[death.death_x][-(death.death_y - xymax)]

    nanheat = np.array(np.sort(np.ndarray.flatten(heatplots)))	#due to fuckery we convert zeros to nan in order to get mean and std
    #nanheat = nanheat[np.logical_not(np.isnan(nanheat))]
    nanheat[nanheat == 0] = np.nan

    mean = np.nanmean(nanheat)
    std = np.nanstd(nanheat)
    grd = np.gradient(nanheat)

    #percentile ranges to base colour scale on, this really needs to be made into something decent, cause it seems 1 death on a tile is in the 37th percentile, and over all it looks like dogshit
    p1=0.50
    p2=0.70
    p3 = 1

    #we create the image by making a black 500,500 image, then manually editing each pixel to have a colour based on the deaths on that tile, in theory it should be a nice heatmap-like thing
    #in theory
    img = Image.new( 'RGBA', (xymax,xymax), (0,0,0,0))
    pixels = img.load()
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            if heatplots[x][y] != 0:
                p = percentile(heatplots[x][y], mean, std)
                print p
                if p <= p1:
                    pixels[x-1,y] = find_intermediate_color(((0, 0, 1 ,1)), ((1, 1, 0, 1)), p-0.3)
                elif p <= p2:
                    pixels[x-1,y] = find_intermediate_color(((1, 1, 0, 1)), ((0.50, 0.50, 0, 1)), p/p2)
                else:
                    pixels[x-1,y] = find_intermediate_color(((1, 1, 0, 1)), ((1, 0, 0, 1)), p/p3)
    img.save("test.png", format="png")

    print mean, std, grd, maxz, nanheat, heatplots

def find_intermediate_color(lowcolor, highcolor, intermed):
    """
    Shamefully stolen from plotly.
    
    Returns the color at a given distance between two colors
    This function takes two color tuples, where each element is between 0
    and 1, along with a value 0 < intermed < 1 and returns a color that is
    intermed-percent from lowcolor to highcolor
    """
    diff_0 = float(highcolor[0] - lowcolor[0])
    diff_1 = float(highcolor[1] - lowcolor[1])
    diff_2 = float(highcolor[2] - lowcolor[2])

    colors = (lowcolor[0] + intermed * diff_0,
            lowcolor[1] + intermed * diff_1,
            lowcolor[2] + intermed * diff_2)
 
    rgb_components = []

    for component in colors:
        rounded_num = decimal.Decimal(str(component*255.0)).quantize(
            decimal.Decimal('1'), rounding=decimal.ROUND_HALF_EVEN
        )
        # convert rounded number to an integer from 'Decimal' form
        rounded_num = int(rounded_num)
        rgb_components.append(rounded_num)

    return (rgb_components[0], rgb_components[1], rgb_components[2])

def percentile(value, mean, std):
    z = (value - mean) / std
    p = st.norm.cdf(z)
    return p

