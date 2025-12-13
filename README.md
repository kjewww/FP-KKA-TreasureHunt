# Treasure-Hunt
## Overview
This project is a 2D game built using Python, specifically utilizing the Pygame library. 
The game runs on a 30×30 pixel tilemap grid, with a map size of 23 rows × 21 
columns. The main objectives of the game are:
- The player must search for a key 
- After obtaining the key, a treasure appears 
- The player must reach the treasure while avoiding the enemy 
- The enemy uses BFS pathfinding to chase the player when within a detection range
## Features 
1. Player Movement
   - Smooth pixel-based movement
   - Collision detection against walls
2. Dynamic Key & Treasure
   - Key spawns at a random position
   - Treasure spawns at a random position once the key is collected
3. Enemy AI with BFS Pathfinding
   - Enemy spawns at a random position
   - If the player enters the enemy’s detection range, the enemy begins chasing
   - Pathfinding uses the Breadth-First Search (BFS) algorithm
4. Game State
   - **Win condition:** Player reaches the treasure after obtaining the key
   - **Lose condition:** Enemy collides with the player
