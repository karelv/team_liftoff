import pygame
from pygame.locals import *
from random import randint
from gameobjects.vector2 import Vector2
from config import ANT_COUNT, SCREEN_SIZE, NEST_POSITION, NEST_SIZE
import random
from config import SCREEN_SIZE, SPIDER_HEALTH
from random import randint
from gameobjects.vector2 import Vector2
from state import StateMachine, AntStateExploring, AntStateSeeking, AntStateDelivering, AntStateHunting
import time

count = 0
ant_count = 1

class SimulationEntity(object):
    """
    The Base Class for the simulation Entity.
    """

    def __init__(self, world, name, image):
        """
        Constructor of the SimulationEntity instance.

        :param world: The world which the entity belongs
        :param name: Name of the entity
        :param image: Sprite of the entity
        """

        #global count
        self.world = world
        self.name = name
        self.image = image
        self.location = Vector2(0, 0)
        self.destination = Vector2(0, 0)
        self.speed = 0.
        self.id = 0
        self.brain = StateMachine()

    def render(self, surface):
        """
        Draw the entity.

        :param surface: pygame surface object
        """
        x, y = self.location
        w, h = self.image.get_size()
        surface.blit(self.image, (x - w / 2, y - h / 2))

    def process(self, time_passed):
        """
        Process the entity data.

        :param time_passed: Time passed since the last render
        """
        self.brain.think()

        if self.speed > 0. and self.location != self.destination:
            vec_to_destination = self.destination - self.location
            distance_to_destination = vec_to_destination.get_length()
            heading = vec_to_destination.get_normalized()
            travel_distance = min(distance_to_destination, time_passed * self.speed)
            self.location += travel_distance * heading


class Ant(SimulationEntity):
    """
    The Ant Entity Class
    """
    def __init__(self, world, image):
        """
        Constructor of the Ant instance.

        :param world: The world which the entity belongs
        :param image: Sprite of the Ant
        """
        SimulationEntity.__init__(self, world, "ant", image)

        exploring_state = AntStateExploring(self)
        seeking_state = AntStateSeeking(self)
        delivering_state = AntStateDelivering(self)
        hunting_state = AntStateHunting(self)

        self.brain.add_state(exploring_state)
        self.brain.add_state(seeking_state)
        self.brain.add_state(delivering_state)
        self.brain.add_state(hunting_state)
        self.carry_image = None
        self.health = SPIDER_HEALTH

    def carry(self, image):
        global count
        """
        Set carry image.

        :param image: the carry image
        """
        count -= 1
        self.carry_image = image
        if self.health > 0:
            self.health -= 0.2


    def drop(self, surface):
        if self.carry_image:
            x, y = self.location
            w, h = self.carry_image.get_size()
            surface.blit(self.carry_image, (x - w, y - h / 2))
            self.carry_image = None
    
    def render(self, surface):
        """
        Draw the ant.

        :param surface: pygame surface object
        """

        SimulationEntity.render(self, surface)

        if self.carry_image:
            x, y = self.location
            w, h = self.carry_image.get_size()
            surface.blit(self.carry_image, (x - w, y - h / 2))
            if self.health <= 40: 
                self.health += 0.4
        if self.health > 0:
            self.health -= 0.1

        # Draw a health bar
        x, y = self.location
        w, h = self.image.get_size()
        bar_x = x - 12
        bar_y = y + h / 2
        surface.fill((255, 0, 0), (bar_x, bar_y, 25, 4))
        surface.fill((0, 255, 0), (bar_x, bar_y, self.health, 4))


class Leaf(SimulationEntity):
    """
    The Leaf Entity Class
    """

    def __init__(self, world, image):
        """
        Constructor of the Leaf instance.

        :param world: The world which the entity belongs
        :param image: Sprite of the Leaf
        """
        SimulationEntity.__init__(self, world, "leaf", image)


class Spider(SimulationEntity):
    """
    The Spider Entity Class
    """

    def __init__(self, world, image, dead_image):
        """
        Constructor of the Spider instance.

        :param world: The world which the entity belongs
        :param image: Sprite of the default spider
        :param dead_image: Sprite of the dead spider
        """

        SimulationEntity.__init__(self, world, "spider", image)
        self.dead_image = dead_image
        self.health = SPIDER_HEALTH
        self.speed = 50. + randint(-20, 20)

    def bitten(self):
        """
        Execute when spider has been bitten.
        """

        self.health -= 1
        if self.health <= 0:
            self.speed = 0.
            self.image = self.dead_image
        self.speed = 140.

    def render(self, surface):
        """
        Draw the spider.

        :param surface: pygame surface object
        """

        SimulationEntity.render(self, surface)

        # Draw a health bar
        x, y = self.location
        w, h = self.image.get_size()
        bar_x = x - 12
        bar_y = y + h / 2
        surface.fill((255, 0, 0), (bar_x, bar_y, 25, 4))
        surface.fill((0, 255, 0), (bar_x, bar_y, self.health, 4))

    def process(self, time_passed):
        """
        Process the spider data.

        :param time_passed: Time passed since the last render
        """

        x, y = self.location
        if x > SCREEN_SIZE[0] + 2:
            self.world.remove_entity(self)
            return

        SimulationEntity.process(self, time_passed)


