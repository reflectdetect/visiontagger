<br />
<p align="center">
<a><img src="image/Logo-circle.png" alt="FawnRescue" width="128" height="128" title="FawnRescue"></a>
  <h3 align="center">FawnRescue</h3>
  <p align="center">
    Flight Computer Code<br />
    <p align="center">
  <a href="https://github.com/FawnRescue/dataset/blob/main/LICENSE"><img src="https://img.shields.io/github/license/FawnRescue/dataset" alt="License"></a>
  <a href="https://github.com/FawnRescue/dataset/network/members"><img src="https://img.shields.io/github/forks/FawnRescue/dataset?style=social" alt="GitHub forks"></a>
  <a href="https://github.com/FawnRescue/dataset/stargazers"><img src="https://img.shields.io/github/stars/FawnRescue/dataset?style=social" alt="GitHub stars"></a>
</p>
    <p>
    <a href="https://github.com/FawnRescue/dataset/issues">Report Bug</a>
    ·
    <a href="https://github.com/FawnRescue/dataset/issues">Request Feature</a>
    </p>
    <a href="https://fawnrescue.github.io/">Website</a>
  </p>
</p>


VisionTagger is a versatile image annotation tool designed for both thermal and normal images. It provides an intuitive interface for drawing bounding boxes around objects in images, making it ideal for various applications, from machine learning datasets preparation to general image marking tasks.

## Features

- **Support for Multiple Image Types**: Works seamlessly with both thermal and standard images.
- **Bounding Box Annotation**: Easily draw, adjust, and remove bounding boxes.
- **Dataset Export**: Export annotations in the MOT dataset format.
- **Intuitive GUI**: User-friendly interface for loading images and annotating them.
- **Batch Annotation**: Load and annotate an entire folder of images efficiently.

## Installation

To install VisionTagger, simply run:

```bash
pip install visiontagger
```
### Installing Tkinter

If you encounter a "No module named 'tkinter'" error, you may need to install Tkinter separately, especially on Linux systems. Here's how to install it:

- For Debian/Ubuntu: `sudo apt-get install python3-tk`
- For Fedora: `sudo dnf install python3-tkinter`
- For Arch Linux: `sudo pacman -S tk`

For other Linux distributions, please use the system's package manager to install the `python3-tk` package.


## Usage

After installation, you can start VisionTagger with:

```bash
visiontagger
or
python -m visiontagger
```

### Loading Images

- Use the 'Open Folder' option to load a folder containing your images.

### Annotating Images

- Click and drag on an image to create a bounding box.
- Right-click inside a bounding box to remove it.
- Navigate through images using the 'Next' and 'Prev' buttons.

### Saving Annotations

- Use the 'Save Annotations' option to save your work in the MOT dataset format.

## Contributing

Contributions to VisionTagger are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on how to submit pull requests, report bugs, or suggest enhancements.

## License

This project is licensed under the [MIT License](LICENCE) - see the LICENSE file for details.
