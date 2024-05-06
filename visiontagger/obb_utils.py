import math


def plus(point1, point2):
    return point1[0] + point2[0], point1[1] + point2[1]


def minus(point1, point2):
    return point1[0] - point2[0], point1[1] - point2[1]


def length(vector):
    return math.sqrt(vector[0] ** 2 + vector[1] ** 2)


def normalize(vector):
    return float(vector[0]) / float(length(vector)), float(vector[1]) / float(length(vector))


def project_point_onto_line(line_start, line_direction, point):
    # Vector from line start to the point to be projected
    point_vector = minus(point, line_start)

    # Dot product for projection
    dot_product = (point_vector[0] * line_direction[0] + point_vector[1] * line_direction[1]) / (
            line_direction[0] ** 2 + line_direction[1] ** 2)

    # Calculate the projected point coordinates
    projected_x = line_start[0] + dot_product * line_direction[0]
    projected_y = line_start[1] + dot_product * line_direction[1]

    return projected_x, projected_y


def calculate_obb(p1, p2, p3):
    # sort
    if p1[0] > p2[0]:
        start = p2
        end = p1
    else:
        start = p1
        end = p2

    direction_vector = minus(end, start)
    orthogonal = (-direction_vector[1], direction_vector[0])

    # Handle the case where the first two points are the same
    if length(orthogonal) == 0:
        return start, end, start, end

    orthogonal = normalize(orthogonal)
    projection = project_point_onto_line(start, orthogonal, p3)
    p4 = plus(end, minus(projection, start))
    return start, end, p4, projection


def sort_points(points):
    """Sorts points in clockwise order, starting from the top-left."""

    # Find the point with the minimum y-coordinate (top)
    # In case of ties, the one with the minimum x-coordinate is chosen (left)
    top_left_point = min(points, key=lambda p: (p[1], p[0]))

    # Calculate angles relative to the top-left point and sort
    def sort_key(p):
        dx, dy = p[0] - top_left_point[0], p[1] - top_left_point[1]
        angle = math.degrees(math.atan2(dy, dx))
        return angle, -dx  # Sort by angle (clockwise), and break ties by greater distance

    sorted_points = [top_left_point] + sorted(points, key=sort_key)[1:]
    return sorted_points


def draw_oriented_bounding_box(canvas, coordinates, color):
    # Draw a polygon on the canvas using the rotated points
    points_list = []
    for point in coordinates:
        points_list.append(point[0])
        points_list.append(point[1])
    return canvas.create_polygon(points_list, outline=color)
