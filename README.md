# f-esri

Ubuntu base Docker image with GDAL compiled with ESRI FileGDB write support <strike>and Oracle (OCI)</strike>
driver support.

This is a fork of https://github.com/dbca-wa/gdal-grande which is based on https://github.com/haies/gdal

Ubuntu version: 20.04 (Focal)

Library versions:

- GDAL: 3.0.0
- OpenJPEG: 2.3.1
- Proj: 8.2.1

# Build new image

1. Clone
```
cd /workdir
git clone https://github.com/rogerlew/f-esri/
```

2. Build

```bash
cd /workdir/f-esri
sudo docker image build --tag f_esri .
```

3. Add f_esri module to dist-packages as .pth

```bash
echo "/workdir/f-esri/" | sudo tee -a /usr/lib/python3/dist-packages/f_esri.pth
```

_wepppy310-env conda environment_
```bash
echo "/workdir/f-esri/" | sudo tee -a /workdir/miniconda3/envs/wepppy310-env/lib/python3.10/site-packages/f_esri.pth
```

4. Configure `www-data` user for docker

```bash
sudo usermod -aG docker www-data
sudo systemctl restart docker
```

```bash
sudo visudo
```

add this line:

```
www-data ALL=(ALL) NOPASSWD: /usr/bin/docker
```

# GDAL Grande: FileGDB Conversion Examples

This document provides usage and conversion examples for using GDAL to convert OGC GeoPackage files (`.gpkg`) to ESRI File Geodatabase (`.gdb`) format.

## Requirements

Before starting, ensure you have the `gdal-grande` Docker image built and ready to use. This image supports the ESRI FileGDB format.

### Check GDAL FileGDB Support

To ensure that the GDAL installation in the Docker image has FileGDB write support, run the following command:

```bash
docker run --rm f_esri ogrinfo --formats | grep -i "FileGDB"
```

Expected output:

```
  OpenFileGDB -vector- (rov): ESRI FileGDB
  FileGDB -vector- (rw+v): ESRI FileGDB
```

The `rw+v` indicates that FileGDB writing is supported.

## Basic GeoPackage to FileGDB Conversion

To convert an OGC GeoPackage (`.gpkg`) to FileGDB (`.gdb`), run the following command:

```bash
docker run --rm -v $(pwd):/data f_esri ogr2ogr -f "FileGDB" /data/output.gdb /data/input.gpkg
```

The f_esri python module provides subprocess wrapper to use docker image for conversion

```python
import f_esri

if f_esri.has_f_esri():
    f_esri.gpkg_to_gdb("/path/to/input.gpkg", "path/to/output.gdb")
```

the `gpkg_to_gdb` function will delete the output.gdb if it exists. it will also create a zip of the geodatabase folder


### Explanation:
- `$(pwd):/data`: Mounts the current directory into the Docker container's `/data` directory.
- `/data/input.gpkg`: The input GeoPackage file.
- `/data/output.gdb`: The output FileGDB directory.

After the conversion, `output.gdb` will be created in the current directory as a File Geodatabase.

### List Layers in the Output FileGDB

To verify the contents of the newly created FileGDB:

```bash
docker run --rm -v $(pwd):/data f_esri ogrinfo /data/output.gdb
```

This command lists the layers and metadata of the FileGDB.

## Sharing FileGDB

Since a `.gdb` is a directory containing multiple files, it is recommended to zip the entire `.gdb` folder for sharing:

### On Linux/MacOS:
```bash
zip -r output.gdb.zip output.gdb
```

### On Windows:
Right-click the `output.gdb` folder and select **Send to → Compressed (zipped) folder**.

The recipient can then unzip the folder and use it in GIS software like ArcGIS or QGIS.

## Additional Notes

- Ensure that the full `.gdb` directory is included when zipping or sharing the FileGDB, as missing files may result in an incomplete or corrupted geodatabase.
- If you're using FileGDB for sharing or long-term storage, consider its compatibility limitations compared to open formats like GeoPackage.

