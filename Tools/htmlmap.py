#!/usr/bin/env python

import os, sys
import UEFfile
import dunjunz

type_map = {
    0x28: "treasure",
    0x29: "food",
    0x2a: "crucifix",
    0x2b: "teleport",
    0x51: "exit",
    0x53: "drainer",
    0x5f: "boots",
    0x60: "armour",
    0x61: "potion",
    0x62: "weapons",
    0x63: "dagger"
    }

def get_image_name(level, level_number, row, column):

    if (row, column) == (11, 11):
        return "ranger_up1", "Ranger"
    elif (row, column) == (12, 11):
        return "wizard_right1", "Wizard"
    elif (row, column) == (11, 12):
        return "barbarian_down1", "Barbarian"
    elif (row, column) == (12, 12):
        return "fighter_left1", "Fighter"
    
    elif (column, row) in level.keys:
        n = level.keys[(column, row)]
        return "key", n
    
    elif (column, row) in level.trapdoors:
        return "trapdoor", "trapdoor"
    
    elif level.is_solid(row, column):
        if (column, row) in level.doors:
            n, o = level.doors[(column, row)]
            if o == 0x1d:
                return "v_door", n
            else:
                return "h_door", n
        else:
            return "%02i" % level_number, None
    
    elif level.is_collectable(row, column) and \
         (column, row) in level.lookup:
    
        name = type_map[level.lookup[(column, row)]]
        if name == "teleport":
            return name, level.teleporters.index((column, row))
        else:
            return name, None
    
    else:
        return "blank", None


if __name__ == "__main__":

    if len(sys.argv) != 4:
    
        sys.stderr.write("Usage: %s <Dunjunz UEF file> <level> <output directory>\n" % sys.argv[0])
        sys.exit(1)
    
    level_number = int(sys.argv[2])
    if not 1 <= level_number <= 25:
    
        sys.stderr.write("Please specify a level from 1 to 25.\n")
        sys.exit(1)
    
    u = UEFfile.UEFfile(sys.argv[1])
    output_dir = sys.argv[3]
    
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    
    for details in u.contents:
    
        if details["name"] == "Dunjunz":
            sprites = dunjunz.Sprites(details["data"])
        
        elif details["name"] == "Level%i" % level_number:
            break
    else:
        sys.stderr.write("Failed to find a suitable data file.\n")
        sys.exit(1)
    
    level = dunjunz.Level(details["data"])
    
    f = open(os.path.join(output_dir, "index.html"), "w")
    f.write("<html>\n<head><title>Dunjunz Level %i</title></head>\n" % level_number)
    f.write("<body>\n<h1>Dunjunz Level %i</h1>\n" % level_number)
    f.write('<table cellpadding="0" cellspacing="0">\n')
    
    for row in range(48):
    
        f.write("<tr>\n")
        
        for column in range(32):
        
            image_name, extra = get_image_name(level, level_number, row, column)
            if extra != None:
                f.write('<td><img src="%s.png" alt="%s" /></td>\n' % (image_name, extra))
            else:
                f.write('<td><img src="%s.png" /></td>\n' % image_name)
        
        f.write("</tr>\n")
    
    f.write("</table>\n<body>\n<html>\n")
    
    for name, sprite in sprites.sprites.items():
        sprite.image(size = (32, 24)).save(os.path.join(output_dir, name + ".png"))
    
    level.wall_sprite.image(size = (32, 24)).save(os.path.join(output_dir, "%02i.png" % level_number))
    
    sys.exit()