# Read-Only Switcher for QGIS

![Plugin Icon](icon.png)  
_Toggle layer read-only status directly from the Layers Panel_

---

## Features

- **One-click switching** of read-only status for selected layers
- **Batch processing** of multiple layers simultaneously
- **Intelligent state detection** handles mixed read-only/editable selections
- **Visual feedback** with operation confirmation
- **No more digging** through Project Properties dialog

## Installation

### Method 1: QGIS Plugin Manager

1. Open QGIS → `Plugins` → `Manage and Install Plugins...`
2. Search for `Read-Only Switcher`
3. Click `Install Plugin`

### Method 2: Manual Installation

```bash
cd ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
git clone https://github.com/leiding06/read_only_switcher.git
```

## Usage

1. Select one or more layers in the Layers Panel
2. Click the toolbar icon:
   ![icon](icon-1.png)
3. View status confirmation dialog

## FAQ

**Q: Why don't some layers change state?**  
A: The plugin only affects vector layers. Raster and other non-vector layers are ignored.

**Q: How to report issues?**  
Please use the [issue tracker](https://github.com/leiding06/read_only_switcher/issues)

## Contributing

Pull requests are welcome! For major changes, please open an issue first.

## License

GNU GPLv2 - See [LICENSE](LICENSE) file for details.
