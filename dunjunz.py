#!/usr/bin/env python

import sys
import Image
import UEFfile

def unscramble_data(data):

    new_data = ""
    for i in range(len(data)):
    
        new_data += chr(ord(data[i]) ^ (i % 256))
    
    return new_data


def read_bits(byte):

    bits = []
    i = 128
    while i > 0:
    
        if byte & i != 0:
            bits.append(1)
        else:
            bits.append(0)
        
        i = i >> 1
    
    return bits


class Level:

    def __init__(self, data, scrambled = True):
    
        if scrambled:
            data = unscramble_data(data)
        
        self.read_data(data)
    
    def read_data(self, data):
    
        self.lookup = {}
        
        for i in range(1, 0x20):
        
            x = ord(data[i])
            y = ord(data[0x20 + i])
            t = ord(data[0x40 + i])
            if t != 0xff:
                self.lookup[(x, y)] = t
        
        self.doors = {}
        
        for i in range(1, 21):
        
            x = ord(data[0x60 + i])
            y = ord(data[0x75 + i])
            o = ord(data[0x8a + i])
            if x != 0xff and y != 0xff and o != 0xff:
                self.doors[(x, y)] = (i, o)
        
        self.keys = {}
        
        for i in range(1, 21):
        
            x = ord(data[0xa0 + i])
            y = ord(data[0xb5 + i])
            if x != 0xff and y != 0xff:
                self.keys[(x, y)] = i
        
        self.trapdoors = set()
        
        for i in range(8):
        
            x = ord(data[0xd0 + i])
            y = ord(data[0xd8 + i])
            self.trapdoors.add((x, y))
        
        self.solid = []
        self.collectables = []
        
        for row in range(48):
        
            r = ((row/8) * 0x20) + (row % 8)
            solid_row = []
            collectables_row = []
            
            for column in range(0, 32, 8):
            
                solid_row += read_bits(ord(data[0xe0 + r + column]))
                collectables_row += read_bits(ord(data[0x1b0 + r + column]))
            
            self.solid.append(solid_row)
            self.collectables.append(collectables_row)
        
        # Read the wall tile for the level.
        self.wall_sprite = Sprite(data[-48:-24])
    
    def is_solid(self, row, column):
        return self.solid[row][column] != 0
    
    def is_collectable(self, row, column):
        return self.collectables[row][column] == 0


class Sprite:

    def __init__(self, data):
    
        self.data = self.read_sprite(data)
    
    def read_columns(self, byte):
    
        columns = []
        byte = ord(byte)
        for i in range(4):
    
            v = (byte & 0x01) | ((byte & 0x10) >> 3)
            byte = byte >> 1
            columns.append(v)
    
        columns.reverse()
        return "".join(map(chr, columns))
    
    def read_sprite(self, tile):
    
        sprite = ""
        
        i = 0
        while i < 24:
            sprite += self.read_columns(tile[i]) + self.read_columns(tile[i + 1])
            i += 2
        
        return sprite
    
    def save(self, file_name):
    
        im = Image.fromstring("P", (8, 12), self.data)
        im.putpalette((0,0,0, 255,0,0, 0,255,0, 255,255,255))
        im.save(file_name)


class Sprites:

    sprite_names = {
        0x0140: ("boots", "armour", "potion", "dagger", "weapons", "crucifix"),
        0x0e40: ("sword_up", "sword_right", "sword_down", "sword_left"),
        0x1100: ("ranger_left1", "skull0", "skull1", "skull2", "skull3", "skull4"),
        0x1910: ("drainer",),
        0x19e0: ("exit",),
        0x1a40: ("wizard_up0", "wizard_up1", "wizard_right0", "wizard_right1",
                 "wizard_down0", "wizard_down1", "wizard_left0", "wizard_left1",
                 "barbarian_up0", "barbarian_up1", "barbarian_right0", "barbarian_right1",
                 "barbarian_down0", "barbarian_down1", "barbarian_left0", "barbarian_left1",
                 "fighter_up0", "fighter_up1", "fighter_right0", "fighter_right1",
                 "fighter_down0", "fighter_down1", "fighter_left0", "fighter_left1",
                 "fireball_up", "fireball_right", "fireball_down", "fireball_left",
                 "axe_up", "axe_right", "axe_down", "axe_left",
                 "key", "treasure", "food"),
        0x2208: ("v_door",),
        0x2240: ("exp0", "exp1", "exp2", "exp3", "trapdoor"),
        0x2340: ("arrow_up", "arrow_right", "arrow_down", "arrow_left", "h_door"),
        0x2440: ("block", "ranger_up0", "ranger_up1", "ranger_right0", "ranger_right1",
                 "ranger_down0", "ranger_down1", "ranger_left0",
                 "enemy_up0", "enemy_up1", "enemy_right0", "enemy_right1",
                 "enemy_down0", "enemy_down1", "enemy_left0", "enemy_left1"),
        }
    
    def __init__(self, data):
    
        self.data = data
        self.sprites = {}
        self.read_all(data)
    
    def save(self, name, file_name):
    
        sprite = self.sprites[name]
        sprite.save(file_name)
    
    def read_all(self, data):
    
        for base, names in self.sprite_names.items():
        
            for s in range(len(names)):
            
                offset = base + (s * 48)
                sprite = Sprite(data[offset:offset + 0x18])
                self.sprites[names[s]] = sprite