class World(object):
    """
    The World class that the simulation entities live in.
    It contain the nest, represented by a circle in the center of the screen, and a number of Ants, Spiders and Leafs
    entities.
    """
    
    def __init__(self):
        
        self.entities = {}
        self.entity_id = 0
        # Draw the nest (a circle) on the background
        self.background = pygame.surface.Surface(SCREEN_SIZE).convert()
        self.background.fill((255, 255, 255))
        pygame.draw.circle(self.background, (200, 222, 187), NEST_POSITION, int(NEST_SIZE))
        
    def add_entity(self, entity):
        """
        Stores the entity then advances the current id.

        :param entity: The entity instance to be added
        :return:
        """
        
        self.entities[self.entity_id] = entity
        entity.id = self.entity_id
        self.entity_id += 1
        print self.entity_id
        
    def remove_entity(self, entity):
        """
        Remove the entity from the world.

        :param entity: The entity instance to be removed
        :return:
        """
        
        del self.entities[entity.id]
                
    def get(self, entity_id):
        """
        Find the entity, given its id (or None if it is not found).

        :param entity_id: The ID of the entity
        :return:
        """
        
        if entity_id in self.entities:
            return self.entities[entity_id]
        else:
            return None
        
    def process(self, time_passed):
        """
        Process every entity in the world.

        :param time_passed: Time passed since the last render
        """
                
        time_passed_seconds = time_passed / 1000.0        
        for entity in self.entities.values():
            entity.process(time_passed_seconds)

    def render(self, surface):
        """
        Draw the background and all the entities.

        :param surface: The pygame surface
        """
        
        surface.blit(self.background, (0, 0))
        for entity in self.entities.itervalues():
            entity.render(surface)
            
    def get_close_entity(self, name, location, distance_range=100.):
        """
        Find an entity within range of a location.

        :param name: Name of the entity
        :param location: location
        :param distance_range: The circular distance of the range (circular "field of view")
        """
        
        location = Vector2(*location)        
        
        for entity in self.entities.itervalues():            
            if entity.name == name:                
                distance = location.get_distance_to(entity.location)
                if distance < distance_range:
                    return entity        
        return None

count = 0

def run():
    global count, ant_count
    start_time = time.time() 
    
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE, 0, 32)

    pygame.display.set_caption('TU Simulation')
        
    world = World()
    
    w, h = SCREEN_SIZE
    
    clock = pygame.time.Clock()
    
    ant_image = pygame.image.load("ant.png").convert_alpha()
    leaf1_image = pygame.image.load("leaf.png").convert_alpha()
    leaf2_image = pygame.image.load("leaf2.png").convert_alpha()
    leaf3_image = pygame.image.load("leaf3.png").convert_alpha()
    spider_image = pygame.image.load("spider.png").convert_alpha()

    
    for ant_no in xrange(ANT_COUNT):
        
        ant = Ant(world, ant_image)
        ant.location = Vector2(randint(0, w), randint(0, h))
        ant.brain.set_state("exploring")
        world.add_entity(ant)
    
    full_screen = False
    while True: 
        for event in pygame.event.get():
            if event.type == QUIT:
                return        
        if event.type == KEYDOWN:
            if event.key == K_f:
                full_screen = not full_screen
                if full_screen:
                    screen = pygame.display.set_mode(SCREEN_SIZE, FULLSCREEN, 32)
                else:
                    screen = pygame.display.set_mode(SCREEN_SIZE, 0, 32)
        
        time_passed = clock.tick(30)
        total_waiting = round((time.time() - start_time),0) * count
        print  total_waiting, count, ant_count

        if total_waiting > 100:
            ant_count += 1
            ant = Ant(world, ant_image)
            ant.location = Vector2(randint(0, w), randint(0, h))
            ant.brain.set_state("exploring")
            world.add_entity(ant)

        if randint(1, 100) == 1:
            leaf_image = random.choice([leaf1_image, leaf2_image, leaf3_image])
            leaf = Leaf(world, leaf_image)
            leaf.location = Vector2(randint(0, w), randint(0, h))
            world.add_entity(leaf)
            count +=1
            
        if randint(1, 100) == 1:
            # Make a 'dead' spider image by turning it upside down
            spider = Spider(world, spider_image, None)
            spider.location = Vector2(-50, randint(0, h))
            spider.destination = Vector2(w+50, randint(0, h))            
            world.add_entity(spider)

        world.process(time_passed)
        world.render(screen)
        


        pygame.display.update()


if __name__ == "__main__":    
    run()

