from visiontagger.obb_utils import sort_points, calculate_obb, draw_oriented_bounding_box

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
except ImportError:
    raise ImportError(
        "Tkinter is not installed. Please install it using your package manager, e.g., 'apt install python3-tk'.")

import numpy as np
import visiontagger
from PIL import Image, ImageTk
import csv
import os
import shutil

MARKER_SIZE = 3.  # You can adjust the size


class AnnotationTool:
    def __init__(self, root):
        self.last_drawn_bounding_box = None
        self.current_click_markers = []
        self.current_bbox = None
        self.click_count = 0
        self.root = root
        self.root.title("Thermal Image Annotation Tool")
        self.root.geometry("800x600")  # Set initial size of the window
        icon_path = os.path.join(os.path.dirname(visiontagger.__file__), 'icon.png')

        icon = ImageTk.PhotoImage(file=icon_path)
        self.root.iconphoto(False, icon)

        # Initialize variables
        self.image_list = []
        self.image_sizes = {}  # Dictionary to store sizes
        self.current_image_index = 0
        self.canvas_image = None

        # Additional attribute to store the actual image dimensions on the canvas
        self.image_on_canvas = None

        self.unsaved_changes = False

        # Create a menu bar
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        # Add 'File' menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open Folder", command=self.load_images)
        file_menu.add_command(label="Save Annotations", command=self.save_annotations)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        menu_bar.add_command(label="Clear current image", command=self.clear_boxes)

        # Create a canvas for image display
        self.canvas = tk.Canvas(self.root, bg='gray')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Status Bar at the bottom
        self.status_bar = tk.Label(self.root, text="No image loaded", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Navigation Buttons
        prev_button = tk.Button(self.root, text="<< Prev", command=self.prev_image)
        prev_button.pack(side=tk.LEFT, padx=10, pady=10)

        next_button = tk.Button(self.root, text="Next >>", command=self.next_image)
        next_button.pack(side=tk.RIGHT, padx=10, pady=10)

        # Label for tips
        self.tips_label = tk.Label(self.root, text="Left Click: Draw Box | Right Click: Remove Box", fg="blue")
        self.tips_label.pack(side=tk.BOTTOM, fill=tk.X)

        # Bounding box variables
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.bounding_boxes = {}  # Dictionary to store bounding boxes for each image

        # Bind mouse events to the canvas
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

        # Bind right-click event for removing bounding boxes
        self.canvas.bind("<Button-3>", self.on_right_click)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def load_images(self):
        config_file = "folder_config.txt"
        initial_dir = None  # Default value

        try:
            # Try to read the last used folder path
            with open(config_file, "r") as file:
                initial_dir = file.readline().strip()
        except FileNotFoundError:
            pass  # No problem if the file doesn't exist yet

        # Use filedialog, prefilled with the last saved path if available
        folder_path = filedialog.askdirectory(initialdir=initial_dir)
        if not folder_path:  # If no folder is selected
            return
        try:
            with open(config_file, "w") as file:
                file.write(folder_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save folder path: {e}")
        # Clear existing data
        self.image_list = []
        self.current_image_index = 0
        self.bounding_boxes = {}
        self.canvas.delete("all")  # Clear the canvas

        # Update the status bar
        self.status_bar.config(text="No image loaded")

        # Load new images from the selected folder
        try:
            files = os.listdir(folder_path)
        except Exception as e:
            messagebox.showerror("Error", "Failed to read the folder")
            return

        # Filter and store image paths
        self.image_list = [os.path.join(folder_path, file) for file in files if
                           file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.tif'))]

        if not self.image_list:
            messagebox.showinfo("No images", "No images found in the selected folder")
            return

        self.unsaved_changes = True
        # Load the first image from the new folder
        self.load_current_image()

    def load_current_image(self):
        if self.current_image_index < 0 or self.current_image_index >= len(self.image_list):
            messagebox.showinfo("No more images", "No more images in the folder")
            return

        image_path = self.image_list[self.current_image_index]
        try:
            # Load the image using PIL
            pil_image = Image.open(image_path)

            if (pil_image.format == 'TIFF' or pil_image.format == 'TIF') and pil_image.mode == 'I;16':
                array = np.array(pil_image)
                normalized = (array.astype(np.uint16) - array.min()) * 255.0 / (array.max() - array.min())
                pil_image = Image.fromarray(normalized.astype(np.uint8))

            if pil_image.mode != "RGB":
                pil_image = pil_image.convert("RGB")
            # Store the original and display sizes
            original_image_size = pil_image.size  # (width, height)
            pil_image.thumbnail((800, 600))
            self.canvas_image = ImageTk.PhotoImage(pil_image)
            display_image_size = (self.canvas_image.width(), self.canvas_image.height())

            self.image_sizes[self.current_image_index] = {'original': original_image_size,
                                                          'display': display_image_size}

            # Clear the canvas including any existing bounding boxes
            self.canvas.delete("all")

            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.canvas_image)

            # Redraw stored bounding boxes for the current image
            if self.current_image_index in self.bounding_boxes:
                for bbox in self.bounding_boxes[self.current_image_index]:
                    self.canvas.create_rectangle(bbox[0], bbox[1], bbox[2], bbox[3], outline='red')

            # Store the dimensions of the image on the canvas
            self.image_on_canvas = (0, 0, self.canvas_image.width(), self.canvas_image.height())

            # Update the status bar
            self.status_bar.config(text=f"Image {self.current_image_index + 1} of {len(self.image_list)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load the image\n{e}")

    def clear_boxes(self):
        """Removes all bounding boxes from the current image."""

        if self.current_image_index in self.bounding_boxes:
            del self.bounding_boxes[self.current_image_index]  # Delete all boxes for the current image
        self.canvas.delete("all")  # Clear the canvas
        self.load_current_image()  # Reload the image to fully reflect the change

    def save_annotations(self):
        if not self.image_list:
            messagebox.showinfo("No Images", "No images loaded. Load a folder to save annotations.")
            return

        save_path = filedialog.askdirectory()
        if not save_path:
            return

        dataset_folder = os.path.join(save_path, "MOT_Dataset")
        images_folder = os.path.join(dataset_folder, "Images", "seq1")
        annotations_folder = os.path.join(dataset_folder, "annotations")
        os.makedirs(images_folder, exist_ok=True)
        os.makedirs(annotations_folder, exist_ok=True)

        annotation_file = os.path.join(annotations_folder, "seq1.csv")

        try:
            with open(annotation_file, 'w', newline='') as file:
                writer = csv.writer(file)
                for image_index, bboxes in self.bounding_boxes.items():
                    sizes = self.image_sizes.get(image_index)
                    if not sizes:
                        continue  # Skip if size data is missing

                    scale_x = sizes['original'][0] / sizes['display'][0]
                    scale_y = sizes['original'][1] / sizes['display'][1]

                    for bbox_id, bbox in enumerate(bboxes):
                        x_min, y_min, x_max, y_max = bbox
                        x_min, x_max = x_min * scale_x, x_max * scale_x
                        y_min, y_max = y_min * scale_y, y_max * scale_y
                        width, height = x_max - x_min, y_max - y_min

                        # Frame number, object ID, bbox coords, default values for other fields
                        writer.writerow([image_index, 0, x_min, y_min, width, height, -1, -1, -1, -1])

            # Copying images to the dataset folder
            for image_index, image_path in enumerate(self.image_list):
                target_path = os.path.join(images_folder, f"seq1_{image_index:012d}.jpg")
                shutil.copy(image_path, target_path)

            messagebox.showinfo("Success", "Annotations and images saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save annotations\n{e}")

    def next_image(self):
        if self.current_image_index < len(self.image_list) - 1:
            self.current_image_index += 1
        else:
            # Uncomment the next line to wrap around to the first image
            # self.current_image_index = 0
            messagebox.showinfo("End of List", "You have reached the end of the image list.")
            return
        self.load_current_image()

    def prev_image(self):
        if self.current_image_index > 0:
            self.current_image_index -= 1
        else:
            # Uncomment the next line to wrap around to the last image
            # self.current_image_index = len(self.image_list) - 1
            messagebox.showinfo("Start of List", "You have reached the start of the image list.")
            return
        self.load_current_image()

    def on_mouse_down(self, event):
        # Check if an image is loaded and if the click is within the image area
        if self.image_on_canvas and self.point_within_image(event.x, event.y):
            self.click_count += 1

            # Draw a marker on the click location
            self.current_click_markers.append(
                self.marker(event)
            )
        if self.click_count == 3:
            self.canvas.delete(self.last_drawn_bounding_box)
            self.process_oriented_bounding_box()

    def marker(self, event):
        x, y = event.x, event.y
        return [x, y,
                self.canvas.create_oval(x - MARKER_SIZE,
                                        y - MARKER_SIZE,
                                        x + MARKER_SIZE,
                                        y + MARKER_SIZE,
                                        fill="blue",
                                        outline="")]

    def on_mouse_drag(self, event):
        self.canvas.delete(self.current_click_markers[len(self.current_click_markers) - 1][2])
        self.current_click_markers[len(self.current_click_markers) - 1] = self.marker(event)
        if self.click_count == 3:
            self.canvas.delete(self.last_drawn_bounding_box)
            self.process_oriented_bounding_box()

    def on_mouse_up(self, event):
        if self.click_count == 3:
            coordinates = self.process_oriented_bounding_box()
            self.bounding_boxes.setdefault(self.current_image_index, []).append(
                coordinates
            )
            self.current_bbox = None
            self.last_drawn_bounding_box = None
            self.click_count = 0

            # Clear the click markers
            for x, y, marker_id in self.current_click_markers:
                self.canvas.delete(marker_id)
            self.current_click_markers = []

    def process_oriented_bounding_box(self):
        # 1. Calculate center, width, height, and angle from the three points
        coordinates = calculate_obb(self.current_click_markers[0],
                                    self.current_click_markers[1],
                                    self.current_click_markers[2])
        # 2. Draw the bounding box on the canvas
        self.last_drawn_bounding_box = draw_oriented_bounding_box(self.canvas,
                                                                  coordinates,
                                                                  color='red')

        return coordinates

    def on_right_click(self, event):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        to_remove = []

        # Check if the right-click is inside any bounding box
        if self.current_image_index in self.bounding_boxes:
            for idx, bbox in enumerate(self.bounding_boxes[self.current_image_index]):
                if bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3]:
                    to_remove.append(idx)

        # Remove the bounding boxes
        for idx in reversed(to_remove):  # Reverse to avoid index shifting issues
            del self.bounding_boxes[self.current_image_index][idx]

        # Redraw the image and bounding boxes if any were removed
        if to_remove:
            self.load_current_image()

    def point_within_image(self, x, y):
        # Check if the given point (x, y) is within the area of the image
        img_x1, img_y1, img_x2, img_y2 = self.image_on_canvas
        return img_x1 <= x <= img_x2 and img_y1 <= y <= img_y2

    def constrain_within_image(self, x, y):
        # Constrain x and y coordinates to be within the image area
        img_x1, img_y1, img_x2, img_y2 = self.image_on_canvas
        x = max(img_x1, min(x, img_x2))
        y = max(img_y1, min(y, img_y2))
        return self.canvas.canvasx(x), self.canvas.canvasy(y)

    def on_close(self):
        if self.unsaved_changes:
            if messagebox.askyesno("Exit", "You have unsaved changes. Are you sure you want to exit?"):
                self.root.destroy()
        else:
            self.root.destroy()


def main():
    root = tk.Tk()
    app = AnnotationTool(root)
    root.mainloop()


if __name__ == "__main__":
    main()
