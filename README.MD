This project simulates the development and dynamics of kidney blood vessels using a **Cellular Automaton** written in **Python** with **Tkinter** and **Pillow**. It models arteries, vessels, aneurysms, glomeruli, dead cells, and their behaviors in a histological grid.

---

## 🎯 Purpose

- To simulate kidney vascular tissue behavior and response to pathophysiological conditions like aneurysms or isolation.
- To process histological grayscale images and classify them into meaningful biological structures.
- To study vascular propagation and vessel repair patterns interactively.

---

## 🧪 Simulation Rules

| Cell Type        | Code | Color                        | Behavior                                                                                                                                   |
|------------------|------|------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| **Artery**       | `A`  | Red                          | Constantly generates vessels in **cardinal directions** (↑ ↓ ← →). Always maintains adjacent vessels.                                      |
| **Vessel**       | `V`  | Blue (intensity based on neighbors) | Propagates to empty adjacent cells with probability `PROPAGATION_CHANCE`.<br>Dies if **isolated**.<br>Becomes **aneurysm** if ≥ `ANEURYSM_THRESHOLD` vessel/artery neighbors. |
| **Aneurysm**     | `X`  | Orange                       | Explodes if ≥ `ANEURYSM_EXPLODE_NEIGHBORS` aneurysm neighbors (cardinal).<br>Destroys nearby vessels within `EXPLOSION_RADIUS`.<br>Cures if surrounded by < `ANEURYSM_CURE_NEIGHBORS` vessels. |
| **Dead Cell**    | `D`  | Black                        | Revives into vessel if ≥ `REVIVE_DEAD_NEIGHBORS` vessel/artery neighbors.                                                                 |
| **Empty**        | `T`  | White                        | Can be converted into vessels by arteries or through propagation.                                                                         |
| **Glomerulus**   | `G`  | Green                        | Static biological filters. Marked as `G` when well vascularized.<br>Becomes `GF` (failing) if poorly irrigated (low vessel/artery support). |
| **Glomerulus (Failing)** | `GF` | Olive                     | Degrades from `G` if lacking support from nearby vessels or arteries.                                                                    |

---

## 🧠 Color Behavior

- **Vessels** (`V`) get **darker blue** when surrounded by more vessels or arteries (8 directions), and become lighter as they're isolated.
- **Aneurysms** are marked with a **bright orange**.
- **Glomeruli** are **green** when functional, and **olive** (`GF`) when not sufficiently irrigated.

---

## 🖼️ Image Integration

- You can **load grayscale kidney histology images** and convert them into grid states.
- Image pixels are classified by intensity:
  
  | Intensity Range | Cell Type |
  |------------------|------------|
  | < 90             | `A` Artery |
  | 90–129           | `V` Vessel |
  | 130–139          | `G` Glomerulus |
  | ≥ 140            | `T` Empty |

- Processed images are resized to `GRID_SIZE x GRID_SIZE` and visualized on the canvas.

---

## 🛠️ Global Parameters

You can adjust these in the Python code to change simulation sensitivity:

```python
PROPAGATION_CHANCE = 0.3          # Vessel spread probability
ANEURYSM_THRESHOLD = 5            # Neighbors to trigger aneurysm
ANEURYSM_EXPLODE_NEIGHBORS = 2    # Aneurysm neighbors needed to explode
ANEURYSM_CURE_NEIGHBORS = 4       # Vessels needed to heal an aneurysm
REVIVE_DEAD_NEIGHBORS = 1         # Neighbors needed to revive a dead cell
EXPLOSION_RADIUS = 2              # Radius affected by aneurysm explosion
```

---

## 🖱️ How to Use

1. When you launch the simulation, an empty grid will appear.
2. Use the buttons to select a cell type:
   - Artery (A)
   - Vessel (V)
   - Aneurysm (X)
   - Dead (D)
   - Empty (T)
   - Hypoxia (H)
3. Alternatively, you can upload a histological image of a kidney for better analysis, located in [images_to_use](./Workshop_3_Simulation/data/images_to_use/)
4. Click on the grid to place cells.
5. Click **Start Simulation** to begin.
6. Use **Step** to advance the simulation manually.
7. Click **Save CSV Result** to save your simulation data in a .csv file.  
8. Click **Reset** to clear the board and start over.

---

## 📦 Requirements

- contourpy       1.3.2
- cycler          0.12.1
- matplotlib      3.10.3
- numpy           2.3.1
- pillow          11.2.1
- pip             23.2.1
- pyparsing       3.2.3
- Tkinter  (pre-installed with Python)
