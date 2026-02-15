def simplified_visualize_fire(forest_map, canvas) -> None:
    """
    Visualizes whole map. Only used at begin of Post-Processing and if the "first step" or "last step" button is pressed.
    """
    #Calculating cell width and height for translating indices to pixel position on Canvas
    canvas_width = canvas.winfo_reqwidth()
    canvas_height = canvas.winfo_reqheight()
    number_of_nodes_width = len(forest_map)
    number_of_nodes_height = len(forest_map[0])
    cell_width = canvas_width / number_of_nodes_width
    cell_height = canvas_height / number_of_nodes_height
    """
    Draw each Cell in forest_map on the canvas.
    The color of the rectangle is determined by fill=forest_map[i,j]. Each element of forest_map is a String which indicates the color of the cell.
    """
    for i in range(len(forest_map)):
        for j in range(len(forest_map[0])):
            canvas.create_rectangle(i * cell_width, j * cell_height, (i+1) * cell_width, (j+1) * cell_height, fill=forest_map[i,j])

def render_optimised_forward(map,canvas,cell_width,cell_height):
    """
    Visualizes only changed cells. Used in Autoplay button and if the "step forward" button is pressed.
    """
    for i in range(len(map)):
            canvas.create_rectangle(map[i].y * cell_width, map[i].x * cell_height, (map[i].y+1) * cell_width, (map[i].x+1) * cell_height, fill=map[i].color)

def render_optimised_backward(map,canvas,cell_width,cell_height):
    """
    Visualizes only changed cells. Used if "step backwards" button is pressed.
    """
    for i in range(len(map)):
            canvas.create_rectangle(map[i].y * cell_width, map[i].x * cell_height, (map[i].y+1) * cell_width, (map[i].x+1) * cell_height, fill=map[i].old_color)